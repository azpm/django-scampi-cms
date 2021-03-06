from django.db import models

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.utils.functional import cached_property

#libscampi imports
from libscampi.contrib.cms.conduit.utils import map_picker_to_commune, unmap_orphan_picker
from libscampi.core.files.storage import OverwriteStorage

#local imports
from libscampi.contrib.cms.communism.managers import *
from libscampi.contrib.cms.communism.validators import magic_keyname
from libscampi.contrib.cms.communism.utils import *

__all__ = ['Theme','StyleSheet','Javascript','Realm','RealmNotification','Section','MagicSection','Commune','Slice','NamedBoxTemplate','NamedBox','Application']

class Theme(models.Model):
    """Defines a theme that communes utilize to provide stylesheet(s), javascript(s)
    and a set of templates that reside under a folder of keyname
    """
    
    name = models.CharField(_("Reference Name"), max_length = 100)
    keyname = models.SlugField(_("Internal Identifier"), max_length = 20, unique = True)
    description = models.TextField(null = True, blank = True)
    banner = models.ImageField(upload_to=theme_banner_decorator, verbose_name = _("Image Banner"))
    
    objects = ThemeManager()
    
    def __unicode__(self):
        return "%s" % self.name
        
    def natural_key(self):
        return self.keyname
        
    def _get_url(self):
        return "{0:>s}{1:>s}/".format(settings.MEDIA_URL, self.keyname)
    base_url = property(_get_url)

    def _static_url(self):
        return "{0:>s}{1:>s}/".format(settings.STATIC_URL, self.keyname)
    static_url = property(_static_url)

class HtmlLinkRef(models.Model):
    """Abstract base for HTML includes (css/js)"""
    name = models.CharField(max_length = 50)
    description = models.TextField(null = True, blank = True)
    precedence = models.PositiveSmallIntegerField(_("Attempt to order"))
    active = models.BooleanField(_("Active"), default=True, db_index=True)
    base = models.BooleanField(_("Always Loaded"), default=False)
    theme = models.ForeignKey(Theme)

    objects = models.Manager()
    base_active = BaseActiveLinkRefs()

    class Meta:
        abstract = True
        ordering = ['precedence']
        
    def __unicode__(self):
        return u"[{0:>s}] {1:>s}".format(self.theme.keyname, self.name)

class Javascript(HtmlLinkRef):
    """Provides the ability to utilize either an uploaded javascript file
    or an "external" file that is hosted somewhere else.  For example, if you wanted to use
    jQuery you might elect to use the Google Hosted version.
    
    Precedence represents an attempt to order the loading of scripts only.
    """
    
    file = models.FileField(upload_to = theme_script_decorator, null = True, blank = True, storage = OverwriteStorage())
    external = models.URLField(null = True, blank = True, verbose_name = _("External URL"))
    
    class Meta:
        verbose_name = "Theme Javacript"
        verbose_name_plural = "Theme Javascripts"

class StyleSheet(HtmlLinkRef):
    """Provides stylesheet (css) capabilities to a theme.  Use the IE field to apply
    the stylesheet for Internet Explorer *only*.
    """    

    ie_choices = (
        (6, 'IE 6 (Please don\'t use)'),
        (7, 'IE 7'),
        (8, 'IE 8'),
        (9, 'IE 9'),
    )
    media = models.CharField(max_length = 200, help_text = "screen, print, etc")
    for_ie = models.PositiveSmallIntegerField(choices = ie_choices, null = True, blank = True, verbose_name = _("IE Version"))
    file = models.FileField(upload_to = theme_style_decorator, storage = OverwriteStorage())
    
    class Meta:
        verbose_name = "Theme Stylesheet"
        verbose_name_plural = "Theme Stylesheets"

