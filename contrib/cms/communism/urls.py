from django.conf.urls import *

from libscampi.contrib.cms.communism.views import view_commune, primary_section
from libscampi.contrib.cms.newsengine.urls import published_archive_urls, story_urls

urlpatterns = patterns('libscampi.contrib.cms.communism.views',
    url(r'^s/', include(story_urls, 'story')), # story permanent links
    url(r'^p/', include(published_archive_urls, 'publish')), # publish archives under /p/<picker-keyname>/
    url(r'^(?P<keyname>[\w\.\-]+)/$', view_commune, name="view-section"),
    url(r'^$', primary_section, name="primary-section"),
)
