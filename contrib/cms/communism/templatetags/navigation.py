import re

from django import template
from django.utils.translation import ugettext_lazy as _

from libscampi.contrib.cms.communism.models import *

register = template.Library()

class realms_node(template.Node):
    def __init__(self, varname):
        self.varname = varname
    
    def render(self, context):
        realms = Realm.objects.select_related().filter(active = True)
        context[self.varname] = realms
        
        return ''
        
def realms(parser, token):
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
        
    return realms_node(varname)


class sections_node(template.Node):
    def __init__(self, varname):
        self.varname = varname
    
    def render(self, context):
        current_realm = context['CMS_REALM']
        
        try:
            sections = current_realm.section_set.select_related().filter(active = True, generates_navigation = True, extends__isnull=True)
        except:
            sections = None
            
        context[self.varname] = sections
        
        return ''
        
def get_navigable_sections(parser, token):
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
        varname = "sections"
        
    return sections_node(varname)

register.tag('get_all_realms', realms)
register.tag('get_navigable_sections', get_navigable_sections)