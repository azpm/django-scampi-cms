from django.views.generic import View, TemplateView
from django.core.exceptions import ImproperlyConfigured

from .mixins import PageMixin, CommuneMixin, ThemeMixin, CSSMixin, JScriptMixin
from libscampi.contrib.cms.conduit.views.mixins import PickerGraph

class Page(CommuneMixin, PageMixin, ThemeMixin, CSSMixin, JScriptMixin, PickerGraph, TemplateView):
    pass

