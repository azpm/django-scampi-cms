import re

from django import template
from django.utils.translation import ugettext_lazy as _

from libscampi.contrib.cms.communism.models import *

register = template.Library()

class RealmsNode(template.Node):
    def __init__(self, varname):
        self.varname = varname
    
    def render(self, context):
        realms = Realm.objects.select_related().filter(active = True).order_by('display_order')
        context[self.varname] = realms
        
        return ''

@register.tag
def get_realms(parser, token):
    """
    Puts a list of active Realms into current context
    
    {% get_realms as realms %}
    
    as Argument specifies name in context for list
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    try:
        varname = m.groups()[0]
    except:
        varname = "realms"
        
    return RealmsNode(varname)
    
class SectionsNode(template.Node):
    def __init__(self, pointer, varname):
        self.pointer = template.Variable(pointer)
        self.varname = varname
        
    def render(self, context):
        pointer = self.pointer.resolve(context)
        
        if type(pointer) == Realm:
            sections = pointer.section_set.select_related().filter(active = True, generates_navigation = True, extends__isnull=True)
        elif type(pointer) == Section:
            sections = Section.objects.select_related().filter(active = True, generates_navigation = True, extends = pointer)
        elif type(pointer) == Commune:
            sections = Section.objects.select_related().filter(active = True, generates_navigation = True, extends = pointer.section)
        else:
            sections = Section.objects.none()
        
        context[self.varname] = sections
            
        return ''
    
@register.tag
def get_sections(parser, token):
    """
    Puts a list of active "navigation generating" sections into current context
    
    {% get_sections pointer as context_varname %}
    
    pointer must be of type :model:`communism.Realm`, :model:`communism.Commune`, :model:`communism:Section`
    context_varname is string for the name in context to set the list
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    
    m = re.search(r'(\w+) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    try:
        varname = m.groups()[1]
        pointer = m.groups()[0]
    except:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
        
    return SectionsNode(pointer, varname)