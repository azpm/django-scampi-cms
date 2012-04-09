import logging

from datetime import datetime, timedelta

from django.db import IntegrityError, DatabaseError
from django.db.models import Count
from django.contrib import admin
from django.forms.formsets import all_valid
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.template.defaultfilters import slugify, truncatewords
from django.core.exceptions import PermissionDenied, ValidationError

from .models import Article, ArticleTranslation, Story, StoryCategory, PublishCategory, Publish, PublishInlineMediaOverride
from .forms import ArticleTranslationForm, StoryForm, PublishForm
from .filtering import ReviewedListFilter, ArticleAuthorListFilter

logger = logging.getLogger('libscampi.contrib.cms.newsengine.models')

class ArticleTranslationInline(admin.StackedInline):
    model = ArticleTranslation
    fieldsets = (
        ('Discourse', {'fields': ('headline', 'sub_headline', 'synopsis', 'body')}),
        ('Dialect', {'fields': ['language']}),
    )
    extra = 1
    #form = ArticleTranslationForm

class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ['headline','sub_headline','languages','who_made_me']
    search_fields = ['translations__headline']
    fieldsets = (
        ('Meta Data', {'fields': ('author', 'contributors')}),
        ('Inline Media', {'fields': (('image_inlines', 'video_inlines', 'audio_inlines'), ('document_inlines', 'object_inlines', 'external_inlines')), 'classes': ('collapse',)})
    )
    raw_id_fields = ('contributors','image_inlines', 'video_inlines', 'audio_inlines', 'document_inlines', 'object_inlines', 'external_inlines')
    readonly_fields = ('author',)
    inlines = [ArticleTranslationInline]
    save_on_top = True
    
    def queryset(self, request):
        qs = super(ArticleAdmin, self).queryset(request)
        
        return qs.select_related('author').annotate(languages=Count('translations__headline'))
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user           
        obj.save()
        
    def languages(self, cls):
        return u"%d" % cls.languages
    
    def headline(self, cls):
        return cls.headline
    headline.short_description = u"Headline"
    
    def sub_headline(self, cls):
        return cls.sub_headline
    sub_headline.short_description = u"Sub Headline"
    
     #provide the JS for the picking filter magic
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
            'http://ajax.microsoft.com/ajax/jquery.templates/beta1/jquery.tmpl.js',
        )
        css = {
            'screen': ('gravity-plugins/bootstrap/css/bootstrap.buttons.css',),
        }
    
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
                
    #override the urls method to add our picking form fields return
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(ArticleAdmin, self).get_urls()
        
        my_urls = patterns('',
            url(r'^preview/$', self.admin_site.admin_view(self.preview), name="newsengine-article-preview"),
        )

        return my_urls + urls
                
    def preview(self, request, *args, **kwargs):
        """"The 'add' admin view for this model."""
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request) or not self.has_change_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            
            if form.is_valid():
                new_object = form.save(commit=False)
                form_validated = True
            else:
                form_validated = False
                new_object = self.model()
            
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new="_saveasnew" in request.POST,
                                  prefix=prefix, queryset=inline.queryset(request))
                formsets.append(formset)
            
            if all_valid(formsets) and form_validated:
                #self.save_model(request, new_object, form, change=False)
                #form.save_m2m()
                arts = []
                for formset in formsets:
                    if formset.model == ArticleTranslation:
                        arts.append(formset.save(commit=False))

                #self.log_addition(request, new_object)
                #return self.response_add(request, new_object)
                assert False
            else:
                assert False
        else:
            raise PermissionDenied
            
        
class StoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ['headline', 'author', 'creation_date','important']
    list_filter = ['categories']
    search_fields = ['article__translations__headline']
    fieldsets = (
        ('Meta Data', {'fields': ('author','categories','article',)}),
        ('Media Playlists', {'fields': (('image_playlist', 'video_playlist', 'audio_playlist'),('document_playlist', 'object_playlist'))}),
        ('Relationships', {'fields': ('peers','important')}),
    )
    
    raw_id_fields = ('article', 'image_playlist', 'video_playlist', 'audio_playlist', 'document_playlist', 'object_playlist','peers')
    filter_horizontal = ['categories']

    save_on_top = True

    def headline(self, cls):
        try:
            val = ArticleTranslation.objects.get(language__code = 'en', model = cls.article_id)
        except ArticleTranslation.DoesNotExist:
            try:
                val = ArticleTranslation.objects.filter(model = cls.article_id)[0]
            except IndexError:
                logger.debug("Tried to get a story [%d] who's article [%d] had no available headlines" % (cls.id, cls.article_id))
                return u""
        
        return u"%s" % truncatewords(val.headline, '5')
        
    def queryset(self, request):
        qs = super(StoryAdmin, self).queryset(request)
        
        return qs.select_related('article','author')

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
    save_on_top = True
    fieldsets = (
        ('Information', {'fields': ('title','keyname')}),
        ('Description', {'fields': ('description',), 'classes': ('collapse',)}),
    )
    
class PublishStoryAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('headline','category','start','end','sticky','order_me','published','approved_by')
    list_display_links = ('headline',)
    list_editable = ('sticky','order_me')
    list_filter = (ReviewedListFilter, ArticleAuthorListFilter, 'published','sticky','category__title')
    date_hierarchy = 'start'
    raw_id_fields = ('story','thumbnail')
    search_fields = ['story__article__translations__headline']
    fieldsets = (
        ('Publish Target', {'fields': ('site','category', ('story', 'thumbnail', 'slug'))}),
        ('Publish Configuration', {'fields': ('start','end','sticky','order_me')}),
        ('Publish Auditing', {'fields': ('approved_by', 'published')}),
    )
    
    list_select_related = True
    save_as = True
    
    ordering = ('-start','sticky','order_me')

    def headline(self, cls):
        try:
            val = ArticleTranslation.objects.get(language__code = 'en', model = cls.story.article_id)
        except ArticleTranslation.DoesNotExist:
            try:
                val = ArticleTranslation.objects.filter(model = cls.story.article_id)[0]
            except IndexError:
                logger.debug("Tried to get a published story [%d] who's article [%d] had no available headlines" % (cls.id, cls.story.article_id))
                return u""
        
        return u"%s" % return u"%s" % truncatewords(val.headline, 5)
        
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