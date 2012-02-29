from django.conf.urls.defaults import *
from django.contrib.sites.models import Site
from libscampi.contrib.cms.communism.models import Realm

from libscampi.contrib.cms.communism.urls import urlpatterns as page_urls

class CMSSite(object):
    def urls(self):
        try:
            realm = Realm.objects.get(site=Site.objects.get_current())
        except (Realm.DoesNotExist, Site.DoesNotExist):
            realm = type("null_realm", (object, ), {'keyname': u"no-realm"})()
        
        cms_urls = patterns(None, 
            url(r'', include(page_urls)),
        )    
        return cms_urls, None, None
        return cms_urls, "cms", realm.keyname
    urls = property(urls)
        
site = CMSSite()