class Realm(models.Model):
    """First level of organization within the Scampi CMS.  Realms are effectively profiles
    for :model:`sites.Site` linked One To One and enabling a collection of metadata for
    Scampi.
    
    The meat of the CMS hierarchy follows:

    :model:`sites.Site` <-> :model:`communism.Realm`  
    the two are the same, we use Realm to add metadata to a django site

    :model:`communism.Realm` -> :model:`communism.Section` <- BaseHierarchyElement
    sections are transparent to end users, and exist as a generic go between for
    anything that needs to be organised inside a realm.

    BaseHierarchyElement <> :model:`communism.Commune`, :models:`communism.Application`
    This application provides to two types of BaseHierarchyElements: :model:`communism.Commune`,
    and :models:`communism.Application`.  It is (should be!) possible to provide new types of
    BaseHierarchyElements so that if neither an :models:`communism.Application` or :model:`communism.Commune` fit what
    is necessary, you can make your own.
    """

    site = models.OneToOneField(Site)
    name = models.CharField(_("Reference Name"), max_length = 100)
    keyname = models.SlugField(_("URI/Template Identifier"), max_length = 20, unique = True)
    description = models.TextField(null = True, blank = True)
    display_order = models.PositiveSmallIntegerField(_("Display Order"), unique = True)
    active = models.BooleanField(default=True, db_index=True)
    generates_navigation = models.BooleanField(_("Generates Navigation"), default = True, db_index=True)
    secure = models.BooleanField(default=False, db_index=True)
    googleid = models.CharField(max_length=50, null=True, blank=True, help_text=_("Google Analytics ID"))
    searchable = models.BooleanField(default=True, db_index=True, help_text = _("Flag for search form generation"))
    search_collection = models.CharField(max_length=200, null = True, blank = True, help_text = ("Keyname for search collections"))
    direct_link = models.BooleanField(default=False, verbose_name = _("Provides a direct link to some external site outside of your Scampi install"))
    theme = models.ForeignKey(Theme, help_text=_("Provides Fall Back theme for sections/applications"))
    objects = RealmManager()
    
    class Meta:
        verbose_name = "Realm"
        verbose_name_plural = "Realms"
        ordering = ['display_order']
    
    def __unicode__(self):
        return u"{0:>s}".format(self.site.domain)
        
    def natural_key(self):
        return self.keyname

    @cached_property
    def primary_section(self):
        """Returns the first active section for this realm, or None"""
        try:
            t = Section.objects.filter(active = True, extends = None, realm__id = self.id).order_by('display_order')[0]
        except IndexError:
            raise ObjectDoesNotExist("no communism.section available")
        
        return t

    @cached_property
    def tla_sections(self):
        return self.section_set.filter(active = True, extends = None, generates_navigation = True)

    @cached_property
    def has_navigable_sections(self):
        """Returns True if realm has active sections, False otherwise"""
        t = self.section_set.filter(active = True, extends = None, generates_navigation = True).exists()
        return t

    @cached_property
    def get_absolute_url(self):
        # Returns fully qualified link to realm, including http/https

        try:
            ps = self.primary_section
        except ObjectDoesNotExist:
            if self.direct_link:
                if self.secure:
                    return "https://{0:>s}/".format(self.site.domain, )
                else:
                    return "http://{0:>s}/".format(self.site.domain, )
        else:
            if ps.generates_navigation:
                if self.secure:
                    return "https://{0:>s}{1:>s}".format(self.site.domain, ps.get_absolute_url())
                else:
                    return "http://{0:>s}{1:>s}".format(self.site.domain, ps.get_absolute_url())
            else:
                if self.secure:
                    return "https://{0:>s}/".format(self.site.domain, )
                else:
                    return "http://{0:>s}/".format(self.site.domain, )

        return "#"

    def get_base_url(self):
        if self.secure:
            return "https://{0:>s}".format(self.site.domain, )
        else:
            return "http://{0:>s}".format(self.site.domain, )

class RealmNotification(models.Model):
    """Provides a simple notification system to globally publish alerts to a realm.
    """
    realm = models.ForeignKey(Realm)
    name = models.CharField(_("Display Name"), max_length = 100)
    display = models.TextField(_("Notification Content"))
    display_start = models.DateTimeField(_("Start"), db_index=True)
    display_end =  models.DateTimeField(_("End"), db_index=True)
    
    class Meta:
        verbose_name = "Service Announcement"
        verbose_name_plural = "Service Announcements"
    
    def __unicode__(self):
        return u"<{0:>s}> {1:>s}".format(self.realm, self.name)

