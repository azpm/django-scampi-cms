from django.views.generic import View, TemplateView
from django.core.exceptions import ImproperlyConfigured

from libscampi.contrib.cms.communism.views.mixins import CommuneMixin, ThemeMixin, CSSMixin, JScriptMixin

from .mixins import PageMixin

class Page(CommuneMixin, PageMixin, ThemeMixin, CSSMixin, JScriptMixin, TemplateView):
    pass

class PageNoView(CommuneMixin, PageMixin, ThemeMixin, CSSMixin, JScriptMixin):
    """
    Implements a CMS page that has no view
    e.g. you must provide an alternative View mixin
    """    
    pass