import debug_toolbar

from django.conf import settings
from django.conf.urls import url, include
from libscampi.contrib.cms.communism.urls import urlpatterns as page_urls


class CMSSite(object):
    @property
    def urls(self):
        cms_urls = [
            url(r'', include(page_urls, namespace="cms")),
        ]

        if settings.DEBUG:
            cms_urls = [
                url(r'__debug__/', include(debug_toolbar.urls)),
            ] + cms_urls

        return cms_urls


site = CMSSite()
