from libscampi.contrib.cms.newsengine.views.story.base import StoryList, StoryDetail
from libscampi.contrib.cms.newsengine.views.publish.base import PublishArchiveIndex, PublishArchiveYear, \
    PublishArchiveMonth, PublishArchiveDay, PublishArchiveDetail

__all__ = [
    'pub_archive_index', 'pub_archive_year', 'pub_archive_month',
    'pub_archive_day', 'pub_archive_detail', 'story_list', 'story_detail'
]

# publish archives
pub_archive_index = PublishArchiveIndex.as_view()
pub_archive_year = PublishArchiveYear.as_view()
pub_archive_month = PublishArchiveMonth.as_view()
pub_archive_day = PublishArchiveDay.as_view()
pub_archive_detail = PublishArchiveDetail.as_view()

# story perma-links
story_list = StoryList.as_view()
story_detail = StoryDetail.as_view()
