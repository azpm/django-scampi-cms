from django import template
from django.template.loader import render_to_string
from django.db.models import Max
from django.core.cache import cache
from django.template.defaultfilters import slugify

register = template.Library()

class namedbox_node(template.Node):
    def __init__(self, namedbox):
        self.namedbox = template.Variable(namedbox)
    
    def render(self, context):
        #get the namedbox and see if the template is in the cache
        namedbox = self.namedbox.resolve(context)
        
        cached_tpl_key = "nb-template-%s" % slugify(namedbox.template.name)
        cached_tpl = cache.get(cached_tpl_key, None)
        
        #grab the template from the database and then cache it
        if not cached_tpl:
            cached_tpl = namedbox.template.content
            cache.set(cached_tpl_key, cached_tpl)
        
        tpl = template.Template(cached_tpl)
        c = template.Context(context.render_context)
        
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
        
        c.update({'box': namedbox})
        
        return tpl.render(c)
        
        
        #return render_to_string(tpl, {'box': namedbox}, context)
        
def render_namedbox(parser, token):
    try:
        tag_name, namedbox = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires 1 argument, a namedbox" % token.contents.split()[0]
    
    return namedbox_node(namedbox)

register.tag('render_namedbox', render_namedbox)