from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from libscampi.contrib.cms.communism import models
from libscampi.contrib.cms.communism import filtering
from libscampi.contrib.cms.communism.utils import section_path_up
from libscampi.contrib.cms.conduit.admin import StaticPickerInlineAdmin


@admin.register(models.Realm)
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
        'search_collection'
    )
    list_editable = ('display_order', 'active', 'secure', 'searchable', 'search_collection')
    fieldsets = (
        ('Domain & Configuration', {'fields': ('site', 'name', 'keyname', 'description', 'theme')}),
        ('Meta', {'fields': ('display_order', 'active', 'generates_navigation', 'secure', 'direct_link')}),
        ('Google Related', {'fields': (('searchable', 'search_collection'), 'googleid')})
    )
    save_on_top = True


@admin.register(models.RealmNotification)
class RealmNotificationAdmin(admin.ModelAdmin):
    list_display = ('realm', 'name', 'display_start', 'display_end')
    list_filter = ('realm',)
    save_on_top = True


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'realm', 'keyname', 'extends', 'active', 'display_order', 'generates_navigation')
    list_editable = ('active', 'display_order', 'generates_navigation')

    list_filter = ('realm',)
    save_on_top = True


class SectionInline(GenericTabularInline):
    ct_field = 'element_type'
    ct_fk_field = 'element_id'
    model = models.Section
    raw_id_fields = ('extends', 'realm', )
    fieldsets = (
        ('Hierarchy Data',
         {'fields': ('realm', 'keyname', 'display_order', 'extends', 'active', 'generates_navigation')}),
    )
    max_num = 1
    extra = 1


@admin.register(models.Slice)
class SliceAdmin(admin.ModelAdmin):
    list_display = ('name', 'my_location', 'display_order')
    list_editable = ('display_order',)
    list_filter = (filtering.SliceRealmFilter, filtering.SliceCommuneFilter,)
    search_fields = ('name', 'commune__name')
    save_on_top = True

    ordering = ('commune', 'display_order')

    def get_queryset(self, request):
        qs = super(SliceAdmin, self).get_queryset(request)

        return qs.select_related('commune')

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
    model = models.Slice
    extra = 1


@admin.register(models.NamedBoxTemplate)
class NamedBoxTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fields = ('name', 'description', 'content')
    save_on_top = True


@admin.register(models.NamedBox)
class BoxAdmin(admin.ModelAdmin):
    list_display_links = ('name',)
    list_display = ('name', 'template', 'slice', 'gridx', 'gridy', 'display_order')
    list_editable = ('template', 'gridx', 'gridy', 'display_order')
    raw_id_fields = ['slice', 'content']
    list_filter = (filtering.NamedBoxRealmFilter, filtering.NamedBoxCommuneFilter)
    fieldsets = (
        ('General', {'fields': ('slice', ('name', 'keyname', 'active'))}),
        ('Display', {'fields': ('display_name', 'template')}),
        ('Arrangement', {'fields': ('gridx', 'gridy', 'display_order')}),
        ('Dynamic Content', {'fields': ('content',), 'description': "Dynamic Content takes precedence over static!"})
    )
    inlines = [StaticPickerInlineAdmin]
    search_fields = ('name', 'keyname')
    list_per_page = 20
    save_on_top = True

    def get_queryset(self, request):
        qs = super(BoxAdmin, self).get_queryset(request)

        return qs.select_related('slice').prefetch_related('template')


class BaseHierarchyElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'realm', 'traverse_up', 'my_order', 'keyname')
    list_filter = ('section__realm',)
    search_fields = ['name', 'section__realm__name', ]
    save_on_top = True

    def traverse_up(self, obj):
        return section_path_up([obj.container], " > ")

    traverse_up.short_description = "Section Hierarchy"

    def my_order(self, obj):
        return obj.container.display_order

    my_order.short_description = "Display Order"


@admin.register(models.Commune)
class CommuneAdmin(BaseHierarchyElementAdmin):
    fieldsets = (
        ('General', {'fields': ('name', 'description', 'theme')}),
    )
    inlines = (SectionInline, SliceInline)


@admin.register(models.Application)
class ApplicationAdmin(BaseHierarchyElementAdmin):
    fieldsets = (
        ('General', {'fields': ('name', 'description')}),
        ('Application Config', {'fields': ('namespace', 'app_name', 'default_view'), 'classes': ('wide',)}),
    )
    inlines = (SectionInline,)


@admin.register(models.StyleSheet, models.Javascript)
class GenericDOMElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'precedence', 'active', 'base', 'theme')
    list_editable = ('precedence', 'active', 'base')
    list_filter = ['theme']
    save_on_top = True


admin.site.register(models.Theme)
