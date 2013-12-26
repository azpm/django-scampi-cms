from django.conf.urls import url, patterns
from libscampi.contrib.cms.newsengine import views
from libscampi.contrib.cms.newsengine.feeds import PublishedStoryFeed

__all__ = ['published_archive_urls', 'story_urls', 'feeds']

published_archive_urls = patterns(
    '',
    url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\w-]+)/$', views.pub_archive_detail, name="pubstory-detail"),
    url(r'^(?P<picker>[\w-]+)/$', views.pub_archive_index, name="pubstory-archive"),
)

story_urls = patterns(
    '',
    url(r'^(?P<slug>[\w-]+)/$', views.story_detail, name="story-detail"),
    url(r'^$', views.story_list, name="story-list"),
)

feeds = patterns(
    '',
    url(r'^rss/(?P<picker>[\w-]+)/$', PublishedStoryFeed(), name="pubstory-feed"),
)