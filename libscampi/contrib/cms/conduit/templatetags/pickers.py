import logging
from django import template
from django.core.cache import cache
from markdown import markdown
from libscampi.contrib.cms.conduit.models import *

logger = logging.getLogger('libscampi.contrib.cms.conduit.templatetags')
register = template.Library()

# TO DO convert to classy tag


class PickerNode(template.Node):
    def __init__(self, picker):
        self.picker = template.Variable(picker)

    def render(self, context):
        try:
            picker = self.picker.resolve(context)
        except template.VariableDoesNotExist:
            return u""

        if type(picker) is DynamicPicker and picker.active:
            request = context.get('request', None)

            if not request:
                return ''

            cached_tpl_key = "conduit:dp:tpl:{0:d}".format(picker.template_id)
            cached_tpl = cache.get(cached_tpl_key, None)

            if not cached_tpl:
                logger.debug("cache miss on {0:>s} trying to get cached template".format(cached_tpl_key))
                cached_tpl = picker.template.content
                cache.set(cached_tpl_key, cached_tpl)

            tpl = template.Template(cached_tpl, name="conduit.PickerTemplate [{0:d}]".format(picker.template_id))

            cache_control = request.META.get('HTTP_CACHE_CONTROL', None)
            if cache_control and cache_control == "max-age=0":
                cache_key = "conduit:dp:ids:{0:d}".format(picker.id)
                logger.debug("deleting picker cache for {0:>s}".format(cache_key))
                cache.delete(cache_key)

            c = {
                'picker': picker,
                'cms_realm': context.get('cms_realm', None),
                'cms_section': context.get('cms_section', None),
                'cms_page': context.get('cms_page', None),
            }

            new_context = template.RequestContext(request, c, current_app=context.current_app)

            try:
                rendered = tpl.render(new_context)
            except Exception, e:
                logger.error("could not render picker {0:>s}, got: {1:>s}".format(picker.name, e))
            else:
                return rendered

        elif type(picker) is StaticPicker:
            return markdown(picker.content)

        return u""

@register.tag('render_picker')
def render_picker(parser, token):
    """
    Renders a Picker
    
    {% render_picker picker_variable %}
    
    Most often used as:
    
    {% render_picker box.picker %}
    
    Will correctly determine if dynamic or static content needs to be rendered.
    
    Dynamic Pickers
    ===============
    
    Pickers will be rendered according to the template given in :model:`conduit.PickerTemplate`

    render_picker provides the following context to :model:`conduit.PickerTemplate`
    
    - picker: the :model:`conduit.DynamicPicker` being rendered
    - cms_realm: the current realm :model:`communism.Realm`
    - cms_section: the current section :model:`communism.Section`
    - page: the current Page instance
    - request: from RequestContext 
    - perms: from RequestContext
    
    Static Pickers
    ==============
    
    Content will be rendered as markdown
    """

    try:
        tag, picker = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("'{0:>s}' requires an argument: a picker".format(token.contents.split()[0]))

    return PickerNode(picker)
