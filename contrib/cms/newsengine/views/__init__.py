from .base import PickedStoryIndex, \
    PickedStoryYearArchive, \
    PickedStoryMonthArchive, \
    PickedStoryDayArchive, \
    PickerStoryTodayArchive, \
    PickedStoryDetailArchive, \
    RelatedStoryDetailView, \
    StoryDetail

story_detail = StoryDetail.as_view()
related_story_detail = RelatedStoryDetailView.as_view()
picked_story_detail = PickedStoryDetailArchive.as_view()
picked_story_archive_day = PickedStoryDayArchive.as_view()
picked_story_archive_month = PickedStoryMonthArchive.as_view()
picked_story_archive_year = PickedStoryYearArchive.as_view()
picked_story_archive = PickedStoryIndex.as_view()