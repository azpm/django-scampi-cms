import logging

from django import template
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.markup.templatetags.markup import markdown

from libscampi.contrib.cms.conduit.models import *

logger = logging.getLogger('libscampi.contrib.cms.conduit.templatetags')
register = template.Library()

class picker_node(template.Node):
    def __init__(self, picker):
        self.picker = template.Variable(picker)
    
    def render(self, context):
        try:
            picker = self.picker.resolve(context)
        except template.VariableDoesNotExist:
            return u""
        
        if type(picker) is DynamicPicker:            
            request = context.get('request', None)
            
            if not request:
                return ''
            
            cached_tpl_key = "dynamicpicker-tpl-%d" % picker.template_id
            cached_tpl = cache.get(cached_tpl_key, None)
            
            if not cached_tpl:
                logger.debug("cache miss on %s trying to get cached template" % cached_tpl)
                cached_tpl = picker.template.content
                cache.set(cached_tpl_key, cached_tpl)
            
            tpl = template.Template(cached_tpl, name="conduit.PickerTemplate [%s]" % picker.template_id)

            
            c = {
                'picker': picker, 
                'cms_realm': context.get('cms_realm', None),
                'cms_section': context.get('cms_section', None),
                'cms_page': context.get('cms_page', None),
            }
            
            new_context = template.RequestContext(request, c, current_app = context.current_app)
            return tpl.render(new_context)
        
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
        raise template.TemplateSyntaxError("'%s' requires an argument: a picker" % token.contents.split()[0])
        
    return picker_node(picker)