from django.conf.urls import url, include

from libscampi.contrib.cms import views
from libscampi.contrib.cms.newsengine.urls import published_archive_urls, story_urls, feeds

urlpatterns = [
    url(r'^f/', include(feeds, 'feeds')),  # rss feeds
    url(r'^s/', include(story_urls, 'story')),  # story permanent links
    url(r'^p/', include(published_archive_urls, 'publish')),  # publish archives under /p/<picker-keyname>/
    url(r'^(?P<keyname>[\w\-]+)/$', views.view_commune, name="view-section"),
    url(r'^$', views.primary_section, name="primary-section"),
]
