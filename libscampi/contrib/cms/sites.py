from django.conf.urls import url, include
from libscampi.contrib.cms.communism.urls import urlpatterns as page_urls


class CMSSite(object):
    @property
    def urls(self):
        cms_urls = [
            url(r'', include(page_urls, namespace="cms")),
        ]

        return cms_urls


site = CMSSite()
