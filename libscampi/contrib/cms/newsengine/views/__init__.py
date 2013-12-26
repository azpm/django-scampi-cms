from libscampi.contrib.cms.newsengine.views.story import base as story
from libscampi.contrib.cms.newsengine.views.publish import base as publish

__all__ = [
    'pub_archive_index','pub_archive_year','pub_archive_month',
    'pub_archive_day','pub_archive_detail','story_list','story_detail'
]

# publish archives
pub_archive_index = publish.PublishArchiveIndex.as_view()
pub_archive_year = publish.PublishArchiveYear.as_view()
pub_archive_month = publish.PublishArchiveMonth.as_view()
pub_archive_day = publish.PublishArchiveDay.as_view()
pub_archive_detail = publish.PublishArchiveDetail.as_view()

# story perma-links
story_list = story.StoryList.as_view()
story_detail = story.StoryDetail.as_view()