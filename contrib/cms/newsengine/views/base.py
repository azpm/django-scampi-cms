from django.views.generic.dates import *

from libscampi.contrib.cms.views.base import Page, PageNoView
from libscampi.contrib.cms.conduit.views.mixins import PickerMixin

from .mixins import PublishStoryMixin

class NewsEngineArchivePage(PublishStoryMixin, PickerMixin, PageNoView):
    
    def get_queryset(self):
        
        f = self.picker.Archive
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