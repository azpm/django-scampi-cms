from django import template
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.markup.templatetags.markup import markdown

from libscampi.contrib.cms.conduit.models import *

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
            tpl = template.Template(picker.template.content)
            c = template.Context(context.render_context)
            perms = context.get('perms', None)
            
            if 'picker' not in c:
                c.update({'picker': picker})
            if 'request' not in c:
                c.update({'request': context['request']})
            if 'section' not in c:
                c.update({'section': context.get('CMS_SECTION', None)})
            if 'perms' not in c and perms:
                c.update({'perms': perms})
            if 'MASTER_MEDIA_URL' not in c:
                c.update({'MASTER_MEDIA_URL': context.get('MASTER_MEDIA_URL', None)})
            if 'MEDIA_URL' not in c:
                c.update({'MEDIA_URL': context.get('MEDIA_URL', None)})
            if 'THEME_URL' not in c:
                c.update({'THEME_URL': context.get('THEME_URL', None)})
                
            return tpl.render(c)
        elif type(picker) is StaticPicker:
            return markdown(picker.content)
                    
        return u""
    
@register.tag('render_picker')
def render_picker(parser, token):
    try:
        tag, picker = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("'%s' requires an argument: a picker" % token.contents.split()[0])
        
    return picker_node(picker)


class unpacked_picker(template.Node):
    def __init__(self, nb):
        self.named_box = template.Variable(nb)
    
    def render(self, context):
        try:
            named_box = self.named_box.resolve(context)
        except template.VariableDoesNotExist:
            return u"" #handed tag something that doesn't exist
        
        graph = context.get('pickers', None)
        if not graph:
            return u"" #case where there isn't a picker graph
            
        try:
            picker = graph[named_box]
        except (ValueError, KeyError):
            return u"" #case where named box doesn't have a picker
            
            
        if type(picker) is DynamicPicker:
            tpl = template.Template(picker.template.content)
            c = template.Context(context.render_context)
            perms = context.get('perms', None)
            
            if 'picker' not in c:
                c.update({'picker': picker})
            if 'request' not in c:
                c.update({'request': context['request']})
            if 'section' not in c:
                c.update({'section': context.get('CMS_SECTION', None)})
            if 'perms' not in c and perms:
                c.update({'perms': perms})
            if 'MASTER_MEDIA_URL' not in c:
                c.update({'MASTER_MEDIA_URL': context.get('MASTER_MEDIA_URL', None)})
            if 'MEDIA_URL' not in c:
                c.update({'MEDIA_URL': context.get('MEDIA_URL', None)})
            if 'THEME_URL' not in c:
                c.update({'THEME_URL': context.get('THEME_URL', None)})
            
            return tpl.render(c)
        elif type(picker) is StaticPicker:
            return markdown(picker.content)


@register.tag('unpack_picker')
def unpack_picker(parser, token):
    try:
        tag, named_box = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("'%s' requires an argument: a picker" % token.contents.split()[0])
    
    return unpacked_picker(named_box)