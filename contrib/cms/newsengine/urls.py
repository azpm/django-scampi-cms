from django.conf.urls import url, patterns
from libscampi.contrib.cms.newsengine.views import *
from libscampi.contrib.cms.newsengine.feeds import PublishedStoryFeed

__all__ = ['published_archive_urls','story_urls','feeds']

published_archive_urls = patterns('',
    url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\w-]+)/$', pub_archive_detail, name="pubstory-detail"),
    #url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', pub_archive_day, name="pubstory-archive-day"),
    #url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', pub_archive_month, name="pubstory-archive-month"),
    #url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/$', pub_archive_year, name="pubstory-archive-year"),
    url(r'^(?P<picker>[\w-]+)/$', pub_archive_index, name="pubstory-archive"),
)

story_urls = patterns('',
    url(r'^(?P<slug>[\w-]+)/$', story_detail, name="story-detail"),
    url(r'^$', story_list, name="story-list"),
)

feeds = patterns('',
    url(r'^rss/(?P<picker>[\w-]+)/$', PublishedStoryFeed(), name="pubstory-feed"),
)