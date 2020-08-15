from django.views.generic import TemplateView

from libscampi.contrib.cms.communism.views import mixins


class Page(mixins.ApplicationMixin, TemplateView):
    """
    Implements an un-managed page with a TemplateView that integrates with the CMS without having a commune, e.g.
    if you are using a custom django application and want to integrate it with scampi cms
    """
    pass


class PageNoView(mixins.ApplicationMixin):
    """
    Implements an un-managed page that has no GET/POST/etc handlers, you must provide the proper response mixin
    """
    pass


class CMSPage(mixins.CommuneMixin, TemplateView):
    """
    Fully manage paged

    Includes the following mixins

    1. libscampi.contrib.cms.communism.views.mixins.CacheMixin
    2. libscampi.contrib.cms.communism.views.mixins.PageMixin
    3. libscampi.contrib.cms.communism.views.mixins.SectionMixin
    4. libscampi.contrib.cms.communism.views.mixins.CommuneMixin

    and inherits from TemplateView to provide template rendering for a GET request
    """
    pass


class CMSPageNoView(mixins.CommuneMixin):
    """
    Implements a CMS page that has no view
    e.g. you must provide an alternative View mixin
    """
    pass
