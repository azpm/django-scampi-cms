from django.db import models
from datetime import datetime, time, timedelta

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site

#scampi imports
from libscampi.contrib.cms.conduit.utils import map_picker_to_commune, unmap_orphan_picker

#local imports
from .managers import localised_section_manager, localised_element_manager
from .utils import theme_style_decorator, theme_script_decorator, theme_banner_decorator, overrive_js_file_url, section_path_up

__all__ = ['Theme','StyleSheet','Javascript','Realm','RealmNotification','Section','Commune','Slice','BoxKind','NamedBox','Application']


"""
Define a theme

This will have to be properly fleshed out for a real release
of this software as a commercial/opensource CMS
"""
class Theme(models.Model):
    name = models.CharField(_("Reference Name"), max_length = 100)
    keyname = models.SlugField(_("Internal Identifier"), max_length = 20, unique = True)
    description = models.TextField(null = True, blank = True)
    banner = models.ImageField(upload_to=theme_banner_decorator)
    def __unicode__(self):
        return "%s" % self.name
        
# provides an abstract html link reference
class HtmlLinkRef(models.Model):
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
        return "%s" % self.name

# Theme Javascript
class Javascript(HtmlLinkRef):
    file = models.FileField(upload_to = theme_script_decorator, null = True, blank = True)
    external = models.URLField(null = True, blank = True)
    class Meta:
        verbose_name = "Theme Javacript"
        verbose_name_plural = "Theme Javascripts"
        
#allow for externally hosted javascripts (like google code)        
models.signals.post_init.connect(overrive_js_file_url, sender=Javascript)

# Theme Stylesheet
class StyleSheet(HtmlLinkRef):
    ie_choices = (
        (6, 'IE 6 (Please don\'t use)'),
        (7, 'IE 7'),
        (8, 'IE 8'),
    )
    media = models.CharField(max_length = 200, help_text = "screen, print, etc")
    for_ie = models.PositiveSmallIntegerField(choices = ie_choices, null = True, blank = True)
    file = models.FileField(upload_to = theme_style_decorator)
    
    class Meta:
        verbose_name = "Theme Stylesheet"
        verbose_name_plural = "Theme Stylesheets"

"""
The meat of the CMS hierarchy follows:

# Django Site <-> Realm  
the two are the same, we use Realm to add metadata to a django site

# Realm -> section <- BaseHierarchyElemenet
sections are transparent to end users, and exist as a generic go between for
anything that needs to be organised inside a realm.

# BaseHierarchyElement <> Commune, Application
This application provides to two types of BaseHierarchyElements: Communes,
and Applications.  It is (should be!) possible to provide new types of
BaseHierarchyElemenets so that if neither an Application or Commune fit what
is necessary, you can make your own
"""

# Realm is one-to-one with django.contrib.sites.models.Site (provides metadata)
class Realm(models.Model):
    site = models.OneToOneField(Site)
    name = models.CharField(_("Reference Name"), max_length = 100)
    keyname = models.SlugField(_("URI/Template Identifier"), max_length = 20, unique = True)
    description = models.TextField(null = True, blank = True)
    display_order = models.PositiveSmallIntegerField(_("Display Order"), unique = True)
    active = models.BooleanField(default=True, db_index=True)
    secure = models.BooleanField(default=False, db_index=True)
    googleid = models.CharField(max_length=50, null=True, blank=True, help_text=_("Google Analytics ID"))
    searchable = models.BooleanField(default=True, db_index=True)
    search_collection = models.CharField(max_length=200, null = True, blank = True)
    direct_link = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Realm"
        verbose_name_plural = "Realms"
        ordering = ['display_order']
    
    def __unicode__(self):
        return "%s" % self.site.domain
        
    def _primary_section(self):
        try:
            t = self.section_set.select_related().filter(active = True, extends = None).order_by('display_order')[0]
        except IndexError:
            t = None
        return t
    primary_section = property(_primary_section)
    
    def _has_navigable_sections(self):
        t = self.section_set.filter(active = True, extends = None, generates_navigation = True)
        if len(t) > 0:
            return True
        else:
            return False
    has_navigable_sections = property(_has_navigable_sections)
        
    def get_absolute_url(self):
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
    realm = models.ForeignKey(Realm)
    name = models.CharField(_("Display Name"), max_length = 100)
    display = models.TextField()
    display_start = models.DateTimeField(db_index=True)
    display_end =  models.DateTimeField(db_index=True)
    
    class Meta:
        verbose_name = "Service Announcement"
        verbose_name_plural = "Service Announcements"
    
    def __unicode__(self):
        return "<%s> %s" % (self.realm, self.name) 


"""
sections are transparent, and are a `generic` middleman to provide
hierarchy information to any BaseHierarchyElements
"""
class Section(models.Model):
    realm = models.ForeignKey(Realm)
    keyname = models.SlugField(_("URI/Template Identifier"), max_length = 20, db_index = True)
    display_order = models.PositiveSmallIntegerField(_("Display Order"), db_index = True)
    active = models.BooleanField(default=True, db_index=True)
    generates_navigation = models.BooleanField(_("Generates Navigation"), default = True, db_index=True)
    extends = models.ForeignKey('self', null = True, blank = True, db_index = True)
    
    element_id = models.PositiveIntegerField()
    element_type = models.ForeignKey(ContentType, limit_choices_to = {
        'model__in': ('commune', 'application'), 
        'app_label__in': ('communism',),
    })
    element = generic.GenericForeignKey('element_type', 'element_id')
    
    objects = models.Manager()
    localised = localised_section_manager()
    
    class Meta:
        verbose_name = "Hierarchy Element"
        verbose_name_plural = "Hierarchy Elements"
        unique_together = (("element_id","element_type"),("realm","keyname"),("realm", "extends", "display_order"))
        ordering = ['display_order']
        
    def __unicode__(self):
        return "%s [%s]" % (self.element, self.element_type.name)
        
    def breadcrumb_helper(self):
        return "%s" % section_path_up([self], ".")
    breadcrumb_helper = property(breadcrumb_helper)
    
    def get_absolute_url(self):
        return "/%s/" % section_path_up([self], ".")

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
        return self.section.get()
    container = property(_container)
    
    def _realm(self):
        return self.container.realm
    realm = property(_realm)
    
    def _keyname(self):
        return self.container.keyname
    keyname = property(_keyname)
    
    def get_absolute_url(self):
        return "/%s/" % section_path_up([self.container], ".")
        
