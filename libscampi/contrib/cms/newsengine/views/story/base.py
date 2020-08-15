import logging
from datetime import datetime

from django.views.generic import DetailView, ListView
from django.db.models import Q

from libscampi.contrib.cms.views.base import PageNoView
from libscampi.contrib.cms.newsengine.models import StoryCategory
from libscampi.contrib.cms.newsengine.views.helpers import story_javascripts, story_stylesheets
from libscampi.contrib.cms.newsengine.views.story.mixins import StoryMixin

logger = logging.getLogger('libscampi.contrib.cms.newsengine.views.story')


class StoryPage(StoryMixin, PageNoView):
    limits = None
    available_categories = None
    base_categories = None
    restrict = True

    def get_cached_css_key(self):
        return "story:list:css:{0:d}".format(self.realm.id)

    def get_cached_js_key(self):
        return "story:list:js:{0:d}".format(self.realm.id)

    def dispatch(self, request, *args, **kwargs):
        # add section to the graph by way of the picker
        kwargs.update(dict(keyname="__un_managed"))

        if request.user.has_perm('newsengine.can_preview_story'):
            self.restrict = False

        # category filtering specified in url
        if 'c' in request.GET:
            limits = request.GET.get('c', '').split(' ')

            filters = [Q(keyname=value) for value in limits]
            query = filters.pop()
            # Or the Q object with the ones remaining in the list
            for filter_ in filters:
                query |= filter_

            self.limits = StoryCategory.objects.filter(Q(browsable=True) & query)

        # finally return the parent get method
        return super(StoryPage, self).request(request, *args, **kwargs)

    def get_queryset(self):
        # first: all stories that don't have an excluded category
        excluded_stories = self.model.objects.filter(categories__excluded=True).values_list('id', flat=True)
        qs = self.model.objects.exclude(pk__in=excluded_stories).distinct()

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
            filters = [Q(categories__pk=value[0]) for value in self.limits.values_list('id')]
            for filter_ in filters:
                qs = qs.filter(filter_)
            self.available_categories = categories.exclude(pk__in=list(self.limits.values_list('id', flat=True)))
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

        # give the template the current picker
        context.update({
            'categories': self.available_categories,
            'limits': self.limits,
            'get_args': get_args,
            'base_categories': self.base_categories,
        })

        return context

    @property
    def base_template_path_arguments(self):
        theme = self.get_theme()
        return (
            "{0:>s}/newsengine/story".format(theme.keyname),
            self.realm.keyname,
        )


class StoryList(StoryPage, ListView):
    def get_page_title(self):
        return "Stories"

    def get_template_names(self):
        theme, realm = self.base_template_path_arguments
        return (
            "{0:>s}/{1:>s}/index.html".format(theme, realm),
            "{0:>s}/index.html".format(theme)
        )


class StoryDetail(StoryPage, DetailView):
    def get_page_title(self):
        return self.object.article.headline

    def get_template_names(self):
        theme, realm = self.base_template_path_arguments
        return (
            "{0:>s}/{1:>s}/{2:>s}.html".format(theme, realm, self.object.slug),
            "{0:>s}/{1:>s}.html".format(theme, self.object.slug),
            "{0:>s}/{1:>s}/detail.html".format(theme, realm),
            "{0:>s}/detail.html".format(theme),
        )

    def get_javascripts(self):
        story = self.object
        theme = self.get_theme()

        return story_javascripts(story, theme, self.refresh_caches)

    def get_stylesheets(self):
        story = self.object
        theme = self.get_theme()

        return story_stylesheets(story, theme, self.refresh_caches)
