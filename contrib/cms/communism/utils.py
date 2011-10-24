from django.core.cache import cache
from django.template.defaultfilters import slugify

"""
Theme Helpers and Utility functions
"""

# put theme stylesheets in the right spot
def theme_style_decorator(cls, f):
    return "%s/css/%s" % (cls.theme.keyname, f)
# put theme javascripts in the right spot    
def theme_script_decorator(cls, f):
    return "%s/js/%s" % (cls.theme.keyname, f)
    
def theme_banner_decorator(cls, f):
    return "%s/img/banner/%s" % (cls.keyname, f)
    
"""
this is not as cool looking though
"""
class external_file_funtime(object):
    def __init__(self, url):
        self.url = url

def overrive_js_file_url(sender, instance, **kwargs):
    if instance.external and not instance.file:
        instance.file = external_file_funtime(instance.external)
        
"""
Commune Helpers and Utility Functions
"""
def section_path_up(cls, glue):
    elements = cls[:]
    if elements[0].extends is not None:
        return section_path_up([elements[0].extends]+elements, glue)
        
    assert False
    return glue.join([z.keyname for z in elements])
    

#updates the cache whenever you save a namedboxtemplate
def cache_namedbox_template(sender, instance, **kwargs):
    cache_key = "nb-template-%s" % slugify(instance.name)
    tpl = instance.content
    cache.set(cache_key, tpl)