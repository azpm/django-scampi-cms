from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
from libscampi.contrib.cms.renaissance.views import view_media

urlpatterns = patterns('libscampi.contrib.cms.renaissance.views',       
    url(r'^(?P<type>[\w/-]+)/(?P<slug>[\w/-]+)/$', cache_page(view_media, 60*5), name="renaissance-view-standalone"),
)
