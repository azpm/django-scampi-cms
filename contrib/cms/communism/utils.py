import logging

from django.core.cache import cache
from django.template.defaultfilters import slugify
from libscampi.core.files.storage import OverwriteStorage
from libscampi.contrib.cms.communism.storage import URLStorage

logger = logging.getLogger('libscampi.contrib.cms.communism.utils')

# theme helpers

# put theme stylesheets in the right spot
def theme_style_decorator(cls, f):
    return "%s/css/%s" % (cls.theme.keyname, f)
# put theme javascripts in the right spot    
def theme_script_decorator(cls, f):
    return "%s/js/%s" % (cls.theme.keyname, f)
    
def theme_banner_decorator(cls, f):
    return "%s/img/banner/%s" % (cls.keyname, f)

def swap_storage_engines(sender, instance, **kwargs):
    """
    determine if the instance should use a URLStorage or OverwriteStorage engine, apply it
    """
    if instance.external and not instance.file:
        instance.file.name = instance.external
        instance.file.storage = URLStorage()

def revert_storage_engines(sender, instance, **kwargs):
    if type(instance.file.storage) is URLStorage:
        instance.file.name = None
        instance.file.storage = OverwriteStorage()

# commune helper -- returns string of path up for child section
def section_path_up(cls, glue):
    elements = cls[:]
    if elements[0].extends is not None:
        return section_path_up([elements[0].extends]+elements, glue)
    return glue.join([z.keyname for z in elements])
    

# updates the cache whenever you save a namedboxtemplate
def cache_namedbox_template(sender, instance, **kwargs):    
    cache_key = "commune:namedbox:tpl:%d" % instance.pk
    tpl = instance.content
    cache.set(cache_key, tpl)
    
    logger.info("updating cached template %s [NamedBoxTemplate]" % cache_key)