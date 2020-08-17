import logging

from django.db import models
from django.core.cache import cache
from django.core.exceptions import FieldError
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from libscampi.core.fields import PickledObjectField
from libscampi.contrib.cms.validators import magic_keyname
from libscampi.contrib.cms.conduit.utils import coerce_filters, cache_picker_template
from libscampi.contrib.cms.conduit.picker import manifest
from libscampi.contrib.cms.conduit.managers import DynamicPickerManager, StaticPickerManager

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
    # TODO add the following field
    #  display_name = models.CharField(
    #  verbose_name=_("Display Name"),
    #  max_length = 100,
    #  null=True,
    #  blank=True,
    #  help_text=_("Optional display name."))
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
        """
        returns a query set of picked objects using inclusion and exclusion filters
        """
        try:
            model, fs = manifest.get_for_picking(self.content)
        except (NameError, TypeError):
            return {}

        cache_key = "conduit:dp:ids:{0:d}".format(self.pk)
        cached_ids = cache.get(cache_key, None)
        if cached_ids:
            qs = model.objects.filter(pk__in=cached_ids)
        else:
            logger.debug("cache miss on {0:>s}".format(cache_key))
            qs = model.objects.all()

        # first we handle any static defers - performance optimisation
        if fs and hasattr(fs, 'static_defer') and callable(fs.static_defer):
            defer = fs.static_defer()
            qs = qs.defer(*defer)

        # second we handle any static select_related fields - performance optimisation
        if fs and hasattr(fs, 'static_select_related') and callable(fs.static_select_related):
            select_related = fs.static_select_related()
            qs = qs.select_related(*select_related)

        # third we handle any static prefetch_related fields - performance optimisation
        if fs and hasattr(fs, 'static_prefetch_related') and callable(fs.static_prefetch_related):
            prefetch_related = fs.static_prefetch_related()
            qs = qs.prefetch_related(*prefetch_related)

        # if we got our initial list from the cache, we can return it without running the expensive filters
        if cached_ids:
            return qs

        # fourth we apply our inclusion filters
        if self.include_filters:
            try:
                for f in self.include_filters:
                    if not f:
                        continue
                    coerce_filters(f)
                    qs = qs.filter(**f)
            except ValueError as e:
                logger.error(
                    "Value Error. Failure to apply include filters on on [%d] %s. %s" % (self.pk, self.name, e))
            except FieldError as e:
                logger.error(
                    "Field Error. Failure to apply include filters on on [%d] %s. %s" % (self.pk, self.name, e))
            except Exception as e:
                logger.error("failure to coerce include filters on [%d] %s. %s" % (self.pk, self.name, e))

        # fifth we apply our exclusion filters
        if self.exclude_filters:
            try:
                for f in self.exclude_filters:
                    if not f:
                        continue
                    coerce_filters(f)
                    qs = qs.exclude(**f)
            except ValueError as e:
                logger.error(
                    "Value Error. Failure to apply exclude filters on on [%d] %s. %s" % (self.pk, self.name, e))
            except FieldError as e:
                logger.error(
                    "Field Error. Failure to apply exclude filters on on [%d] %s. %s" % (self.pk, self.name, e))
            except Exception as e:
                logger.error("failure to coerce exclude filters on [%d] %s. %s" % (self.pk, self.name, e))

        # before we limit the qs we let the picking filterset apply any last minute operations
        if fs and hasattr(fs, 'static_chain') and callable(fs.static_chain):
            qs = fs.static_chain(qs)

        # limit the qs if necessary
        if self.max_count > 0:
            for_cache = qs.values_list('id', flat=True)[:self.max_count]
            logger.debug("setting dynamic picker cache on {0:>s} - {1:>s}".format(cache_key, for_cache))
            cache.set(cache_key, list(for_cache), 60 * 10)
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
        return (self.commune.keyname, self.commune.section.display_order, self.namedbox.gridy, self.namedbox.gridx,
                self.namedbox.display_order, self.namedbox.keyname)


models.signals.post_save.connect(cache_picker_template, sender=PickerTemplate)
