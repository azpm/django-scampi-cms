from django.conf.urls import patterns, url, include


class CMSSite(object):
    @property
    def urls(self):
        cms_urls = patterns(None, url(r'', include('libscampi.contrib.cms.communism.urls', namespace="cms")), )
        
        return cms_urls
        
site = CMSSite()
