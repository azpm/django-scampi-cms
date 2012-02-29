from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

from libscampi.contrib.cms.communism.views import view_commune, primary_section
from libscampi.contrib.cms.newsengine.urls import urlpatterns as newsengine_archive_urls

urlpatterns = patterns('libscampi.contrib.cms.communism.views',
    url(r'^(?P<keyname>[\w\.\-]+)/(?P<picker>[\w-]+)/', include(newsengine_archive_urls, "cms", "newsengine")),
    url(r'^(?P<keyname>[\w\.\-]+)/$', view_commune, name="view-commune"),
    url(r'^$', primary_section, name="primary-section"),
)