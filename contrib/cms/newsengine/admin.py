from datetime import datetime, timedelta

from django.db import IntegrityError, DatabaseError
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.template.defaultfilters import slugify

from .models import Article, ArticleTranslation, Story, StoryCategory, PublishCategory, Publish, PublishInlineMediaOverride
from .forms import ArticleTranslationForm, StoryForm, PublishForm

class ArticleTranslationInline(admin.StackedInline):
    model = ArticleTranslation
    fieldsets = (
        ('Dialect', {'fields': ['language']}),
        ('Discourse', {'fields': ('headline', 'sub_headline', 'body')}),
    )
    extra = 1
    min_num = 1
    form = ArticleTranslationForm

class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ['en_headline','en_sub_headline','who_made_me']
    search_fields = ['headline']
    fieldsets = (
        ('Meta Data', {'fields': ('author', 'contributors')}),
        ('Inline Media', {'fields': (('image_inlines', 'video_inlines', 'audio_inlines'), ('document_inlines', 'object_inlines', 'external_inlines')), 'classes': ('collapse',)})
    )
    raw_id_fields = ('contributors','image_inlines', 'video_inlines', 'audio_inlines', 'document_inlines', 'object_inlines', 'external_inlines')
    readonly_fields = ('author',)
    inlines = [ArticleTranslationInline]
    
    def queryset(self, request):
        qs = super(ArticleAdmin, self).queryset(request)
        
        return qs.select_related('author')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user           
        obj.save()
        
    def en_headline(self, cls):
        return cls.headline_en
    en_headline.short_description = u"Headline [en]"
    
    def en_sub_headline(self, cls):
        return cls.sub_headline_en
    en_sub_headline.short_description = u"Sub Headline [en]"
    
    """
    In addition to showing a user's username in related fields, show their full
    name too (if they have one and it differs from the username).
    """
    always_show_username = True  
    
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        field = super(ArticleAdmin, self).formfield_for_manytomany(
                                                db_field, request, **kwargs)
        if db_field.rel.to == User:
            field.label_from_instance = self.get_user_label
        return field

    
    def get_user_label(self, user):
        name = user.get_full_name()
        username = user.username
        if not self.always_show_username:
            return name or username
        return (name and name != username and '%s (%s)' % (name, username)
                or username)
        
class StoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ['headline', 'author', 'creation_date']
    list_filter = ['categories']
    search_fields = ['article__translations__headline']
    fieldsets = (
        ('Meta Data', {'fields': ('author','categories','article','seen','shared')}),
        ('Media Playlists', {'fields': (('image_playlist', 'video_playlist', 'audio_playlist'),('document_playlist', 'object_playlist'))}),
        ('Relationships', {'fields': ('peers',)}),
    )
    readonly_fields = ('seen','shared')
    
    raw_id_fields = ('article', 'image_playlist', 'video_playlist', 'audio_playlist', 'document_playlist', 'object_playlist','peers')
    filter_horizontal = ['categories']
    
    def headline(self, cls):
        return u"%s" % cls.article.headline
    
    def queryset(self, request):
        qs = super(StoryAdmin, self).queryset(request)
        
        return qs.select_related('author', 'article__translations__headline').filter(article__translations__language__code = 'en')
    

    def save_model(self, request, obj, form, change):
        obj.save()
        
        if not change:
            publish_request = Publish(story=obj, published = False)
            try:
                publish_request.save()
            except (DatabaseError, IntegrityError):
                mail_admins("couldn't pre-publish a story", "%s" % locals(), fail_silently = True)
    
    form = StoryForm
    
class PublishCategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Information', {'fields': ('title','keyname')}),
        ('Description', {'fields': ('description',), 'classes': ('collapse',)}),
    )
    
class PublishStoryAdmin(admin.ModelAdmin):
    list_display = ('site','headline','category','start','end','published','approved_by')
    list_display_links = ('headline',)
    list_editable = ('published',)
    list_filter = ('site','category','published','seen')
    date_hierarchy = 'start'
    raw_id_fields = ('story','thumbnail')
    search_fields = ['story__article__translations__headline']
    fieldsets = (
        ('Publish Target', {'fields': ('site','category', ('story', 'thumbnail', 'slug'))}),
        ('Publish Configuration', {'fields': ('start','end')}),
        ('Publish Auditing', {'fields': ('approved_by', 'published')}),
    )
    
    list_select_related = True
    save_as = True
    
    ordering = ['-id']
    
    #form = PublishForm
    
    def headline(self, cls):
        try:
            val = ArticleTranslation.objects.get(language__code = 'en', model = cls.story.article_id)
        except ArticleTranslation.DoesNotExist:
            return u""
        
        return u"%s" % val.headline
        
    def queryset(self, request):
        qs = super(PublishStoryAdmin, self).queryset(request)
        
        return qs.select_related('site','approved_by__username','category__keyname','category__title', 'story__article_id')
                
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.start is not None and obj.start < datetime.now():
            return ('start', 'slug', 'approved_by')
        else:
            return ('slug', 'approved_by')
    
    def save_model(self, request, obj, form, change):
        if obj.seen == False:
            obj.seen = True
            obj.slug = "%d%d-%s" % (obj.start.hour, obj.start.minute, slugify(obj.story.article.headline))
        
        obj.approved_by = request.user
        try:
            obj.save()
        except IntegrityError:
            mail_admins("couldn't publish a story", "%s" % locals(), fail_silently = True)
                
admin.site.register(Article, ArticleAdmin)
admin.site.register(PublishInlineMediaOverride)
admin.site.register(StoryCategory)
admin.site.register(Story, StoryAdmin)
admin.site.register(PublishCategory, PublishCategoryAdmin)
admin.site.register(Publish, PublishStoryAdmin)