class Section(models.Model):
    """Sections are transparent, and are a 'generic' middleman to provide
    hierarchy information to any BaseHierarchyElements
    """
    realm = models.ForeignKey(Realm)
    keyname = models.SlugField(_("URI/Template Identifier"), max_length = 20, db_index = True, validators=[magic_keyname])
    display_order = models.PositiveSmallIntegerField(_("Display Order"), db_index = True)
    active = models.BooleanField(default=True, db_index=True)
    generates_navigation = models.BooleanField(_("Generates Navigation"), default = True, db_index=True)
    extends = models.ForeignKey('self', null = True, blank = True, db_index = True)
    
    element_id = models.PositiveIntegerField(verbose_name = _("Primary Key of <BaseHierarchyElement>"))
    element_type = models.ForeignKey(ContentType, limit_choices_to = {
        'model__in': ('commune', 'application'), 
        'app_label__in': ('communism',),
    }, verbose_name = _("Type of BaseHierarchyElement"))
    element = generic.GenericForeignKey('element_type', 'element_id')
    
    objects = SectionManager()
    localised = localised_section_manager()
    
    class Meta:
        verbose_name = "Hierarchy Element"
        verbose_name_plural = "Hierarchy Elements"
        unique_together = (("element_id","element_type"),("realm","keyname"),("realm", "extends", "display_order"))
        
        ordering = ('realm__display_order', 'display_order')
        
    def __unicode__(self):
        return u"{0:>s} [{1:>s}]".format(self.element, self.element_type.name)
        
    def natural_key(self):
        return self.realm.keyname, self.keyname
        
    def breadcrumb_helper(self):
        """Returns fully dotted path to section, including path up for everything extended."""
        return "{0:>s}".format(section_path_up([self], "."))
    breadcrumb_helper = property(breadcrumb_helper)
    
    def get_absolute_url(self):
        """Returns the fully dotted URL path to section."""
        return "/{0:>s}/".format(section_path_up([self], "."))
        
    def get_real_absolute_url(self):
        realm = self.realm
        
        if realm.secure:
            return "https://{0:>s}/{1:>s}/".format(realm.site.domain, section_path_up([self], "."))
        else:
            return "http://{0:>s}/{1:>s}/".format(realm.site.domain, section_path_up([self], "."))

class MagicSection(Section):
    class Meta:
        proxy = True

    def __unicode__(self):
        return u"Magic Section"

    def breadcrumb_helper(self):
        return u""

    def get_absolute_url(self):
        return u""

    def get_real_absolute_url(self):
        return u""

    def save(self, force_insert=False, force_update=False, using=None):
        raise NotImplementedError("You cannot save the magic section!")


#abstract base class for anything to extend to get hierarchy
class BaseHierarchyElement(models.Model):
    section = generic.GenericRelation(Section, content_type_field = "element_type", object_id_field = "element_id")
    name = models.CharField(_("Display Name"), max_length = 100)
    description = models.TextField(null = True, blank = True)

    localised = localised_element_manager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"{0:>s}".format(self.name)
        
    def natural_key(self):
        return self.realm.keyname, self.keyname

    @cached_property
    def container(self):
        """Returns the section that holds this hierarchy element. used in templates."""
        #section =
        return self.section.select_related('realm','realm__site').get()

    def realm(self):
        """Returns the realm that the containing section exists on."""
        return self.container.realm
    realm = property(realm)

    def keyname(self):
        """Returns the keyname of the containing section -- hierarchy elements treat this is read only member data."""
        return self.container.keyname
    keyname = property(keyname)

    def get_absolute_url(self):
        return "/{0:>s}/".format(section_path_up([self.container], "."))
        

class Commune(BaseHierarchyElement):
    """Commune is a buildable page that contains:

    slices <- 3 columns <- named box(s)

    Communes are "discoverable" by:
    http<commune.section.realm.secure>://<commune.section.realm.site.domain>/<commune.keyname>/

    e.g. a commune named kuat inside non-secure realm television *tv.azpm.org* would be:
        http://tv.azpm.org/kuat/

    You can have n-count, ordred slices in a Commune, each slice containing 3 fixed columns.

    Each column can have content, of deterministic width

    - Column #1 is the left most column and can have content that spans upto 3 columns
    - Column #2 is the middle column and can have content that spans upto 2 columns
    - Column #3 is the right most column and can have content that spans 1 column
    """
    theme = models.ForeignKey(Theme)
    
    objects = CommuneManager()
    
    class Meta:
        verbose_name = "CMS Page"
        verbose_name_plural = "CMS Pages"
        #ordering = ('section__realm__display_order','section__display_order')

class Slice(models.Model):
    """Slices correspond directly with template idioms:
    
    This allows multiple types of 3-Column layouts on a single page.

    <div class="slice">
    -- content here --
    </div>
    """

    name = models.CharField(_("Reference Name"), max_length = 100)
    commune = models.ForeignKey(Commune)
    display_order = models.PositiveSmallIntegerField(_("Display Order"), help_text = u"1-Ordered") 
    
    objects = SliceManager()
    
    class Meta:
        unique_together = ('commune', 'display_order')
        ordering = ('display_order',)
    
    def __unicode__(self):
        return u"{0:>s} - {1:>s} #{2:d}".format(self.commune.realm.name, self.commune.keyname, self.display_order)

    def natural_key(self):
        return self.commune.keyname, self.display_order
    
