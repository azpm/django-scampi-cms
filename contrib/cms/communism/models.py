from django.db import models
from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site

#libscampi imports
from libscampi.contrib.cms.conduit.utils import map_picker_to_commune, unmap_orphan_picker

#local imports
from .managers import localised_section_manager, localised_element_manager
from .utils import theme_style_decorator, theme_script_decorator, theme_banner_decorator, overrive_js_file_url, section_path_up, cache_namedbox_template

__all__ = ['Theme','StyleSheet','Javascript','Realm','RealmNotification','Section','Commune','Slice','NamedBoxTemplate','NamedBox','Application']

class Theme(models.Model):
    """Defines a theme that communes utilize to provide stylesheet(s), javascript(s)
    and a set of templates that reside under a folder of keyname
    """
    
    name = models.CharField(_("Reference Name"), max_length = 100)
    keyname = models.SlugField(_("Internal Identifier"), max_length = 20, unique = True)
    description = models.TextField(null = True, blank = True)
    banner = models.ImageField(upload_to=theme_banner_decorator, verbose_name = _("Image Banner"))
    
    def __unicode__(self):
        return "%s" % self.name
        
    def _get_url(self):
        return "%s%s/" % (settings.MEDIA_URL, self.keyname)
    base_url = property(_get_url)
        
class HtmlLinkRef(models.Model):
    """Abstract base for HTML includes (css/js)"""
    name = models.CharField(max_length = 50)
    description = models.TextField(null = True, blank = True)
    precedence = models.PositiveSmallIntegerField(_("Attempt to order"))
    active = models.BooleanField(_("Active"), default=True, db_index=True)
    base = models.BooleanField(_("Always Loaded"), default=False)
    theme = models.ForeignKey(Theme)
    class Meta:
        abstract = True
        ordering = ['precedence']
        
    def __unicode__(self):
        return "[%s] %s" % (self.theme.keyname, self.name)

class Javascript(HtmlLinkRef):
    """Provides the ability to utilize either an uploaded javascript file
    or an "external" file that is hosted somewhere else.  For example, if you wanted to use
    jQuery you migh elect to use the Google Hosted version.
    
    Precedence represents an attempt to order the loading of scripts only.
    """
    
    file = models.FileField(upload_to = theme_script_decorator, null = True, blank = True)
    external = models.URLField(null = True, blank = True, verbose_name = _("External URL"))
    
    class Meta:
        verbose_name = "Theme Javacript"
        verbose_name_plural = "Theme Javascripts"
        
