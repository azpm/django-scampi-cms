import logging

from django.core.cache import cache
from django.contrib.sites.models import Site
from libscampi.core.files.storage import OverwriteStorage
from libscampi.contrib.cms.communism.storage import URLStorage

logger = logging.getLogger('libscampi.contrib.cms.communism.utils')

__all__ = ['theme_style_decorator', 'theme_script_decorator', 'theme_banner_decorator', 'swap_storage_engines', 'revert_storage_engines', 'refresh_local_site', 'section_path_up', 'cache_namedbox_template']

# theme helpers


def theme_style_decorator(cls, f):
    """ put theme stylesheets in the right spot """
    return "%s/css/%s" % (cls.theme.keyname, f)


def theme_script_decorator(cls, f):
    """ put theme javascripts in the right spot """
    return "%s/js/%s" % (cls.theme.keyname, f)
    

def theme_banner_decorator(cls, f):
    return "%s/img/banner/%s" % (cls.keyname, f)


def swap_storage_engines(sender, instance, **kwargs):
    """ determine if the instance should use a URLStorage or OverwriteStorage engine, apply it """
    if instance.external and not instance.file:
        instance.file.name = instance.external
        instance.file.storage = URLStorage()


def revert_storage_engines(sender, instance, **kwargs):
    """ Swaps a file storage from URL to OverwriteStorage -- used when about to save Javascript Files """
    if type(instance.file.storage) is URLStorage:
        instance.file.name = None
        instance.file.storage = OverwriteStorage()


def refresh_local_site(sender, instance, **kwargs):
    """
    clear local site cache, is fired when:
        any Commune, Application or Section is saved
    """
    Site.objects.clear_cache()


def section_path_up(cls, glue):
    """
    commune helper -- returns string of path up for child section
    """
    elements = cls[:]
    if elements[0].extends is not None:
        return section_path_up([elements[0].extends]+elements, glue)
    return glue.join([z.keyname for z in elements])


def cache_namedbox_template(sender, instance, **kwargs):    
    """
    Caches a named box template into default cache.  Is triggered whenever a namedbox changes.
    """
    cache_key = "commune:namedbox:tpl:{0:d}".format(instance.pk)
    tpl = instance.content
    cache.set(cache_key, tpl)
    
    logger.info("updating cached template %s [NamedBoxTemplate]" % cache_key)
