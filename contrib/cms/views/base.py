from django.views.generic import View, TemplateView
from django.core.exceptions import ImproperlyConfigured

from .mixins import PageMixin, CommuneMixin, ThemeMixin, CSSMixin, JScriptMixin

class Page(CommuneMixin, PageMixin, ThemeMixin, CSSMixin, JScriptMixin, TemplateView):
    pass

class PageNoView(CommuneMixin, PageMixin, ThemeMixin, CSSMixin, JScriptMixin):
    """
    Implements a CMS page that has no view
    e.g. you must provide an alternative View mixin
    """    
    pass