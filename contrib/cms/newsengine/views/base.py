from django.views.generic.dates import *

from libscampi.contrib.cms.views.base import Page
from libscampi.contrib.cms.conduit.views.mixins import PickerMixin

class PickedStoryIndex(ArchiveIndexView, PickerMixin, Page):
    pass

"""
class PickedStoryYearArchive(Page, PickerArchiveMixin, YearArchiveView):

class PickedStoryMonthArchive(Page, PickerArchiveMixin, MonthArchiveView):

class PickedStoryDayArchive(Page, PickerArchiveMixin, DayArchiveView):

class PickerStoryTodayArchive(Page, PickerArchiveMixin, TodayArchiveView):

class PickedStoryDetailArchive(Page, PickerArchiveMixin, DateDetailView):
"""