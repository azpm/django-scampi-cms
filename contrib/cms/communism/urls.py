from django.conf.urls import *

from libscampi.contrib.cms.communism.views import view_commune, primary_section
from libscampi.contrib.cms.newsengine.urls import urlpatterns as newsengine_archive_urls

urlpatterns = patterns('libscampi.contrib.cms.communism.views',
    url(r'^p/(?P<picker>[\w-]+)/', include(newsengine_archive_urls)),
    url(r'^(?P<keyname>[\w\.\-]+)/$', view_commune, name="view-section"),
    url(r'^$', primary_section, name="primary-section"),
)