from .base import PickedStoryIndex, \
    PickedStoryYearArchive, \
    PickedStoryMonthArchive, \
    PickedStoryDayArchive, \
    PickerStoryTodayArchive, \
    PickedStoryDetailArchive, \
    RelatedStoryDetailView

related_story_detail = RelatedStoryDetailView.as_view()
story_detail = PickedStoryDetailArchive.as_view()
story_archive_day = PickedStoryDayArchive.as_view()
story_archive_month = PickedStoryMonthArchive.as_view()
story_archive_year = PickedStoryYearArchive.as_view()
story_archive = PickedStoryIndex.as_view()