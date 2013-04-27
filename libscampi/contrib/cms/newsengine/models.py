from datetime import datetime, timedelta
from itertools import chain

from django.db import models
from django.db.models import Q, Count
from django.contrib.comments.models import Comment
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.moderation import moderator
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property

from taggit.managers import TaggableManager

#libscampi contributed packages
from libscampi.contrib import django_filters
from libscampi.contrib.multilingual.models import Language, MultilingualModel
from libscampi.contrib.cms.renaissance.models import Image, Video, Audio, Document, Object, External, ImagePlaylist, VideoPlaylist, AudioPlaylist, DocumentPlaylist, ObjectPlaylist
from libscampi.contrib.cms.conduit import picker
from libscampi.contrib.cms.conduit.widgets import PickerFilterSelectMultiple
from libscampi.contrib.cms.newsengine.managers import PublishedManager, CategoryGenera
from libscampi.contrib.cms.newsengine.commenting import StoryModerator
from libscampi.contrib.cms.newsengine.validators import validate_article

__all__ = ['ArticleTranslation','Article','StoryCategory','Story','PublishCategory','Publish','PublishPicking']
    
class ArticleTranslation(models.Model):
    language = models.ForeignKey(Language)
    model = models.ForeignKey('Article', related_name = 'translations')
    
    headline = models.CharField(_('Article Headline'), max_length = 255,
            help_text = _("Article Title. No markup allowed."))
    sub_headline = models.CharField(_('Article Tag line'), max_length = 255,
            help_text = _("Will be truncated to 30 words when viewed as a spotlight.  No markup allowed."))
    synopsis = models.TextField(blank = True,
            help_text = _("Article Synopsis, markup(down) allowed: see <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown Syntax</a> for help"))
    body = models.TextField(blank = True,
            help_text = _("Article body, markup(down) allowed: see <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown Syntax</a> for help"),
            validators=[validate_article]
    )
            
    class Meta:
        unique_together = ('language', 'model')
        verbose_name = 'Article Translation'
        verbose_name_plural = 'Article Translations'
    
    def __unicode__(self):
        return u"{0:>s}".format(self.headline)
    
class Article(MultilingualModel):
    contributors = models.ManyToManyField(User, related_name = "contributors", null = True, blank = True)
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, editable = False, null = True)
    modified = models.DateTimeField(auto_now=True)
    
    image_inlines = models.ManyToManyField(Image, blank = True, verbose_name = _("Images"), help_text = "Images (inline)")
    video_inlines = models.ManyToManyField(Video, blank = True, verbose_name = _("Videos"), help_text = "Videos (inline)")
    audio_inlines = models.ManyToManyField(Audio, blank = True, verbose_name = _("Audio"), help_text = "Audios (inline)")
    document_inlines = models.ManyToManyField(Document, blank = True, verbose_name = _("Documents"), help_text = "Documents (inline)")
    object_inlines = models.ManyToManyField(Object, blank = True, verbose_name = _("HTML Objects"), help_text = "Objects (inline)")
    external_inlines = models.ManyToManyField(External, blank = True, verbose_name = _("Widgets"), help_text = "Externals (inline)")
    
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
        return u"{0:>s}".format(self.headline)
  
class StoryCategory(models.Model):
    title = models.CharField(max_length = 100)
    keyname =  models.SlugField(max_length = 100, db_index = True)

    seen = models.PositiveIntegerField(default = 0, editable = False)
    shared = models.PositiveIntegerField(default = 0, editable = False)

    # flags
    browsable = models.BooleanField(default=True, help_text=_("Visible in category filters list on archive pages."), db_index=True)
    excluded = models.BooleanField(default=False, help_text=_("Hide from Story Archives."), db_index=True)
    active = models.BooleanField(default=True, help_text=_("Active in backend."), db_index=True)
    collection = models.BooleanField(verbose_name=_("Collection"), default=False, help_text=_("Is a 'collection' Category"), db_index=True)
    logo = models.ForeignKey(Image, null = True, blank = True)

    description = models.TextField(blank = True)
    
    objects = models.Manager()
    genera = CategoryGenera()
    
    class Meta:
        ordering = ('keyname',)
        verbose_name = "Story Category"
        verbose_name_plural = "Story Categories"
    
    def __unicode__(self):
        if self.collection:
            return u"[collection] {0:>s}".format(self.title)

        return u"{0:>s}".format(self.title)
    
