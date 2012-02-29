from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

from libscampi.contrib.cms.newsengine.views import story_archive, story_detail, story_archive_day, story_archive_month, story_archive_year

urlpatterns = patterns('libscampi.contrib.cms.communism.views',
    #no category limits 
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\w-]+)/$',  cache_page(story_detail, 60 * 10), name="published-story-detail"), 
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', cache_page(story_archive_day, 60 * 10), name="published-story-archive-day"), 
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', cache_page(story_archive_month, 60 * 20), name="published-story-archive-month"),
    url(r'^(?P<year>\d{4})/$', cache_page(story_archive_year, 60*25), name="published-story-archive-year"),
    #with cagetory limits
    url(r'^c/(?P<categories>[\w\.\-\+]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', cache_page(story_archive_day, 60 * 10), name="cat-limited-published-story-archive-day"),
    url(r'^c/(?P<categories>[\w\.\-\+]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', cache_page(story_archive_month, 60 * 20), name="cat-limited-published-story-archive-month"),
    url(r'^c/(?P<categories>[\w\.\-\+]+)/(?P<year>\d{4})/$', cache_page(story_archive_year, 60*25), name="cat-limited-published-story-archive-year"),
    url(r'^c/(?P<categories>[\w\.\-\+]+)/$', cache_page(story_archive, 60*60), name="cat-limited-published-story-archive"),
    #index
    url(r'^$', cache_page(story_archive, 60*60), name="published-story-archive"),    
)