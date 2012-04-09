import django_filters
from datetime import datetime

from taggit.managers import TaggableManager

from django.db import models
from django.db.models import Count, Max, Avg, Min
from django.contrib.comments.models import Comment
from django.contrib.contenttypes import generic
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.moderation import moderator

#libscampi contributed packages
from libscampi.contrib.multilingual.models import Language, MultilingualModel
from libscampi.contrib.cms.renaissance.models import Image, Video, Audio, Document, Object, External, ImagePlaylist, VideoPlaylist, AudioPlaylist, DocumentPlaylist, ObjectPlaylist, ImageTypeOverride, VideoTypeOverride, AudioTypeOverride, DocumentTypeOverride, ObjectTypeOverride
from libscampi.contrib.cms.conduit import picker
from libscampi.contrib.cms.conduit.widgets import PickerFilterSelectMultiple
from libscampi.contrib.cms.newsengine.managers import PublishedManager, CategoryGenera
from libscampi.contrib.cms.newsengine.commenting import StoryModerator

__all__ = ['ArticleTranslation','Article','StoryCategory','Story',
    'PublishCategory','Publish','PublishInlineMediaOverride','PublishPicking']
    
class ArticleTranslation(models.Model):
    language = models.ForeignKey(Language)
    model = models.ForeignKey('Article', related_name = 'translations')
    
    headline = models.CharField(_('Article Title'), max_length = 255, 
            help_text = _("Article Title. No markup allowed."))
    sub_headline = models.CharField(_('Article Tagline'), max_length = 255, 
            help_text = _("Will be truncated to 30 words when viewed as a spotlight.  No markup allowed."))
    synopsis = models.TextField(blank = True,
            help_text = _("Article Synopsis, markup(down) allowed: see <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown Syntax</a> for help"))
    body = models.TextField(blank = True,
            help_text = _("Article body, markup(down) allowed: see <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown Syntax</a> for help"))
            
    class Meta:
        unique_together = ('language', 'model')
        verbose_name = 'Article Translation'
        verbose_name_plural = 'Article Translations'
    
    def __unicode__(self):
        return u"%s" % self.headline
    
class Article(MultilingualModel):
    contributors = models.ManyToManyField(User, related_name = "contributors", null = True, blank = True, limit_choices_to={'is_staff':True})
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, editable = False, null = True)
    modified = models.DateTimeField(auto_now=True)
    
    image_inlines = models.ManyToManyField(Image, blank = True, help_text = "Images (inline)")
    video_inlines = models.ManyToManyField(Video, blank = True, help_text = "Videos (inline)")
    audio_inlines = models.ManyToManyField(Audio, blank = True, help_text = "Audios (inline)")
    document_inlines = models.ManyToManyField(Document, blank = True, help_text = "Documents (inline)")
    object_inlines = models.ManyToManyField(Object, blank = True, help_text = "Objects (inline)")
    external_inlines = models.ManyToManyField(External, blank = True, help_text = "Externals (inline)")
    
    class Meta:
        translation = ArticleTranslation
        ordering = ('-creation_date',)
        multilingual = ['headline','sub_headline','synopsis','body']
        verbose_name = "Article"
        verbose_name_plural = "Articles"
    
    def who_made_me(self):
        return u"%s" % self.author.get_full_name()
    who_made_me.short_description = "Creating Editor"
    
    def __unicode__(self):
        return u"%s" % self.headline
  
class StoryCategory(models.Model):
    title = models.CharField(max_length = 100)
    keyname =  models.SlugField(max_length = 100, db_index = True)
    
    browsable = models.BooleanField(default=True)
    seen = models.PositiveIntegerField(default = 0, editable = False)
    shared = models.PositiveIntegerField(default = 0, editable = False)
    
    description = models.TextField(blank = True)
    
    objects = models.Manager()
    genera = CategoryGenera()
    
    class Meta:
        ordering = ('keyname',)
        verbose_name = "Story Category"
        verbose_name_plural = "Story Categories"
    
    def __unicode__(self):
        return u"%s" % self.title
    
class Story(models.Model):
    article = models.ForeignKey(Article)
    categories = models.ManyToManyField(StoryCategory)
    author = models.ForeignKey(User, limit_choices_to={'is_staff':True})
    creation_date = models.DateTimeField(verbose_name = "Creation Date", auto_now_add=True)    
    modified = models.DateTimeField(auto_now=True)
    peers = models.ManyToManyField('self', related_name='related_stories', null = True, blank = True)
    important = models.BooleanField(default = False)
    
    tags = TaggableManager(blank=True)
    
    image_playlist = models.ForeignKey(ImagePlaylist, null = True, blank = True)
    video_playlist = models.ForeignKey(VideoPlaylist, null = True, blank = True)
    audio_playlist = models.ForeignKey(AudioPlaylist, null = True, blank = True)
    document_playlist = models.ForeignKey(DocumentPlaylist, null = True, blank = True)
    object_playlist = models.ForeignKey(ObjectPlaylist, null = True, blank = True)

    class Meta:
        ordering = ('-creation_date',)
        verbose_name = "Story"
        verbose_name_plural = "Stories"
        
    def __unicode__(self):
        return u"%s" % self.article
    
