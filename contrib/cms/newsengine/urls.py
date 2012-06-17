from django.conf.urls import *
from django.views.decorators.cache import cache_page

from libscampi.contrib.cms.newsengine.views import picked_story_archive, picked_story_detail, picked_story_archive_day, picked_story_archive_month, picked_story_archive_year, related_story_detail, story_detail

urlpatterns = patterns('libscampi.contrib.cms.communism.views',
    url(r'^s/(?P<slug>[\w-]+)/$', story_detail, name="story-detail"),
    url(r'^(?P<picker>[\w-]+)/r/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\w-]+)/', related_story_detail, name="related-story-detail"),
    url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\w-]+)/$',  cache_page(picked_story_detail, 60 * 10), name="pubstory-detail"),
    url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', cache_page(picked_story_archive_day, 60 * 10), name="pubstory-archive-day"),
    url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', cache_page(picked_story_archive_month, 60 * 20), name="pubstory-archive-month"),
    url(r'^(?P<picker>[\w-]+)/(?P<year>\d{4})/$', cache_page(picked_story_archive_year, 60*25), name="pubstory-archive-year"),
    url(r'^(?P<picker>[\w-]+)/$', cache_page(picked_story_archive, 60*60), name="pubstory-archive"),
)