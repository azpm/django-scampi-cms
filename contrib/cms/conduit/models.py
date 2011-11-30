import logging

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

#scampu stuff
from libscampi.core.fields import PickledObjectField 
from libscampi.contrib.cms.communism.models import Commune
from libscampi.utils.functional import cached_property

#local imports
from libscampi.contrib.cms.conduit.utils import coerce_filters, cache_picker_template
from libscampi.contrib.cms.conduit.picker import manifest

logger = logging.getLogger('libscampi.contrib.cms.conduit.models')

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

models.signals.post_save.connect(cache_picker_template, sender=PickerTemplate)

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
    
    class Meta:
        unique_together = ('commune', 'keyname')
        verbose_name = "Dynamic Content Picker"
        verbose_name_plural = "Dynamic Content Pickers"
        
    def __unicode__(self):
        return self.name
    
    def picked(self):
        try:
            model, fs = manifest.get_for_picking(self.content)
        except (NameError, TypeError):
            return {}

        qs = model.objects.select_related().all()       
        if self.include_filters:
            for f in self.include_filters:
                coerce_filters(f)
                qs = qs.filter(**f)
        
        if self.exclude_filters:
            for f in self.exclude_filters:
                coerce_filters(f)
                qs = qs.exclude(**f)
    
        if fs and hasattr(fs, 'static_chain') and callable(fs.static_chain):
            qs = fs.static_chain(qs)        
            
        if self.max_count > 0:
            return qs[:self.max_count]
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
    
    class Meta:
        verbose_name = "Static Content Picker"
        verbose_name_plural = "Static Content Pickers"
        
    def __unicode__(self):
        return self.name