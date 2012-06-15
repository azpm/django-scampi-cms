import logging

from django import template
from django.template.loader import render_to_string
from django.db.models import Max
from django.core.cache import cache
from django.template.defaultfilters import slugify

logger = logging.getLogger('libscampi.contrib.cms.communism.templatetags')
register = template.Library()

class namedbox_node(template.Node):
    def __init__(self, namedbox):
        self.namedbox = template.Variable(namedbox)
    
    def render(self, context):
        #get the namedbox and see if the template is in the cache
        namedbox = self.namedbox.resolve(context)
        
        cached_tpl_key = "commune:namedbox:tpl:%d" % namedbox.template_id
        cached_tpl = cache.get(cached_tpl_key, None)
        
        #grab the template from the database and then cache it
        if not cached_tpl:
            logger.debug("cache miss on %s%s trying to get cached template" % (cache.key_prefix, cached_tpl_key))
            cached_tpl = namedbox.template.content
            cache.set(cached_tpl_key, cached_tpl)
        
        tpl = template.Template(cached_tpl, name = "communism.NamedBoxTemplate [%s]" % namedbox.template_id)
        request = context.get('request', None)
            
        if not request:
            return ''
        
        c = {
            'box': namedbox, 
            'cms_realm': context.get('cms_realm', None),
            'cms_section': context.get('cms_section', None),
            'cms_page': context.get('cms_page', None),
        }
        
        new_context = template.RequestContext(request, c, current_app = context.current_app)
        return tpl.render(new_context)

        
def render_namedbox(parser, token):
    """
    Renders a :model:`communism.NamedBox` according to it's :model:`communism.NamedBoxTemplate`
    
    {% render_namedbox box %}  Where box is a :model:`communism.NamedBox`
    
    Provides the following context to the :model:`communism.NamedBoxTemplate`:
    
    - box: the namedbox being rendered :model:`communism.NamedBox`, use as {{ box.field_name }}
    - request: django request, use as {{ request.field_name }} comes from RequestContext
    - cms_section: :model:`communism.Section`, use as {{ cms_section.field_name }}
    - cms_realm: :model:`communism.Realm`, use as {{ cms_realm.field_name }}
    """
    
    try:
        tag_name, namedbox = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires 1 argument, a namedbox" % token.contents.split()[0]
    
    return namedbox_node(namedbox)

register.tag('render_namedbox', render_namedbox)