class PublishCategory(models.Model):
    keyname = models.SlugField(max_length = 100, db_index = True)
    title = models.CharField(max_length = 100)
    description = models.TextField(blank = True)
    
    class Meta:
        verbose_name = "Publishing Word"
        verbose_name_plural = "Publishing Words"
        
    def __unicode__(self):
        return u"%s" % (self.title)
    
class Publish(models.Model):
    story = models.ForeignKey(Story)
    site = models.ForeignKey(Site, limit_choices_to = {'realm__direct_link': False}, null = True, blank = True)
    thumbnail = models.ForeignKey(Image, null = True, blank = True)
    approved_by = models.ForeignKey(User, null = True)
    start = models.DateTimeField(null = True, db_index = True)
    end = models.DateTimeField(null = True, blank = True, db_index = True)
    category = models.ForeignKey(PublishCategory, null = True, verbose_name="Kind")
    published = models.BooleanField(default = False, db_index = True)       
    
    slug = models.SlugField(max_length = 255, null = True, unique_for_date = start)
    sticky = models.BooleanField(default=False)
    order_me = models.PositiveSmallIntegerField(default=0)
    seen = models.BooleanField(default=False)

    comments = generic.GenericRelation(Comment, object_id_field='object_pk') # reverse generic relation
    objects = models.Manager()
    active = PublishedManager()
    
    class Meta:
        verbose_name = "Published Story"
        verbose_name_plural = "Published Stories"
        ordering = ('sticky','order_me','-start')
    
    def __unicode__(self):
        return "%s > %s" % (self.site, self.story.article.headline)
        
    def get_absolute_url(self):
        return "%d/%d/%d/%s/" % (self.start.year, self.start.month, self.start.day, self.slug)

    @property
    def comments_enabled(self):
        delta = datetime.now() - self.start
        return delta.days < 30

class PublishInlineMediaOverride(models.Model):
    publish = models.OneToOneField(Publish)
    image_inlines = models.ManyToManyField(ImageTypeOverride)
    video_inlines = models.ManyToManyField(VideoTypeOverride)
    audio_inlines = models.ManyToManyField(AudioTypeOverride)
    document_inlines = models.ManyToManyField(DocumentTypeOverride)
    object_inlines = models.ManyToManyField(ObjectTypeOverride)
    
    class Meta:
        verbose_name = "Publish Inline Media Override"
        verbose_name_plural = "Publish Inline Media Overrides"

class PublishPicking(django_filters.FilterSet):
    start = django_filters.filters.DateRangeFilter(lookup_type=('lt','gt','lte','gte'))
    end = django_filters.filters.DateRangeFilter(name="end", lookup_type=('lt','gt','lte','gte'))
    story__categories = django_filters.filters.ModelMultipleChoiceFilter(queryset=StoryCategory.objects.all(), widget=PickerFilterSelectMultiple("Story Categories",False))  
    
    class Meta:
        model = Publish
        fields = ['site','start','end','category','published','story__categories']
        
                
    @staticmethod
    def static_chain(qs):
        qs = qs.distinct()
        return qs
        
    @staticmethod
    def static_select_related():
        return (
            'thumbnail',
            'story__author',
        )
        
    @staticmethod
    def static_prefetch_related():
        return (
            'story__article',
            'story__article__image_inlines',
            'story__article__video_inlines',
            'story__article__audio_inlines',
            'story__article__document_inlines',
            'story__article__object_inlines',
        )
        
    @staticmethod
    def static_defer():
        return (
            'end',
            'approved_by',
            'category',
            'seen',
            'published',
            'thumbnail__author',
            'thumbnail__creation_date',
            'thumbnail__reproduction_allowed',
            'thumbnail__modified',
            'thumbnail__mime_type',
            'story__author__email',
            'story__author__password',
            'story__author__is_staff',
            'story__author__is_active',
            'story__author__is_superuser',
            'story__author__last_login',
            'story__author__date_joined',
            'story__seen',
            'story__shared',
            'story__creation_date',
            'story__modified',
            'story__image_playlist',
            'story__video_playlist',
            'story__audio_playlist',
            'story__document_playlist',
            'story__object_playlist',
        )
        
#moderate publish comments
moderator.register(Story, StoryModerator)

#picking
picker.manifest.register(Publish, PublishPicking)