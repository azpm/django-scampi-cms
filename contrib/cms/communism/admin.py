from django.contrib import admin
from django.contrib.contenttypes import generic

from libscampi.contrib.cms.conduit.admin import StaticPickerInlineAdmin

#local imports
from .models import *
from .utils import section_path_up

class RealmAdmin(admin.ModelAdmin):
    list_display = ('site', 'name', 'keyname', 'display_order', 'active', 'secure', 'searchable', 'search_collection')
    list_editable = ('display_order', 'active', 'secure', 'searchable', 'search_collection')
    fieldsets = (
        ('Domain & Configuration', {'fields': ('site', 'name', 'keyname','description')}),
        ('Meta', {'fields': ('display_order','active','secure','direct_link')}),
        ('Google Related', {'fields': (('searchable','search_collection'), 'googleid')})
    )

class RealmNotificationAdmin(admin.ModelAdmin):
    list_display = ('realm', 'name', 'display_start', 'display_end')
    list_filter = ('realm',)
    
class SectionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'realm', 'keyname', 'extends','active','display_order','generates_navigation')
    list_editable = ('active','display_order','generates_navigation')
    
    list_filter = ('realm',)

class SectionInline(generic.GenericTabularInline):
    ct_field = 'element_type'
    ct_fk_field = 'element_id'
    model = Section
    fieldsets = (
        ('Hierarchy Data', {'fields': ('realm', 'keyname', 'display_order', 'extends', 'active', 'generates_navigation')}),
    )
    max_num = 1
    extra = 1

class SliceAdmin(admin.ModelAdmin):
    list_display = ('name', 'traverse_up', 'display_order')
    list_editable = ('display_order',)
    search_fields = ('name','commune__name')

    def traverse_up(self, cls):
        return "%s -> %s" % (cls.commune.realm, section_path_up([cls.commune.container], " > "))
    traverse_up.short_description = "Section Hierarchy"

class SliceInline(admin.TabularInline):
    fieldsets = (
        ('Slice', {'fields': ('name', 'display_order')}),
    )
    model = Slice
    extra = 1
    
class BoxKindAdmin(admin.ModelAdmin):
    list_display = ('colorhint','cssclass')
    fieldsets = (
        ('Basic', {'fields': ('colorhint', 'cssclass')}),
    )
    search_fields = ('colorhint',)

class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'keyname', 'display_name', 'display_boxtop', 'slice', 'gridx', 'gridy', 'display_order')
    #list_filter = ('slice',)
    list_display_links = ('name',)
    list_editable = ('display_name', 'display_boxtop', 'gridx', 'gridy', 'display_order')
    raw_id_fields = ['slice','content']
    fieldsets = (
        ('General', {'fields': ('slice', ('name', 'keyname', 'active'))}),
        ('Display', {'fields': ('display_name', 'display_boxtop', 'kind', 'width_hint')}),
        ('Arrangement', {'fields': ('gridx', 'gridy', 'display_order')}),
        ('Dynamic Content', {'fields': ('content',), 'description': "Dynamic Content takes precedence over static!"})
    )
    inlines = [StaticPickerInlineAdmin]
    search_fields = ('name','keyname')
    list_per_page = 20
    
class BaseHierarchyElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'realm', 'traverse_up', 'keyname')
    search_fields = ['name','section__realm__name',]
    
    def traverse_up(self, cls):
        return section_path_up([cls.container], " > ")
    traverse_up.short_description = "Section Hierarchy"
    
class CommuneAdmin(BaseHierarchyElementAdmin):
    fieldsets = (
        ('General', {'fields': ('name', 'description', 'theme')}),
        ('Archives', {'fields': ('archive_categories',)}),
    )
    filter_horizontal = ('archive_categories',)
    #list_filter = ('section__realm__site',)
    inlines = (SectionInline, SliceInline)
       
class ApplicationAdmin(BaseHierarchyElementAdmin):   
    fieldsets = (
        ('General', {'fields': ('name', 'description')}),
        ('Application Config', {'fields': ('namespace', 'app_name', 'default_view'), 'classes': ('wide',)}),
    )
    inlines = (SectionInline,)

class GenericDOMElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'precedence', 'active','base', 'theme')
    list_editable = ('precedence', 'active', 'base')
    list_filter = ['theme']

admin.site.register(Theme)
admin.site.register(StyleSheet, GenericDOMElementAdmin)
admin.site.register(Javascript, GenericDOMElementAdmin)
admin.site.register(Realm, RealmAdmin)
admin.site.register(RealmNotification, RealmNotificationAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(NamedBox, BoxAdmin)
admin.site.register(BoxKind, BoxKindAdmin)
admin.site.register(Commune, CommuneAdmin)
admin.site.register(Application, ApplicationAdmin)