from django.views.generic import View, TemplateView
from django.core.exceptions import ImproperlyConfigured

from libscampi.contrib.cms.communism.views.mixins import SectionMixin, CommuneMixin, ThemeMixin, CSSMixin, JScriptMixin

from .mixins import PageMixin

class Page(SectionMixin, CommuneMixin, ThemeMixin, CSSMixin, JScriptMixin, PageMixin, TemplateView):
    pass

class PageNoView(SectionMixin, CommuneMixin, ThemeMixin, CSSMixin, PageMixin, JScriptMixin):
    """
    Implements a CMS page that has no view
    e.g. you must provide an alternative View mixin
    """    
    pass
    
class UnManagedPage(SectionMixin, ThemeMixin, CSSMixin, JScriptMixin, PageMixin, TemplateView):
    pass