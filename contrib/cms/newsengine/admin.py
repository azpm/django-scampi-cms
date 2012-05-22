import logging

from datetime import datetime

from django.core.mail import mail_admins
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError, DatabaseError
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.forms.formsets import all_valid
from django.utils import simplejson
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.template.defaultfilters import slugify, truncatewords
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

from .models import Article, ArticleTranslation, Story, StoryCategory, PublishCategory, Publish, PublishQueue
from .forms import StoryForm, ArticleTranslationForm
from .filtering import PublishTypeListFilter, ArticleAuthorListFilter

logger = logging.getLogger('libscampi.contrib.cms.newsengine.models')
csrf_protect_m = method_decorator(csrf_protect)

class ArticleTranslationInline(admin.StackedInline):
    model = ArticleTranslation
    fieldsets = (
        ('Dialect', {'fields': ['language']}),
        ('Discourse', {'fields': ('headline', 'sub_headline', 'synopsis', 'body')}),
    )
    extra = 0
    max_num = None

    form = ArticleTranslationForm

class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ['headline','sub_headline','languages','who_made_me','creation_date','modified']
    search_fields = ['translations__headline','author__first_name','author__last_name','author__username']
    fieldsets = (
        ('Authorship', {'fields': ('author', 'contributors')}),
        ('Media', {
            'description': "Usage: <strong>{% inline [media-type] [media-slug]</strong> <em>[attr1=val1,attr2=val2]</em> <strong>%}</strong>",
            'fields': (('image_inlines', 'video_inlines', 'audio_inlines'), ('document_inlines', 'object_inlines', 'external_inlines'))
        })
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
        return truncatewords(cls.headline, '5')
    headline.short_description = u"Headline"
    
    def sub_headline(self, cls):
        return truncatewords(cls.sub_headline, '5')
    sub_headline.short_description = u"Tagline"
    
     #provide the JS for the picking filter magic
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
            'admin/js/media.inlines.js',
            'admin/js/article.preview.js',
        )


    # show username w/ full name
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
        from django.conf.urls import patterns, url
        urls = super(ArticleAdmin, self).get_urls()
        
        my_urls = patterns('',
            url(r'^preview/$', self.admin_site.admin_view(self.preview), name="newsengine-article-preview"),
            url(r'^inline-media-helper/', self.admin_site.admin_view(self.inline_media_helper), name="newsengine-article-media-helper")
        )

        return my_urls + urls

    def inline_media_helper(self, request, *args, **kwargs):
        media_id = request.REQUEST.get('media_id', None)
        media_type = request.REQUEST.get('media_ctype', None)

        if not media_id or not media_type:
            raise Http404("no media_id or media_type")

        try:
            ctype = ContentType.objects.get_by_natural_key(app_label="renaissance", model=media_type)
        except ContentType.DoesNotExist:
            raise Http404("matching media type not found")

        try:
            media = ctype.get_object_for_this_type(pk=media_id)
        except ctype.model_class().DoesNotExist:
            raise Http404("matching media instance not found")

        returnable = {
            'pk': media.pk,
            'title': media.title,
            'slug': media.slug,
            'type': {'name': media.type.title, 'keyname': media.type.keyname},
            'form_of': media_type
        }

        if hasattr(media, "file"):
            returnable.update({'file': media.file.url})

        response = HttpResponse(simplejson.dumps(returnable), content_type="application/json")

        return response

    @csrf_protect_m
    def preview(self, request, *args, **kwargs):
        """
        Preview an article
        """
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        formsets = []
        inline_instances = self.get_inline_instances(request)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if not form.is_valid():
                raise Http404("Invalid Article to Preview. Article Form.")

            article = {
                'image_inines': form.cleaned_data['image_inlines'],
                'video_inlines': form.cleaned_data['video_inlines'],
                'audio_inlines': form.cleaned_data['audio_inlines'],
                'document_inlines': form.cleaned_data['document_inlines'],
                'object_inlines': form.cleaned_data['object_inlines'],
                'external_inlines': form.cleaned_data['external_inlines'],
            }

            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                    instance=self.model(),
                    save_as_new=True,
                    prefix=prefix, queryset=inline.queryset(request))
                formsets.append(formset)
            if all_valid(formsets):
                translations = formsets[0].cleaned_data

                return TemplateResponse(request,
                    "admin/newsengine/article/preview.html",
                    {'article': article, 'translations': translations},
                    current_app=self.admin_site.name)
            else:
                raise Http404("Invalid Article to Preview. Translation Form")
        else:
            raise PermissionDenied
            
        
class StoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ['headline', 'author_name', 'creation_date']
    search_fields = ['article__translations__headline','author__first_name','author__last_name','author__username']
    fieldsets = (
        ('Meta Data', {'fields': ('author','categories','article','tags')}),
        ('Media Playlists', {'fields': (('image_playlist', 'video_playlist', 'audio_playlist'),('document_playlist', 'object_playlist'))}),
        ('Relationships', {'fields': ('peers','important')}),
    )
    
    raw_id_fields = ('article', 'image_playlist', 'video_playlist', 'audio_playlist', 'document_playlist', 'object_playlist','peers')
    filter_horizontal = ['categories']

    save_on_top = True

    def author_name(self, cls):
        return cls.author.get_full_name()

    def headline(self, cls):
        try:
            val = ArticleTranslation.objects.get(language__code = 'en', model = cls.article_id)
        except ArticleTranslation.DoesNotExist:
            try:
                val = ArticleTranslation.objects.filter(model = cls.article_id)[0]
            except IndexError:
                logger.debug("Tried to get a story [%d] who's article [%d] had no available headlines" % (cls.id, cls.article_id))
                return u""
        
        return u"%s" % truncatewords(val.headline, '10')
        
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
    list_filter = ('seen','published','sticky',PublishTypeListFilter)
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
        
        return u"%s" % truncatewords(val.headline, 5)
        
    def queryset(self, request):
        qs = super(PublishStoryAdmin, self).queryset(request)
        
        return qs.select_related('site','approved_by__username','category__keyname','category__title', 'story__article_id')
                
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.start is not None and obj.start < datetime.now():
            return ('start', 'slug', 'approved_by')
        else:
            return ('slug', 'approved_by')
    
    def save_model(self, request, obj, form, change):
        if not obj.seen:
            obj.seen = True
            obj.slug = "%d%d-%s" % (obj.start.hour, obj.start.minute, slugify(obj.story.article.headline))
        
        obj.approved_by = request.user
        try:
            obj.save()
        except IntegrityError:
            logger.critical("couldn't publish a story", "%s" % locals())

class PublishQueueAdmin(PublishStoryAdmin):
    list_filter = (ArticleAuthorListFilter,PublishTypeListFilter)

    def queryset(self, request):
        qs = super(PublishQueueAdmin, self).queryset(request)
        return qs.filter(seen = False, published = False)

admin.site.register(Article, ArticleAdmin)
admin.site.register(StoryCategory)
admin.site.register(Story, StoryAdmin)
admin.site.register(PublishCategory, PublishCategoryAdmin)
admin.site.register(Publish, PublishStoryAdmin)
admin.site.register(PublishQueue, PublishQueueAdmin)