class Story(models.Model):
    article = models.ForeignKey(Article)
    categories = models.ManyToManyField(StoryCategory)
    author = models.ForeignKey(User)
    creation_date = models.DateTimeField(verbose_name = "Creation Date", auto_now_add=True)    
    modified = models.DateTimeField(auto_now=True)
    peers = models.ManyToManyField('self', related_name='related_stories', null = True, blank = True)
    important = models.BooleanField(default = False)
    slug = models.SlugField(max_length = 250, null = True, unique = True, editable = False)

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
        return u"{0:>s}".format(self.article)

    def related(self):
        cats = self.categories.exclude(excluded=True).values_list('id', flat=True)

        right_now = datetime.now()
        long_ago = right_now - timedelta(days=30)

        # lets grab peers first
        peers = Story.objects.filter(
            Q(peers__in=[self.pk]),
            publish__published=True,
            publish__start__lte=right_now
        ).annotate(rel_count=Count('peers')).exclude(Q(pk=self.pk)).values('rel_count','id','slug','article')[:10]

        # then the related by categories
        by_categories = Story.objects.filter(
            Q(categories__in=list(cats)),
            publish__published=True,
            publish__start__lte=right_now,
            publish__start__gte=long_ago
        ).exclude(Q(pk=self.pk)).annotate(rel_count=Count('categories')).order_by('-rel_count','important').values('rel_count','id','slug','article')[:10]

        combined = list(chain(peers, by_categories))
        return combined

    def visible_categories(self):
        return self.categories.filter(browsable=True)

    def get_absolute_url(self):
        return "/s/{0:>s}".format(self.slug)

    @cached_property
    def latest_publish(self):
        return Publish.objects.filter(story__id=self.pk, published=True).exclude(start__gte=datetime.now()).latest('start')

    @property
    def comments_enabled(self):
        lastest_pub = self.latest_publish

        delta = datetime.now() - lastest_pub.start
        return delta.days < 30

class PublishCategory(models.Model):
    keyname = models.SlugField(max_length = 100, db_index = True)
    title = models.CharField(max_length = 100)
    description = models.TextField(blank = True)
    
    class Meta:
        verbose_name = "Publishing Word"
        verbose_name_plural = "Publishing Words"
        
    def __unicode__(self):
        return u"{0:>s}".format(self.title)
    
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
    sticky = models.BooleanField(default=False, db_index = True)
    order_me = models.PositiveSmallIntegerField(default=0, db_index = True)
    seen = models.BooleanField(default=False, db_index = True)
    # comment handling
    comments = generic.GenericRelation(Comment, object_id_field='object_pk') # reverse generic relation
    # various managers
    objects = models.Manager()
    active = PublishedManager()

    class Meta:
        verbose_name = "Published Story"
        verbose_name_plural = "Published Stories"
        ordering = ('-sticky','order_me','-start')
    
    def __unicode__(self):
        if self.category:
            return u"[{0:>s}] > {1:>s}".format(self.category.title, self.story.article.headline)
        else:
            return u"{0:>s}".format(self.story.article.headline)

    def get_absolute_url(self):
        return "{0:d}/{1:d}/{2:d}/{3:>s}/".format(self.start.year, self.start.month, self.start.day, self.slug)

    @property
    def comments_enabled(self):
        delta = datetime.now() - self.start
        return delta.days < 30

class PublishQueue(Publish):
    class Meta:
        proxy = True
        verbose_name = "Publish Queue"
        verbose_name_plural = "Publish Queue"

class PublishPicking(django_filters.FilterSet):
    start = django_filters.filters.DateRangeFilter(lookup_type=('lt','gt','lte','gte'))
    end = django_filters.filters.DateRangeFilter(name="end", lookup_type=('lt','gt','lte','gte'))
    story__categories = django_filters.filters.ModelMultipleChoiceFilter(queryset=StoryCategory.objects.all(), widget=PickerFilterSelectMultiple("Story Categories",False))  
    
    class Meta:
        model = Publish
        fields = ['site','start','end','category','published','story__categories']

    @staticmethod
    def query_set(qs):
        qs = qs.select_related('thumbnail', 'story_author').distinct()

        return qs


@receiver(post_save, sender=Publish)
def slug_for_publish(sender, instance, created, raw, **kwargs):
    if instance.slug == '' or not instance.slug and None != instance.story:
        # this publish needs a slug
        slugged_headline = slugify(instance.story.article.headline)
        slug = "%d-%s" % (instance.pk, slugged_headline)
        instance.slug = slug[:255]
        instance.save()

@receiver(post_save, sender=PublishQueue)
def slug_for_publish_queue(sender, instance, created, raw, **kwargs):
    if instance.slug == '' or not instance.slug and None != instance.story:
        # this publish needs a slug
        slugged_headline = slugify(instance.story.article.headline)
        slug = "%d-%s" % (instance.pk, slugged_headline)
        instance.slug = slug[:255]
        instance.save()

@receiver(post_save, sender=Story)
def slug_for_story(sender, instance, created, raw, **kwargs):
    if instance.slug == '' or not instance.slug and None != instance.article:
        # this story needs a slug
        slugged_headline = slugify(instance.article.headline)
        slug = "%d-%s" % (instance.pk, slugged_headline)
        instance.slug = slug[:255]
        instance.save()

#moderate publish comments
moderator.register(Story, StoryModerator)

#picking
picker.manifest.register(Publish, PublishPicking)