"""
Commune is a buildable page that contains:

slices <- 3 columns <- named box(s)

Communes are "discoverable" by:
http<commune.section.realm.secure>://commune.section.realm.site.domain/<commune.keyname>/

e.g. a commune named kuat inside non-secure realm television <-> tv.azpm.org would be:
http://tv.azpm.org/kuat/

You can have n-count, ordred slices in a Commune, each slice containing 3 fixed columns.

Each column can have content, of deterministic width:=
Column #1 is the left most column and can have content that spans upto 3 columns
Column #2 is the middle column and can have content that spans upto 2 columns
Column #3 is the right most column and can have content that spans 1 column
"""
class Commune(BaseHierarchyElement):
    theme = models.ForeignKey(Theme)
    
    class Meta:
        verbose_name = "CMS Page"
        verbose_name_plural = "CMS Pages"
        
    def _generic_template(self):
        return "%s/commune/generic.html" % self.theme.keyname
    generic_template = property(_generic_template)
    
    def _realm_override_template(self):
        return "%s/commune/%s/generic.html" % (self.theme.keyname, self.realm.keyname)
    generic_realm_template = property(_realm_override_template)

    def _commune_override_template(self):
        return "%s/commune/%s/%s.html" % (self.theme.keyname, self.realm.keyname, self.keyname)
    override_template = property(_commune_override_template)

"""
Slices and Named Boxes correspond directly with template idioms:

<div class="content-slice">
 {{ content here }}
</div>

and

<div class="content-{{type}}">

</div>

respectively
"""
class Slice(models.Model):
    name = models.CharField("Reference Name", max_length = 100)
    commune = models.ForeignKey(Commune)
    display_order = models.PositiveSmallIntegerField("Display Order") 
    
    class Meta:
        unique_together = ('commune', 'display_order')
    
    def __unicode__(self):
        return "%s > %s > #%d" % (self.commune.realm, self.commune.keyname, self.display_order)
    
class BoxKind(models.Model):
    colorhint = models.CharField("Box Top Color Hint", max_length = 20, default = "No Color")
    cssclass = models.CharField("Box Top CSS", max_length = 20, null = True, blank = True)
    
    class Meta:
        verbose_name = u"Box Kind"
        verbose_name_plural = u"Box Kinds"
        
    def __unicode__(self):
        return u"%s" % self.colorhint
        
# A named box merely provides a styled box to hold content, that content comes from a conduit.models.picker
class NamedBox(models.Model):
    column_choices = (
        (1, 'Column #1'),
        (2, 'Column #2'),
        (3, 'Column #3'),
    )
    box_type_choices = (
        ('content-sw', 'Single Width'),
        ('content-dw', 'Double Width'),
        ('content-fw', 'Full Width')
    )
    
    name = models.CharField("Reference Name", max_length = 100)
    display_name = models.CharField("Displayed Box Title", max_length = 50, null = True, blank = True)
    display_boxtop = models.BooleanField("Show Box Top", default = True)
    keyname = models.SlugField("Template/HTML Identifier", max_length = 20)
    kind = models.ForeignKey(BoxKind)   
    slice = models.ForeignKey(Slice)
    gridx = models.PositiveSmallIntegerField("Column", choices = column_choices)
    gridy = models.PositiveSmallIntegerField("Sub Slice")
    display_order = models.PositiveSmallIntegerField("Display Order")
    content = models.ForeignKey("conduit.DynamicPicker", null = True, blank = True)
    active = models.BooleanField(default = True, db_index=True)
    width_hint = models.CharField(choices = box_type_choices, max_length = 10)
    
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
    
    def _single_wide(self):
        if self.width_hint == 'content-sw':
            return True
        return False
    sw = property(_single_wide)
    
    
    def _double_wide(self):
        if self.width_hint == 'content-dw':
            return True
        return False
    dw = property(_double_wide)
    
    def _full_wide(self):
        if self.width_hint == 'content-fw':
            return True
        return False
    fw = property(_full_wide)
    
#handle mapping pickers to communes        
models.signals.post_init.connect(map_picker_to_commune, sender=NamedBox)
models.signals.post_delete.connect(unmap_orphan_picker, sender=NamedBox)

"""
Application is a pre-existing DJANGO application with it's own urls, views, models, etc.

You create an Application<BaseHierarchyElement> to allow hierarchical navigation to your pre-existing work
You must also manually set up the website urls.py to import your applications urls and use them
"""
class Application(BaseHierarchyElement):
    namespace = models.CharField("URL Namespace", max_length = 25, null = True, blank = True)
    app_name = models.CharField("Django Application Name", max_length = 50)
    default_view = models.CharField("Django View Function", max_length = 50)
    
    class Meta:
        verbose_name = "CMS Offload"
        verbose_name_plural = "CMS Offloads"