from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from libscampi.contrib.cms.newsengine.views.api import resources
from libscampi.contrib.cms.newsengine.views import *
from libscampi.contrib.cms.newsengine.feeds import PublishedStoryFeed

__all__ = ['published_archive_urls','story_urls','feeds']

published_archive_urls = patterns('',
    url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\w-]+)/$', pub_archive_detail, name="pubstory-detail"),
    url(r'^(?P<picker>[\w-]+)/$', pub_archive_index, name="pubstory-archive"),
)

story_urls = patterns('',
    url(r'^(?P<slug>[\w-]+)/$', story_detail, name="story-detail"),
    url(r'^$', story_list, name="story-list"),
)

feeds = patterns('',
    url(r'^rss/(?P<picker>[\w-]+)/$', PublishedStoryFeed(), name="pubstory-feed"),
)

api = format_suffix_patterns(patterns('',
    url(r'^story/$', resources.StoryList.as_view(), name="story-list"),
    url(r'^story/(?P<pk>\d+)/$', resources.StoryDetail.as_view(), name="story-detail"),
    url(r'^publish/$', resources.PublishList.as_view(), name="publish-list"),
    url(r'^publish/(?P<pk>\d+)/$', resources.PublishDetail.as_view(), name="publish-detail"),
), allowed=['json, api'])