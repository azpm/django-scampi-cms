from django.views.generic.dates import *

from libscampi.contrib.cms.views.base import Page, PageNoView
from libscampi.contrib.cms.conduit.views.mixins import PickerMixin

from .mixins import PublishStoryMixin

class NewsEngineArchivePage(PublishStoryMixin, PickerMixin, PageNoView):
    
    def get_queryset(self):
        qs = self.model.objects.select_related().all()
        
        """
        this is a hardcoded "hack"
        
        the newsengine publish stories are displayed, by way of the CMS through
        dynamic pickers. Without having time to write a robust "archive" feature
        for dynamic pickers, we conclude that because contrib.CMS is not editable
        the Picking Filterset for Publish (published stories) is immutable and
        'start', 'end', 'end__isnull' are known keys of things we DON'T want to
        filter by for the archives.
        
        We do this because the archives themselves will exclude things that
        haven't been published yet, and will always show expired stories.
        """
        
        exclude_these = ('start', 'end', 'end__isnull')
        
        #loop over the inclusion filters and update the qs
        if self.picker.include_filters:
            if isinstance(self.picker.include_filters, list):
                for f in self.include_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) #this strips anything we dont want
                    qs = qs.filter(**f)
            else:
                qs = qs.filter(**f)
        
        if self.picker.exclude_filters:
            if isinstance(self.picker.include_filters, list):
                for f in self.exclude_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) #strips unneeded filters
                    qs = qs.exclude(**f)
            else:
                qs = qs.exclude(**f)
        
        
        assert False


class PickedStoryIndex(NewsEngineArchivePage, ArchiveIndexView):
    pass

"""
class PickedStoryYearArchive(Page, PickerArchiveMixin, YearArchiveView):

class PickedStoryMonthArchive(Page, PickerArchiveMixin, MonthArchiveView):

class PickedStoryDayArchive(Page, PickerArchiveMixin, DayArchiveView):

class PickerStoryTodayArchive(Page, PickerArchiveMixin, TodayArchiveView):

class PickedStoryDetailArchive(Page, PickerArchiveMixin, DateDetailView):
"""