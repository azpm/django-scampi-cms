import logging

from operator import and_
from django.views.generic.dates import *
from django.db.models import Q

from libscampi.contrib.cms.views.base import CMSPageNoView
from libscampi.contrib.cms.conduit.views.mixins import PickerMixin
from libscampi.contrib.cms.newsengine.models import StoryCategory
from libscampi.contrib.cms.newsengine.views.helpers import story_javascripts, story_stylesheets
from libscampi.contrib.cms.newsengine.views.publish.mixins import PublishMixin

logger = logging.getLogger('libscampi.contrib.cms.newsengine.views.publish')

class PublishArchivePage(PublishMixin, PickerMixin, CMSPageNoView):
    """
    Base page for newsengine archives

    provides the picker-pruned initial queryset
    """

    limits = None
    available_categories = None

    def get(self, request, *args, **kwargs):
        #keyname specified in url
        if 'c' in request.GET:
            limits = request.GET.get('c','').split(' ')

            filters = [Q(keyname=value) for value in limits]
            query = filters.pop()
            # Or the Q object with the ones remaining in the list
            for filter in filters:
                query |= filter

            self.limits = StoryCategory.objects.filter(Q(browsable=True) & query)

        #finally return the parent get method
        return super(PublishArchivePage, self).get(request, *args, **kwargs)

    def get_queryset(self):
        """
        this is a hardcoded queryset for :model:`newsengine.Publish`

        :model:`newsengine.Publish` are displayed, by way of the CMS through
        dynamic pickers. Without having time to write a robust "archive" feature
        for dynamic pickers, we conclude that because contrib.CMS is not editable
        the Picking Filter Set for :model:`newsengine.Publish` is immutable and
        'start', 'end', 'end__isnull' are known keys of things we DON'T want to
        filter by for the archives.

        We do this because the archives themselves will exclude things that
        haven't been published yet, and will always show expired stories.
        """
        qs = self.model.objects.distinct()
        exclude_these = ('start', 'end', 'end__isnull')

        #loop over the inclusion filters and update the qs
        if self.picker.include_filters:
            if isinstance(self.picker.include_filters, list):
                for f in self.picker.include_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) # this strips anything we don't want
                    qs = qs.filter(**f)
            else:
                logger.critical(
                    "invalid picker: cannot build archives from picker {0:>s} [id: {1:d}]".format(self.picker.name,
                        self.picker.id))


        if self.picker.exclude_filters:
            if isinstance(self.picker.include_filters, list):
                for f in self.picker.exclude_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) #strips unneeded filters
                    qs = qs.exclude(**f)
            else:
                logger.critical(
                    "invalid picker: cannot build archives from picker {0:>s} [id: {1:d}]".format(self.picker.name,
                        self.picker.id))

        categories = StoryCategory.genera.for_cloud(qs).exclude(pk__in=list(self.base_categories.values_list('id', flat=True)))

        if self.limits:
            filters = [Q(story__categories__pk=value[0]) for value in self.limits.values_list('id')]
            for filter in filters:
                qs = qs.filter(filter)
            self.available_categories = categories.exclude(pk__in=list(self.limits.values_list('id', flat=True)))
        else:
            self.available_categories = categories

        return qs

    def get_context_data(self, *args, **kwargs):
        # get the existing context
        context = super(PublishArchivePage, self).get_context_data(*args, **kwargs)

        if self.limits:
            get_args = u"c=%s" % "+".join([t.keyname for t in self.limits])
        else:
            get_args = None

        # give the template the current picker
        context.update({'categories': self.available_categories, 'limits': self.limits, 'get_args': get_args})
        return context

    def get_page_title(self):
        return "more %s" % self.picker.name

class PublishArchiveIndex(PublishArchivePage, ArchiveIndexView):
    """
    Archive index view for :model:`newsengine.Publish`, populated by a :model:`conduit.DynamicPicker`
    """
    def get_page_title(self):
        return "%s, Archive - %s" % (self.picker.name, self.picker.commune.name)
    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/index.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/index.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/index.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/index.html".format(self.commune.theme.keyname),
            )

        return tpl_list

class PublishArchiveYear(PublishArchivePage, YearArchiveView):
    """
    Archive Year view for :model:`newsengine.Publish`, populated by a :model:`conduit.DynamicPicker`
    """
    make_object_list = True

    def get_page_title(self):
        return "{0:>s}, Archive {1:>s} - {2:>s}".format(self.picker.name, self.get_year(), self.picker.commune.name)

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/year.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/year.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/year.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/year.html".format(self.commune.theme.keyname),
            )

        return tpl_list

class PublishArchiveMonth(PublishArchivePage, MonthArchiveView):
    """
    Archive Month view for :model:`newsengine.Publish`, populated by a :model:`conduit.DynamicPicker`
    """
    def get_page_title(self):
        return "{0:>s}, Archive {1:>s}/{2:>s} - {3:>s}".format(self.picker.name, self.get_month(), self.get_year(), self.picker.commune.name)

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/month.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/month.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/month.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/month.html".format(self.commune.theme.keyname),
            )

        return tpl_list

class PublishArchiveDay(PublishArchivePage, DayArchiveView):
    """
    Archive Day view for :model:`newsengine.Publish`, populated by a :model:`conduit.DynamicPicker`
    """
    def get_page_title(self):
        return "{0:>s}, Archive {1:>s}/{2:>s}/{3:>s} - {4:>s}".format(self.picker.name, self.get_day(), self.get_month(), self.get_year(), self.picker.commune.name)

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/day.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/day.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/day.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/day.html".format(self.commune.theme.keyname),
            )

        return tpl_list

class PublishArchiveDetail(PublishArchivePage, DateDetailView):
    """
    Archive Detail view for :model:`newsengine.Publish`, populated by a :model:`conduit.DynamicPicker`
    """
    def get_page_title(self):
        return "%s" % self.object.story.article.headline

    def get_javascripts(self):
        story = self.object.story
        theme = self.get_theme()

        return story_javascripts(story, theme, self.refresh_caches)

    def get_stylesheets(self):
        story = self.object.story
        theme = self.get_theme()

        return story_stylesheets(story, theme, self.refresh_caches)

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/{4:>s}.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname, self.object.slug),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/detail.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/detail.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/detail.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/detail.html".format(self.commune.theme.keyname),
            )

        return tpl_list
