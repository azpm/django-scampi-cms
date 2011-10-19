from django.views.generic import View, TemplateView
from django.core.exceptions import ImproperlyConfigured

from .mixins import PageMixin, CommuneMixin, ThemeMixin, CSSMixin, JScriptMixin

class Page(CommuneMixin, PageMixin, ThemeMixin, CSSMixin, JScriptMixin, TemplateView):
    pass

