from django import template
from classytags.helpers import InclusionTag


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
