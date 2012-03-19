from django.contrib import admin

from libscampi.contrib.cms.renaissance.models import *

#individual media piece config
class MediaAdmin(object):
    fieldsets = (
        ('Designation', {'fields': ('title','slug','caption',)}),
        ('Attribution', {'fields': ('author','credit', 'reproduction_allowed')}),
    )
    
    list_display = ['title', 'slug', 'creation_date', 'reproduction_allowed']
    list_filter = ['reproduction_allowed']
    
    date_hierarchy = 'creation_date'
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'caption']
    save_on_top = True

class FileBasedMediaAdmin(MediaAdmin, admin.ModelAdmin):
    fieldsets = MediaAdmin.fieldsets + ( ('Classification', {'fields': ('file','type')}), )
    list_filter = MediaAdmin.list_filter+['type']
    prepopulated_fields = {'slug': ('title',)}
    
class VideoMediaAdmin(MediaAdmin, admin.ModelAdmin):
    fieldsets = MediaAdmin.fieldsets + ( ('Classification', {'fields': ('file','thumbnail','type')}), )
    list_filter = MediaAdmin.list_filter+['type']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['thumbnail']

class ExternalAdmin(admin.ModelAdmin): pass
    
#generic playlist admin
class PlaylistAdmin(object):    
    fieldsets = (
        ('Designation', {'fields': ('title','slug','caption',)}),
        ('Display', {'fields': ('template',)})
    )
    list_display = ['title', 'creation_date']
    date_hierarchy = 'creation_date'
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'caption']
    save_on_top = True
   
#play list inline block
class RankedItemInline(object): extra = 5
class RankedImageInline(RankedItemInline, admin.TabularInline): model = RankedImage
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
    
class MediaTypeOverrideAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Designation', {'fields': ('type',)}),
        ('Display', {'fields': ('template',)})
    )
    list_display = ('type', 'template')
    save_on_top = True
    
class DimensionalMediaTypeOverrideAdmin(MediaTypeOverrideAdmin, admin.ModelAdmin):
    fieldsets = MediaTypeOverrideAdmin.fieldsets + ( ('Attributes', {'fields': ('width', 'height')}), )
    list_display =  MediaTypeOverrideAdmin.list_display + ('width', 'height')
    
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

admin.site.register(ImageTypeOverride, DimensionalMediaTypeOverrideAdmin)
admin.site.register(VideoTypeOverride, DimensionalMediaTypeOverrideAdmin)
admin.site.register(ObjectTypeOverride, DimensionalMediaTypeOverrideAdmin)
admin.site.register(AudioTypeOverride, MediaTypeOverrideAdmin)
admin.site.register(DocumentTypeOverride, MediaTypeOverrideAdmin)

admin.site.register(MediaInlineTemplate, InlineTemplateAdmin)
admin.site.register(MediaPlaylistTemplate)