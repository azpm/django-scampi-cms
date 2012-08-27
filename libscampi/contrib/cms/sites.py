from django.conf.urls import *
from libscampi.contrib.cms.communism.urls import urlpatterns as page_urls

class CMSSite(object):
    def urls(self):
        cms_urls = patterns(None, 
            url(r'', include(page_urls, namespace="cms")),
        )    
        
        return cms_urls
        
    urls = property(urls)
        
site = CMSSite()
