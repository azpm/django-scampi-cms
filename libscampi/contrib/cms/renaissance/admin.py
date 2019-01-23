from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from libscampi.contrib.cms.renaissance.models import *

#individual media piece config
class MediaAdmin(object):
    fieldsets = (
        ('Designation', {'fields': ('title','slug','caption','tags')}),
        ('Attribution', {'fields': ('author','credit', 'reproduction_allowed')}),
    )
    
    list_display = ['title', 'slug', 'creation_date', 'reproduction_allowed']
    list_filter = ['reproduction_allowed']

    ordering = ['-creation_date']
    date_hierarchy = 'creation_date'
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'caption']
    save_on_top = True

class FileBasedMediaAdmin(MediaAdmin, admin.ModelAdmin):
    fieldsets = MediaAdmin.fieldsets + ( ('Classification', {'fields': ('file','type')}), )
    list_filter = MediaAdmin.list_filter+['type']
    prepopulated_fields = {'slug': ('title',)}

    def get_list_display(self, request):
        if self.model is Image:
            if request.GET.get("pop",False):
                return ['title', 'popover', 'reproduction_allowed']
            else:
                return ['title', 'slug','popover','creation_date', 'reproduction_allowed']
        else:
            return self.list_display

    def popover(self, cls):
        args = {'url': cls.file.url, 'name': cls.title, 'preview': _("I")}
        return mark_safe(u"<a class='popover web-symbol' href='%(url)s' target='_blank' rel='%(url)s' title='%(name)s'>%(preview)s</a>" % args)
    popover.short_description = u"Preview"
    popover.allow_tags = True


class VideoMediaAdmin(MediaAdmin, admin.ModelAdmin):
    fieldsets = MediaAdmin.fieldsets + ( ('Classification', {'fields': ('file','thumbnail','type','url')}), )
    list_filter = MediaAdmin.list_filter+['type']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['thumbnail']

class ExternalAdmin(admin.ModelAdmin): pass
    
#generic playlist admin
class PlaylistAdmin(object):    
    fieldsets = (
        ('Designation', {'fields': ('title','slug','caption','tags')}),
        ('Display', {'fields': ('template',)})
    )
    list_display = ['title', 'creation_date']
    date_hierarchy = 'creation_date'
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'caption']
    save_on_top = True
   
#play list inline block
class RankedItemInline(object): extra = 5
class RankedImageInline(RankedItemInline, admin.TabularInline):
    model = RankedImage
    raw_id_fields= ['image']

class RankedVideoInline(RankedItemInline, admin.TabularInline): model = RankedVideo
class RankedAudioInline(RankedItemInline, admin.TabularInline): model = RankedAudio
class RankedDocumentInline(RankedItemInline, admin.TabularInline): model = RankedDocument
class RankedObjectInline(RankedItemInline, admin.TabularInline): model = RankedObject
    
#each media type as a playlist
class ImagePlaylistAdmin(PlaylistAdmin, admin.ModelAdmin): inlines = [RankedImageInline,]
class VideoPlaylistAdmin(PlaylistAdmin, admin.ModelAdmin): inlines = [RankedVideoInline,]
class AudioPlaylistAdmin(PlaylistAdmin, admin.ModelAdmin): inlines = [RankedAudioInline,]
class DocumentPlaylistAdmin(PlaylistAdmin, admin.ModelAdmin): inlines = [RankedDocumentInline,]
class ObjectPlaylistAdmin(PlaylistAdmin, admin.ModelAdmin): inlines = [RankedObjectInline,]

#media typing config
class MediaTypeAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Designation', {'fields': ('title','keyname','description')}),
        ('Display', {'fields': ('inline_template',)})
    )
    
    list_display = ('title', 'keyname', 'inline_template')
    save_on_top = True
    
class DimensionalMediaTypeAdmin(MediaTypeAdmin, admin.ModelAdmin):
    fieldsets = MediaTypeAdmin.fieldsets + ( ('Attributes', {'fields': ('width', 'height')}), )
    list_display =  MediaTypeAdmin.list_display + ('width', 'height')
    
class InlineTemplateAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(Image, FileBasedMediaAdmin)
admin.site.register(Video, VideoMediaAdmin)
admin.site.register(Audio, FileBasedMediaAdmin)
admin.site.register(Document, FileBasedMediaAdmin)
admin.site.register(Object, FileBasedMediaAdmin)
admin.site.register(External, ExternalAdmin)

admin.site.register(ImagePlaylist, ImagePlaylistAdmin)
admin.site.register(VideoPlaylist, VideoPlaylistAdmin)
admin.site.register(AudioPlaylist, AudioPlaylistAdmin)
admin.site.register(DocumentPlaylist, DocumentPlaylistAdmin)
admin.site.register(ObjectPlaylist, ObjectPlaylistAdmin)

admin.site.register(ImageType, DimensionalMediaTypeAdmin)
admin.site.register(VideoType, DimensionalMediaTypeAdmin)
admin.site.register(ObjectType, DimensionalMediaTypeAdmin)
admin.site.register(AudioType, MediaTypeAdmin)
admin.site.register(DocumentType, MediaTypeAdmin)

admin.site.register(MediaInlineTemplate, InlineTemplateAdmin)
admin.site.register(MediaPlaylistTemplate)
