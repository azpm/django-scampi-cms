import logging

from django.db import models
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

#scampi stuff
from libscampi.core.fields import PickledObjectField 
from libscampi.contrib.cms.communism.models import Commune
from libscampi.utils.functional import cached_property
from libscampi.contrib.cms.newsengine.utils import cache_publishpicker_base_cats

#local imports
from libscampi.contrib.cms.conduit.utils import coerce_filters, cache_picker_template
from libscampi.contrib.cms.conduit.picker import manifest
from libscampi.contrib.cms.conduit.managers import DynamicPickerManager, StaticPickerManager

logger = logging.getLogger('libscampi.contrib.cms.conduit.models')

__all__ = ['PickerTemplate','DynamicPicker','StaticPicker']

class PickerTemplate(models.Model):
    """
    A picker template for dynamic picker rendering.  Each template is given a RequestContext
    containing the following variables:
    
    - picker: the picker being render
    - cms_realm: the current realm :model:`communism.Realm`
    - cms_section: the current section :model:`communism.Section`
    - page: the current Page instance
    - request: from RequestContext 
    - perms: from RequestContext
    """
    name =  models.CharField(help_text = _("Name for easier reference"), max_length = 100, unique = True)
    content = models.TextField(_("django template"))
    stylesheet = models.ManyToManyField('communism.StyleSheet', blank = True)
    javascript = models.ManyToManyField('communism.Javascript', blank = True)
    
    class Meta:
        verbose_name = "Picker Template"
        verbose_name_plural = "Picker Templates"
        
    def __unicode__(self):
        return self.name

class PickerBase(models.Model):
    name = models.CharField(help_text = _("Name for easier reference"), max_length = 100, unique = True)
    commune = models.ForeignKey(Commune, null = True, blank = True, related_name = "%(class)s_related")
    
    class Meta:
        abstract = True
        ordering = ['precedence']
    
class DynamicPicker(PickerBase):
    keyname = models.SlugField(max_length = 100, help_text = _("URL Keyname for permalinks"))
    template = models.ForeignKey(PickerTemplate)
    max_count = models.PositiveSmallIntegerField(help_text = _("Max items to be picked at a time. A 0 indicates unlimited."), default = 0)
    content = models.ForeignKey(ContentType, verbose_name = _("Content Source"))
    include_filters = PickledObjectField(editable = False, compress = True)
    exclude_filters = PickledObjectField(editable = False, compress = True)
    
    objects = DynamicPickerManager()
    
    class Meta:
        unique_together = ('commune', 'keyname')
        verbose_name = "Dynamic Content Picker"
        verbose_name_plural = "Dynamic Content Pickers"
        
    def __unicode__(self):
        return self.name
        
    def natural_key(self):
        if self.commune:
            return (self.commune.keyname, self.keyname)
        return (None, self.keyname)

    def picked(self):
        """
        returns a query set of picked objects using inclusion and exclusion filters
        """
        try:
            model, fs = manifest.get_for_picking(self.content)
        except (NameError, TypeError):
            return {}

        cache_key = "conduit:dp:ids:%d" % self.pk
        cached_ids = cache.get(cache_key, None)
        if cached_ids:
            qs = model.objects.filter(id__in=cached_ids)
            return qs
        logger.debug("cache miss on %s" % cache_key)

        #first we handle any static defers - performance optimisation
        if fs and hasattr(fs, 'static_defer'):
            defer = fs.static_defer()
            qs = model.objects.defer(*defer)
        else:
            qs = model.objects.all() 
            
        #second we handle any static select_related fields - performance optimisation    
        if fs and hasattr(fs, 'static_select_related'):
            select_related = fs.static_select_related()
            qs = qs.select_related(*select_related)
        
        #third we handle any static prefetch_related fields - performance optimisation    
        if fs and hasattr(fs, 'static_prefetch_related'):
            prefetch_related = fs.static_prefetch_related()
            qs = qs.prefetch_related(*prefetch_related)
        
        #fourth we apply our inclusion filters
        if self.include_filters:
            for f in self.include_filters:
                if not f:
                    continue
                coerce_filters(f)
                qs = qs.filter(**f)
        
        #fifth we apply our exclusion filters
        if self.exclude_filters:
            for f in self.exclude_filters:
                if not f:
                    continue
                coerce_filters(f)
                qs = qs.exclude(**f)
    
        #before we limit the qs we let the picking filterset apply any last minute operations
        if fs and hasattr(fs, 'static_chain') and callable(fs.static_chain):
            qs = fs.static_chain(qs)        
            
        #limit the qs if necessary
        if self.max_count > 0:
            for_cache = qs.values_list('id', flat=True)
            cache.set(cache_key, for_cache[:self.max_count], 60*10)
            return qs[:self.max_count]

        cache.set(cache_key, qs.values_list('id', flat=True), 60*10)
        return qs
        
    def get_absolute_url(self):
        if self.commune:
            return "/%s/%s/" % (self.commune.keyname, self.keyname)
        
        return ""
        
class StaticPicker(PickerBase):
    content = models.TextField(_("Content"), help_text = _("Markdown friendly"))
    namedbox = models.OneToOneField("communism.NamedBox", null = True, blank = True)
    stylesheet = models.ManyToManyField('communism.StyleSheet', blank = True)
    javascript = models.ManyToManyField('communism.Javascript', blank = True)
    
    objects = StaticPickerManager()
    
    class Meta:
        verbose_name = "Static Content Picker"
        verbose_name_plural = "Static Content Pickers"
        
    def __unicode__(self):
        return self.name
        
    def natural_key(self):
        return (self.commune.keyname, self.commune.display_order, self.namedbox.gridy, self.namedbox.gridx, self.namedbox.display_order, self.namedbox.keyname)
        
models.signals.post_save.connect(cache_publishpicker_base_cats, sender=DynamicPicker)
models.signals.post_save.connect(cache_picker_template, sender=PickerTemplate)