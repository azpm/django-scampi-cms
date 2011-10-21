from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

from libscampi.contrib.cms.newsengine.views import story_archive, story_detail, story_archive_day, story_archive_month, story_archive_year

urlpatterns = patterns('libscampi.contrib.cms.communism.views',
    url(r'^$', story_archive, name="published-story-archive"),
    url(r'^(?P<year>\d{4})/$', story_archive_year, name="published-story-archive-year"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', story_archive_month, name="published-story-archive-month"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', story_archive_day, name="published-story-archive-day"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\w-]+)/$',  story_detail, name="published-story-detail"),
)