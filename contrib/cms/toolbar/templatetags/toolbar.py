from django import template
from classytags.arguments import Argument, MultiValueArgument
from classytags.core import Options, Tag
from classytags.helpers import InclusionTag
from classytags.parser import Parser


register = template.Library()

class ScampiToolbar(InclusionTag):
    template = '__cms_toolbar.html'
    name = "scampi_toolbar"

    def render(self, context):
        request = context.get('request', None)
        if not request:
            return ''
        toolbar = getattr(request, 'toolbar', None)
        if not toolbar:
            return ''
        if not toolbar.show_toolbar:
            return ''
        return super(ScampiToolbar, self).render(context)

    def get_context(self, context):
        return context

register.tag(ScampiToolbar)