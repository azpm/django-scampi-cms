import logging
from collections import OrderedDict
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from libscampi.core.fields import PickledObjectField
from libscampi.contrib.cms.conduit.utils import coerce_filters, cache_picker_template
from libscampi.contrib.cms.conduit.picker import manifest
from libscampi.contrib.cms.conduit.managers import DynamicPickerManager, StaticPickerManager
from libscampi.contrib.cms.conduit.validators import magic_keyname


logger = logging.getLogger('libscampi.contrib.cms.conduit.models')

__all__ = ['PickerTemplate', 'DynamicPicker', 'StaticPicker']


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
    name = models.CharField(help_text=_("Name for easier reference"), max_length=100, unique=True)
    content = models.TextField(_("django template"))
    stylesheet = models.ManyToManyField('communism.StyleSheet', blank=True)
    javascript = models.ManyToManyField('communism.Javascript', blank=True)

    class Meta:
        verbose_name = "Picker Template"
        verbose_name_plural = "Picker Templates"

    def __unicode__(self):
        return u"{0:>s}".format(self.name)


class PickerBase(models.Model):
    name = models.CharField(help_text=_("Name for easier reference"), max_length=100, unique=True)
    commune = models.ForeignKey('communism.Commune', verbose_name=_('Primary Commune'), null=True, blank=True,
                                related_name="%(class)s_related")

    class Meta:
        abstract = True
        ordering = ['precedence']
        permissions = (
            ('change_picker_commune', 'User can change commune association of DynamicPicker')
        )


class DynamicPicker(PickerBase):
    # TODO display_name = models.CharField(verbose_name=_("Display Name"), max_length = 100, null=True, blank=True, help_text=_("Optional display name."))
    active = models.BooleanField(default=False)
    keyname = models.SlugField(max_length=100, help_text=_("URL Keyname for permalinks"), validators=[magic_keyname])
    template = models.ForeignKey(PickerTemplate)
    max_count = models.PositiveSmallIntegerField(
        help_text=_("Max items to be picked at a time. A 0 indicates unlimited."), default=0)
    content = models.ForeignKey(ContentType, verbose_name=_("Content Source"))
    include_filters = PickledObjectField(editable=False, compress=True)
    exclude_filters = PickledObjectField(editable=False, compress=True)

    objects = DynamicPickerManager()

    class Meta:
        unique_together = ('keyname',)
        verbose_name = "Dynamic Content Picker"
        verbose_name_plural = "Dynamic Content Pickers"

    def __unicode__(self):
        return u"{0:>s}".format(self.name)

    def natural_key(self):
        if self.commune:
            return self.commune.keyname, self.keyname
        return None, self.keyname

    def picked(self):
        """returns a query set of picked objects using inclusion and exclusion filters"""
        try:
            model, fs = manifest.get_for_picking(self.content)
        except (NameError, TypeError):
            return {}

        def sort_filters(x, y):
            if '__exact' in x:
                x_low = -1
            elif '__in' in x:
                x_low = 0
            else:
                x_low = 1

            if '__exact' in y:
                y_low = -1
            elif '__in' in y:
                y_low = 0
            else:
                y_low = 1

            return cmp(x_low, y_low)

        ordered_include_filters = []
        if self.include_filters:
            for f in self.include_filters:
                ordered_include_filters.append(OrderedDict(sorted(f.items(), key=lambda x: x[0], cmp=sort_filters)))

        ordered_exclude_filters = []
        if self.exclude_filters:
            for f in self.exclude_filters:
                ordered_exclude_filters.append(OrderedDict(sorted(f.items(), key=lambda x: x[0], cmp=sort_filters)))

        qs = model.objects

        for filters in ordered_include_filters:
            coerce_filters(filters)
            qs = qs.filter(**filters)

        for filters in ordered_exclude_filters:
            coerce_filters(filters)
            qs = qs.exclude(**filters)

        if getattr(fs, 'query_set', None):
            qs = fs.query_set(qs)

        if self.max_count > 0:
            return qs[:self.max_count]

        return qs

    def get_absolute_url(self):
        if self.commune:
            return "/p/{0:>s}/".format(self.keyname)

        return ""


class StaticPicker(PickerBase):
    content = models.TextField(_("Content"), help_text=_("Markdown friendly"))
    namedbox = models.OneToOneField("communism.NamedBox", null=True, blank=True)
    stylesheet = models.ManyToManyField('communism.StyleSheet', blank=True)
    javascript = models.ManyToManyField('communism.Javascript', blank=True)

    objects = StaticPickerManager()

    class Meta:
        verbose_name = "Static Content Picker"
        verbose_name_plural = "Static Content Pickers"

    def __unicode__(self):
        return u"{0:>s}".format(self.name)

    def natural_key(self):
        return self.commune.keyname, self.commune.section.display_order, self.namedbox.gridy, self.namedbox.gridx, self.namedbox.display_order, self.namedbox.keyname


models.signals.post_save.connect(cache_picker_template, sender=PickerTemplate)
