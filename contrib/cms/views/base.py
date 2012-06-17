from django.views.generic import TemplateView

from libscampi.contrib.cms.communism.views.mixins import SectionMixin, ApplicationMixin, CommuneMixin, ThemeMixin, CSSMixin, JScriptMixin

from .mixins import PageMixin

class Page(SectionMixin, ApplicationMixin, ThemeMixin, CSSMixin, JScriptMixin, PageMixin, TemplateView):
    """
    Implements an un-managed page with a  templateview that integrates with the CMS without having a commune, e.g.
    if you are using a custom django application and want to integrate it with scampi cms
    """
    pass

class PageNoView(SectionMixin, ApplicationMixin, ThemeMixin, CSSMixin, JScriptMixin, PageMixin):
    """
    Implements an un-managed page that has no view, you must provide the proper response mixin
    """
    pass

class CMSPage(SectionMixin, CommuneMixin, ThemeMixin, CSSMixin, JScriptMixin, PageMixin, TemplateView):
    """
    Implements a canonical Commune based CMS Page
    """
    pass

class CMSPageNoView(SectionMixin, CommuneMixin, ThemeMixin, CSSMixin, JScriptMixin, PageMixin):
    """
    Implements a CMS page that has no view
    e.g. you must provide an alternative View mixin
    """    
    pass
    
