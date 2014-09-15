from django.contrib import admin
from django.contrib.contenttypes import generic
from libscampi.contrib.cms.communism.models import *
from libscampi.contrib.cms.communism.utils import section_path_up

__all__ = ['RealmAdmin', 'RealmNotificationAdmin', 'SectionAdmin', 'SliceAdmin', 'SliceInline', 'NamedBoxTemplateAdmin',
           'BoxAdmin', 'CommuneAdmin', 'ApplicationAdmin', 'GenericDOMElementAdmin']


class RealmAdmin(admin.ModelAdmin):
    list_display = (
        'site',
        'name',
        'keyname',
        'theme',
        'display_order',
        'active',
        'generates_navigation',
        'secure',
        'searchable',
        'search_collection',
    )
    list_editable = ('display_order', 'active', 'secure', 'searchable', 'search_collection')
    fieldsets = (
        ('Domain & Configuration', {'fields': ('site', 'name', 'keyname', 'description', 'theme')}),
        ('Meta', {'fields': ('display_order', 'active', 'generates_navigation', 'secure', 'direct_link')}),
        ('Google Related', {'fields': (('searchable', 'search_collection'), 'googleid')})
    )
    save_on_top = True


class RealmNotificationAdmin(admin.ModelAdmin):
    list_display = ('realm', 'name', 'display_start', 'display_end')
    list_filter = ('realm',)
    save_on_top = True


class SectionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'realm', 'keyname', 'extends', 'active', 'display_order', 'generates_navigation')
    list_editable = ('active', 'display_order', 'generates_navigation')

    list_filter = ('realm',)
    save_on_top = True


class SectionInline(generic.GenericTabularInline):
    ct_field = 'element_type'
    ct_fk_field = 'element_id'
    model = Section
    fieldsets = (
        ('Hierarchy Data',
         {'fields': ('realm', 'keyname', 'display_order', 'extends', 'active', 'generates_navigation')}),
    )
    max_num = 1
    extra = 1


class SliceAdmin(admin.ModelAdmin):
    list_display = ('name', 'my_location', 'display_order')
    list_editable = ('display_order',)
    search_fields = ('name', 'commune__name')
    save_on_top = True

    ordering = ('commune', 'display_order')


    def queryset(self, request):
        qs = super(SliceAdmin, self).queryset(request)

        return qs.select_related('commune__section__realm', 'commune')

    def my_location(self, cls):
        return "{0:>s} -> {1:>s}".format(cls.commune.realm, cls.commune.name)

    my_location.short_description = "Realm / Commune"

    def traverse_up(self, cls):
        return "{0:>s} -> {1:>s}".format(cls.commune.realm, section_path_up([cls.commune.container], " > "))

    traverse_up.short_description = "Section Hierarchy"


class SliceInline(admin.TabularInline):
    fieldsets = (
        ('Slice', {'fields': ('name', 'display_order')}),
    )
    model = Slice
    extra = 1


class NamedBoxTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fields = ('name', 'description', 'content')
    save_on_top = True


class BoxAdmin(admin.ModelAdmin):
    # list_display = ('name', 'keyname', 'display_name', 'template', 'slice', 'gridx', 'gridy', 'display_order')
    list_display_links = ('name',)
    #list_editable = ('display_name', 'template', 'gridx', 'gridy', 'display_order')
    list_display = ('name', 'template', 'slice', 'gridx', 'gridy', 'display_order')
    list_editable = ('template', 'gridx', 'gridy', 'display_order')
    raw_id_fields = ['slice', 'content']
    list_filter = ('slice__commune',)
    fieldsets = (
        ('General', {'fields': ('slice', ('name', 'keyname', 'active'))}),
        ('Display', {'fields': ('display_name', 'template')}),
        ('Arrangement', {'fields': ('gridx', 'gridy', 'display_order')}),
        ('Dynamic Content', {'fields': ('content',), 'description': "Dynamic Content takes precedence over static!"})
    )
    search_fields = ('name', 'keyname')
    list_per_page = 20
    save_on_top = True

    def queryset(self, request):
        qs = super(BoxAdmin, self).queryset(request)

        return qs.select_related('slice').prefetch_related('template')


class BaseHierarchyElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'realm', 'traverse_up', 'my_order', 'keyname')
    list_filter = ('section__realm',)
    search_fields = ['name', 'section__realm__name', ]
    save_on_top = True

    def traverse_up(self, cls):
        return section_path_up([cls.container], " > ")

    traverse_up.short_description = "Section Hierarchy"

    def my_order(self, cls):
        return cls.container.display_order

    my_order.short_description = "Display Order"


class CommuneAdmin(BaseHierarchyElementAdmin):
    fieldsets = (
        ('General', {'fields': ('name', 'description', 'theme')}),
    )
    inlines = (SectionInline, SliceInline)


class ApplicationAdmin(BaseHierarchyElementAdmin):
    fieldsets = (
        ('General', {'fields': ('name', 'description')}),
        ('Application Config', {'fields': ('namespace', 'app_name', 'default_view'), 'classes': ('wide',)}),
    )
    inlines = (SectionInline,)


class GenericDOMElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'precedence', 'active', 'base', 'theme')
    list_editable = ('precedence', 'active', 'base')
    list_filter = ['theme']
    save_on_top = True


admin.site.register(Theme)
admin.site.register(StyleSheet, GenericDOMElementAdmin)
admin.site.register(Javascript, GenericDOMElementAdmin)
admin.site.register(Realm, RealmAdmin)
admin.site.register(RealmNotification, RealmNotificationAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(NamedBox, BoxAdmin)
admin.site.register(NamedBoxTemplate, NamedBoxTemplateAdmin)
admin.site.register(Commune, CommuneAdmin)
admin.site.register(Application, ApplicationAdmin)
