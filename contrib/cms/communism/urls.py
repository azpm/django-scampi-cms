from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

from libscampi.contrib.cms.communism.views import view_commune, primary_section
#from libscampi.contrib.cms.communism.views import story_detail, story_archive_day, story_archive_month, story_archive_year, story_archive, view_commune, primary_section

urlpatterns = patterns('libscampi.contrib.cms.communism.views',
    url(r'^(?P<keyname>[\w\.\-]+)/$', view_commune, name="view-commune"),
    url(r'^$', primary_section, name="primary-section"),
)

 """
    url(r'^(?P<keyname>[\w\.\-]+)/(?P<publishword>[\w/-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\w/-]+)/$', 
        cache_page(story_detail, 60*5), name="published-story-detail"),
    url(r'^(?P<keyname>[\w\.\-]+)/(?P<publishword>[\w/-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 
        cache_page(story_archive_day, 60*15), name="published-story-archive-day"),
    url(r'^(?P<keyname>[\w\.\-]+)/(?P<publishword>[\w/-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 
        cache_page(story_archive_month, 60*25), name="published-story-archive-month"),
    url(r'^(?P<keyname>[\w\.\-]+)/(?P<publishword>[\w/-]+)/(?P<year>\d{4})/$', 
        cache_page(story_archive_year, 60*60), name="published-story-archive-year"),
    url(r'^(?P<keyname>[\w\.\-]+)/(?P<publishword>[\w/-]+)/$', 
        cache_page(story_archive, 60*60), name="published-story-archive"),
    """ 