#allow for externally hosted javascripts (like google code)        
models.signals.post_init.connect(overrive_js_file_url, sender=Javascript)

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
    file = models.FileField(upload_to = theme_style_decorator)
    
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

    :model:`communism.Realm` -> :model:`communism.Section` <- BaseHierarchyElemenet
    sections are transparent to end users, and exist as a generic go between for
    anything that needs to be organised inside a realm.

    BaseHierarchyElement <> :model:`communism.Commune`, :models:`communism.Application`
    This application provides to two types of BaseHierarchyElements: :model:`communism.Commune`,
    and :models:`communism.Application`.  It is (should be!) possible to provide new types of
    BaseHierarchyElemenets so that if neither an :models:`communism.Application` or :model:`communism.Commune` fit what
    is necessary, you can make your own.
    """

    site = models.OneToOneField(Site)
    name = models.CharField(_("Reference Name"), max_length = 100)
    keyname = models.SlugField(_("URI/Template Identifier"), max_length = 20, unique = True)
    description = models.TextField(null = True, blank = True)
    display_order = models.PositiveSmallIntegerField(_("Display Order"), unique = True)
    active = models.BooleanField(default=True, db_index=True)
    secure = models.BooleanField(default=False, db_index=True)
    googleid = models.CharField(max_length=50, null=True, blank=True, help_text=_("Google Analytics ID"))
    searchable = models.BooleanField(default=True, db_index=True, help_text = _("Flag for search form generation"))
    search_collection = models.CharField(max_length=200, null = True, blank = True, help_text = ("Keyname for search collections"))
    direct_link = models.BooleanField(default=False, verbose_name = _("Provides a direct link to some external site outside of your Scampi install"))
    
    class Meta:
        verbose_name = "Realm"
        verbose_name_plural = "Realms"
        ordering = ['display_order']
    
    def __unicode__(self):
        return "%s" % self.site.domain
        
    def _primary_section(self):
        "Returns the first active section for this realm, or None"
        try:
            t = self.section_set.filter(active = True, extends = None).order_by('display_order')[0]
        except IndexError:
            t = None
        return t
    primary_section = property(_primary_section)
    
    def _tla_sections(self):
        return self.section_set.filter(active = True, extends = None, generates_navigation = True)
    tl_sections = property(_tla_sections)
    
    def _has_navigable_sections(self):
        "Returns True if realm has active sections, False otherwise"
        t = self.section_set.filter(active = True, extends = None, generates_navigation = True).exists()
        return t
    has_navigable_sections = property(_has_navigable_sections)
        
    def get_absolute_url(self):
        "Returns fully qualified link to realm, including http/https"
        ps = self.primary_section
        if ps and ps.generates_navigation == True: 
            if self.secure:
                return "https://%s%s" % (self.site.domain, ps.get_absolute_url())
            else:
                return "http://%s%s" % (self.site.domain, ps.get_absolute_url())
        elif ps and ps.generates_navigation == False:
            if self.secure:
                return "https://%s/" % (self.site.domain,)
            else:
                return "http://%s/" % (self.site.domain,)
        elif self.direct_link:
            if self.secure:
                return "https://%s/" % (self.site.domain,)
            else:
                return "http://%s/" % (self.site.domain,)
        else:
            return "#"
            

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
        return "<%s> %s" % (self.realm, self.name) 

class Section(models.Model):
    """Sections are transparent, and are a 'generic' middleman to provide
    hierarchy information to any BaseHierarchyElements
    """
    realm = models.ForeignKey(Realm)
    keyname = models.SlugField(_("URI/Template Identifier"), max_length = 20, db_index = True)
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
    
    objects = models.Manager()
    localised = localised_section_manager()
    
    class Meta:
        verbose_name = "Hierarchy Element"
        verbose_name_plural = "Hierarchy Elements"
        unique_together = (("element_id","element_type"),("realm","keyname"),("realm", "extends", "display_order"))
        
        ordering = ('realm__display_order', 'display_order')
        
    def __unicode__(self):
        return "%s [%s]" % (self.element, self.element_type.name)
        
    def breadcrumb_helper(self):
        """Returns fully dotted path to section, including path up for everything extended."""
        return "%s" % section_path_up([self], ".")
    breadcrumb_helper = property(breadcrumb_helper)
    
    def get_absolute_url(self):
        """Returns the fully dotted URL path to section."""
        return "/%s/" % section_path_up([self], ".")
        
    def get_real_absolute_url(self):
        realm = self.realm
        
        if realm.secure:
            return "https://%s/%s/" % (realm.site.domain, section_path_up([self], "."))
        else:
            return "http://%s/%s/" % (realm.site.domain, section_path_up([self], "."))

#abstract base class for anything to extend to get hierarchy
class BaseHierarchyElement(models.Model):
    section = generic.GenericRelation(Section, content_type_field = "element_type", object_id_field = "element_id")
    name = models.CharField(_("Display Name"), max_length = 100)
    description = models.TextField(null = True, blank = True)

    objects = models.Manager()
    localised = localised_element_manager()
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return "%s" % self.name
        
    def _container(self):
        """Returns the section that holds this hierarchy element. used in templates."""
        return self.section.get()
    container = property(_container)
    
    def _realm(self):
        """Returns the realm that the containing section exists on."""
        return self.container.realm
    realm = property(_realm)
    
    def _keyname(self):
        """Returns the keyname of the containing section -- hierarchy elements treat this is read only member data."""
        return self.container.keyname
    keyname = property(_keyname)
    
    def get_absolute_url(self):
        return "/%s/" % section_path_up([self.container], ".")
        

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
    
    class Meta:
        verbose_name = "CMS Page"
        verbose_name_plural = "CMS Pages"

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
    
    class Meta:
        unique_together = ('commune', 'display_order')
    
    def __unicode__(self):
        return "%s > %s > #%d" % (self.commune.realm, self.commune.keyname, self.display_order)
    
    
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
        
    def __unicode__(self):
        return self.name
        
models.signals.post_save.connect(cache_namedbox_template, sender=NamedBoxTemplate)
        
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
    
    content = models.ForeignKey("conduit.DynamicPicker", null = True, blank = True)
    
    class Meta:
        unique_together = (('slice', 'gridx', 'gridy', 'display_order'), ('slice', 'keyname'))
        verbose_name = "Named Box"
        verbose_name_plural = "Named Boxes"
        
        ordering = ['slice', 'gridy', 'gridx', 'display_order']
    
    def __unicode__(self):
        return "%s Column #%d, %d" % (self.name, self.gridx, self.display_order)
    
    def _picker(self):
        if self.content:
            return self.content
        elif self.staticpicker:
            return self.staticpicker
        else:
            return None
    picker = property(_picker)
    
#handle mapping pickers to communes        
models.signals.post_save.connect(map_picker_to_commune, sender=NamedBox)
models.signals.post_delete.connect(unmap_orphan_picker, sender=NamedBox)

class Application(BaseHierarchyElement):
    """Application is a pre-existing DJANGO application with it's own urls, views, models, etc.

    You create an Application<BaseHierarchyElement> to allow hierarchical navigation to your pre-existing work
    You must also manually set up the website urls.py to import your applications urls and use them
    """
    namespace = models.CharField(_("URL Namespace"), max_length = 25, null = True, blank = True)
    app_name = models.CharField(_("Django Application Name"), max_length = 50)
    default_view = models.CharField(_("Django View Function"), max_length = 50)
    
    class Meta:
        verbose_name = "CMS Offload"
        verbose_name_plural = "CMS Offloads"