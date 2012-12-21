import logging
from datetime import datetime
from operator import and_

from django.views.generic import DetailView, ListView
from django.db.models import Q, Count
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.contrib.sites.models import Site

from libscampi.contrib.cms.views.base import PageNoView

from libscampi.contrib.cms.newsengine.models import StoryCategory
from libscampi.contrib.cms.newsengine.views.helpers import story_javascripts, story_stylesheets
from libscampi.contrib.cms.newsengine.views.story.mixins import StoryMixin

logger = logging.getLogger('libscampi.contrib.cms.newsengine.views.story')

class StoryPage(StoryMixin, PageNoView):
    theme = None
    limits = None
    available_categories = None
    base_categories = None
    restrict = True

    def get(self, request, *args, **kwargs):
        try:
            realm = Site.objects.get_current().realm
        except (AttributeError, ObjectDoesNotExist):
            raise Http404("SCAMPI Improperly Configured, no Realm available.")
        else:
            self.theme = realm.theme

        if request.user.has_perm('newsengine.can_preview_story'):
            self.restrict = False

        self.cached_css_key = "story:list:css:{0:d}".format(realm.id)
        self.cached_js_key = "story:list:js:{0:d}".format(realm.id)

        #category filtering specified in url
        if 'c' in request.GET:
            limits = request.GET.get('c','').split(' ')

            filters = [Q(keyname=value) for value in limits]
            query = filters.pop()
            # Or the Q object with the ones remaining in the list
            for filter in filters:
                query |= filter

            self.limits = StoryCategory.objects.filter(Q(browsable=True) & query)

        #add section to the graph by way of the picker
        kwargs.update(dict(keyname="__un_managed"))

        #finally return the parent get method
        return super(StoryPage, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model.objects.exclude(categories__excluded=True).distinct()

        # limit to stories that are published, before right now, to the current site, or no specific site
        now = datetime.now()

        if self.restrict:
            qs = qs.filter(
                Q(publish__site__id=self.realm.site_id) | Q(publish__site__isnull=True),
                publish__published=True,
                publish__start__lte=now,
            )

        categories = StoryCategory.genera.for_cloud(qs)

        if self.limits:
            limit_ids = list(self.limits.values_list('id', flat=True))
            query = reduce(and_, [Q(categories__pk=t) for t in limit_ids])
            qs = qs.filter(query)

            self.available_categories = categories.exclude(reduce(and_, [Q(pk=t) for t in limit_ids]))
        else:
            self.available_categories = categories

        self.base_categories = StoryCategory.objects.none()

        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(StoryPage, self).get_context_data(*args, **kwargs)

        if self.limits:
            get_args = u"c=%s" % "+".join([t.keyname for t in self.limits])
        else:
            get_args = None

        #give the template the current picker
        context.update({
            'categories': self.available_categories,
            'limits': self.limits,
            'get_args': get_args,
            'base_categories': self.base_categories,
        })

        return context


    def get_theme(self):
        return self.theme

class StoryList(StoryPage, ListView):
    def get_page_title(self):
        return "Stories"

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/story/{1:>s}/index.html".format(self.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/story/index.html".format(self.theme.keyname)
        )

        return tpl_list

class StoryDetail(StoryPage, DetailView):
    def get_page_title(self):
        return self.object.article.headline

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/story/{1:>s}/{2:>s}.html".format(self.theme.keyname, self.realm.keyname, self.object.slug),
            "{0:>s}/newsengine/story/{1:>s}.html".format(self.theme.keyname, self.object.slug),
            "{0:>s}/newsengine/story/{1:>s}/detail.html".format(self.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/story/detail.html".format(self.theme.keyname),
        )

        return tpl_list

    def get_javascripts(self):
        story = self.object
        theme = self.get_theme()

        return story_javascripts(story, theme, self.refresh_caches)

    def get_stylesheets(self):
        story = self.object
        theme = self.get_theme()

        return story_stylesheets(story, theme, self.refresh_caches)