class NamedBoxTemplate(models.Model):
    """Provides the ability to style a named box generically.
    
    context for <content>:
    - box: the namedbox being rendered :model:`communism.NamedBox`, use as {{ box.field_name }}
    - request: django request, use as {{ request.field_name }} comes from RequestContext
    - cms_section: :model:`communism.Section`, use as {{ cms_section.field_name }}
    - cms_realm: :model:`communism.Realm`, use as {{ cms_realm.field_name }}
       
    trivial example template:
    
    {% load pickers %}
    <div class="namedbox">
        <h2>{{ box.display_name }}</h2>
        {% render_picker box.picker %}
    </div>
          
    """
    name = models.CharField(_("Reference Name"), max_length=50, db_index=True)
    description = models.TextField(blank = True)
    content = models.TextField(_("django template"))
    
    class Meta:
        verbose_name = u"NamedBox Template"
        verbose_name_plural = u"NamedBox Templates"
        ordering = ['name',]
        
    def __unicode__(self):
        return u"{0:>s}".format(self.name)
        
class NamedBox(models.Model):
    """Holds content, either static or picked
    
    Boxes are positioned on a grid that corresponds to the three available columns.
    By default, boxes fill up as much space as possible -- e.g. placing a box in Column 1,
    subslice 1 and no other boxes in column 2 or 3 will make the box three columns wide.
    """
    
    column_choices = (
        (1, 'Column #1'),
        (2, 'Column #2'),
        (3, 'Column #3'),
    )
    #structural
    slice = models.ForeignKey(Slice)
    gridx = models.PositiveSmallIntegerField(_("Column"), choices = column_choices)
    gridy = models.PositiveSmallIntegerField(_("Sub Slice"), help_text = u"1-Ordered")
    display_order = models.PositiveSmallIntegerField(_("Display Order"), help_text = u"1-Ordered")
    #display
    name = models.CharField(_("Reference Name"), max_length = 100)
    display_name = models.CharField(_("Optional Box Title"), help_text = u"", max_length = 50, blank = True)
    template = models.ForeignKey(NamedBoxTemplate)
    #reference
    keyname = models.SlugField(_("Template/HTML Identifier"), max_length = 20)
    active = models.BooleanField(default = True, db_index=True)
    content = models.ForeignKey("conduit.DynamicPicker", null = True, blank = True, on_delete=models.SET_NULL)
    
    objects = NamedBoxManager()
    
    class Meta:
        unique_together = (('slice', 'gridx', 'gridy', 'display_order'), ('slice', 'keyname'))
        verbose_name = "Named Box"
        verbose_name_plural = "Named Boxes"
        
        ordering = ['slice', 'gridy', 'gridx', 'display_order']
    
    def __unicode__(self):
        return u"{0:>s} Column #{1:d}, {2:d}".format(self.name, self.gridx, self.display_order)
        
    def natural_key(self):
        return self.slice.commune.keyname, self.slice.display_order, self.gridy, self.gridx, self.display_order, self.keyname
    
    def _picker(self):
        if self.content:
            return self.content
        elif self.staticpicker:
            return self.staticpicker
        else:
            return None
    picker = property(_picker)
    


class Application(BaseHierarchyElement):
    """Application is a pre-existing DJANGO application with it's own urls, views, models, etc.

    You create an Application<BaseHierarchyElement> to allow hierarchical navigation to your pre-existing work
    You must also manually set up the website urls.py to import your applications urls and use them
    """
    namespace = models.CharField(_("URL Namespace"), max_length = 25, null = True, blank = True)
    app_name = models.CharField(_("Django Application Name"), max_length = 50)
    default_view = models.CharField(_("Django View Function"), max_length = 50)
    
    objects = ApplicationManager()

    @cached_property
    def theme(self):
        return self.realm.theme

    class Meta:
        verbose_name = "CMS Offload"
        verbose_name_plural = "CMS Offloads"
        
# handle mapping pickers to communes
models.signals.post_save.connect(map_picker_to_commune, sender=NamedBox)
models.signals.post_delete.connect(unmap_orphan_picker, sender=NamedBox)
# update namedbox picker template cache
models.signals.post_save.connect(cache_namedbox_template, sender=NamedBoxTemplate)
# allow for externally hosted javascripts (like google code)
models.signals.post_init.connect(swap_storage_engines, sender=Javascript)
models.signals.pre_save.connect(revert_storage_engines, sender=Javascript)
# refresh site cache on commune/section creation/update
models.signals.post_save.connect(refresh_local_site, sender=Commune)
models.signals.post_save.connect(refresh_local_site, sender=Application)
models.signals.post_save.connect(refresh_local_site, sender=Section)
