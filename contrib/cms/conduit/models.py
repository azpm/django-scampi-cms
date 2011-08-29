from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

#libazpm stuff
from libscampi.core.fields import PickleField 
from libscampi.contrib.cms.conduit.utils import coerce_filters
from libscampi.contrib.cms.conduit.picker import manifest
from libscampi.contrib.cms.communism.models import *

class PickerTemplate(models.Model):
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
    precedence = models.PositiveSmallIntegerField(_("Order hint for picker graph"), default = 0)
    class Meta:
        abstract = True
        ordering = ['precedence']

    
class DynamicPicker(PickerBase):
    name = models.CharField(max_length = 50, help_text = _("Picker Name"))
    keyword = models.SlugField(max_length = 50, help_text = _("Picker Slug/URL Reference"))
    description = models.CharField(max_length = 200, null = True, blank = True)
    commune = models.ForeignKey(Commune)
    template = models.ForeignKey(PickerTemplate)
    max_count = models.PositiveSmallIntegerField(help_text = _("Max items to be picked at a time"))
    content = models.ForeignKey(ContentType, verbose_name = _("Content Source"), help_text = _("What model will populate this picker?"))
    include_filters = PickleField(editable = False, compress = True)
    exclude_filters = PickleField(editable = False, compress = True)
    
    class Meta:
        verbose_name = "Dynamic Content Picker"
        verbose_name_plural = "Dynamic Content Pickers"
        
        unique_together = ('commune', 'keyword')
        
    def __unicode__(self):
        return self.name
    
    def picked(self):
        try:
            model, fs = manifest.get_for_picking(self.content)
        except (NameError, TypeError):
            return {}

        qs = model.objects.select_related().all()       
        if self.include_filters:
            f = self.include_filters
            coerce_filters(f)
            qs = qs.filter(**f)
        if self.exclude_filters:
            f = self.exclude_filters
            coerce_filters(f)
            qs = qs.exclude(**f)
        
            
        if fs and hasattr(fs, 'static_chain') and callable(fs.static_chain):
            qs = fs.static_chain(qs)        
        if self.max_count > 0:
            return qs[:self.max_count]
        return qs
    
    #def _get_objects(self):
        
    #picked = property(_get_objects)


        
class StaticPicker(PickerBase):
    content = models.TextField(_("Content"), help_text = _("Markdown friendly"))
    namedbox = models.OneToOneField("communism.NamedBox", null = True, blank = True)
    class Meta:
        verbose_name = "Static Content Picker"
        verbose_name_plural = "Static Content Pickers"
        
    def __unicode__(self):
        return self.name