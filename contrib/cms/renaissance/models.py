# -*- coding: utf-8 -*
import mimetypes
import os
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from taggit.managers import TaggableManager

#Local Imports
from libscampi.contrib.cms.renaissance import settings as local_settings
from libscampi.contrib.cms.renaissance.validation import ValidImgExtension, ValidVidExtension, ValidDocExtension, ValidAudExtension, ValidObjExtension

# Patch mimetypes w/ any extra types
mimetypes.types_map.update(local_settings.EXTRA_MIME_TYPES)

__all__ = [
    'MediaInlineTemplate', 'MediaPlaylistTemplate',
    'ImageType', 'VideoType', 'AudioType', 'DocumentType', 'ObjectType',
    'Image', 'Video', 'Audio', 'Document', 'Object', 'External',
    'RankedImage', 'RankedVideo', 'RankedAudio', 'RankedDocument', 'RankedObject',
    'ImagePlaylist', 'VideoPlaylist', 'AudioPlaylist', 'DocumentPlaylist', 'ObjectPlaylist'
]

class MediaInlineTemplate(models.Model):
    title = models.CharField(max_length = 25)
    description = models.TextField(null = True, blank = True)
    content = models.TextField()
    
    stylesheet = models.ManyToManyField('communism.StyleSheet', blank = True)
    javascript = models.ManyToManyField('communism.Javascript', blank = True)
    
    def __unicode__(self):
        return "%s" % self.title
    class Meta:
        verbose_name = 'Template (Inline)'
        verbose_name_plural = 'Templates (Inline)'

class MediaPlaylistTemplate(models.Model):
    title = models.CharField(max_length = 25)
    description = models.TextField(null = True, blank = True)
    
    stylesheet = models.ForeignKey('communism.StyleSheet', null = True, blank = True)
    javascript = models.ForeignKey('communism.Javascript', null = True, blank = True)
    
    content = models.TextField()
    
    def __unicode__(self):
        return "%s" % self.title
    class Meta:
        verbose_name = 'Template (Playlist)'
        verbose_name_plural = 'Templates (Playlist)'

class MediaType(models.Model):
    title = models.CharField(max_length=255)
    keyname = models.SlugField(max_length=20, unique = True)
    description = models.TextField(null = True, blank = True)
    inline_template = models.ForeignKey(MediaInlineTemplate, verbose_name = "Media Inline-Template", db_column="template_id") #this is a bit of a fuckup because we added the other template
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        if hasattr(self,'width') and  hasattr(self,'height'):
            width = getattr(self,'width', None)
            height = getattr(self,'height', None)
            
            if width & height:
                return u"{0:>s} [{1:d} x {2:d}]".format(self.title, width, height)
    
        return "%s" % self.title 

class ImageType(MediaType):
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = 'Image Type'
        verbose_name_plural = 'Image Types'
    
class VideoType(MediaType):
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    class Meta:
        verbose_name = 'Video Type'
        verbose_name_plural = 'Video Types'
    
class AudioType(MediaType):
    class Meta:
        verbose_name = 'Audio Type'
        verbose_name_plural = 'Audio Types'

class DocumentType(MediaType):
    class Meta:
        verbose_name = 'Document Type'
        verbose_name_plural = 'Document Types'
    
class ObjectType(MediaType):
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    class Meta:
        verbose_name = 'HTML Object Type'
        verbose_name_plural = 'HTML Object Types'
        
class Media(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    caption = models.TextField(blank=True)
    
    author = models.ForeignKey(User, limit_choices_to={'is_staff':True}, blank = True, null = True)
    creation_date = models.DateTimeField(auto_now_add=True)    
    credit = models.CharField(max_length=150, blank=True)
    reproduction_allowed = models.BooleanField("we have reproduction rights for this media", default=True)
    modified = models.DateTimeField(auto_now=True)
    
    mime_type = models.CharField(max_length=150, blank=True)
    tags = TaggableManager(blank=True)
    
    class Meta:
        ordering = ['-creation_date']
        abstract = True
        
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        if hasattr(self,'file') and getattr(self,'file',None):
            return self.file.url
        return ''
    
    def save(self, *args, **kwargs):
        if hasattr(self,'file') and getattr(self,'file', None) and not self.mime_type:
            self.mime_type = mimetypes.guess_type(self.file.path)[0]
            
        super(Media, self).save(*args, **kwargs)

    def __unicode__(self):
        return "{0:>s}".format(self.title)

def _file_upload_pathing(cls, fname):
    now = datetime.datetime.now()
    
    file, ext = os.path.splitext(fname)
    
    #fname = re.sub(r'\s','', fname) #strip all whitespace chars from file
    name = slugify(file)
    
    return "master/{0:>s}/{1:d}/{2:d}/{3:d}/{4:>s}/{5:>s}{6:>s}".format(cls.base_type, now.year, now.month, now.day,
        cls.type.keyname, name, ext)

class Image(Media):
    file = models.ImageField(upload_to=_file_upload_pathing, validators=[ValidImgExtension()])
    type = models.ForeignKey(ImageType)
    
    class Meta:
        verbose_name = "Image File"
        verbose_name_plural = "Image Files"
        
    base_type = "image"
                
class Video(Media):
    file = models.FileField(upload_to=_file_upload_pathing, validators=[ValidVidExtension()])
    type = models.ForeignKey(VideoType)
    thumbnail = models.ForeignKey(Image, null = True)
        
    class Meta:
        verbose_name = "Video File"
        verbose_name_plural = "Video Files"
        
    base_type = "video"

class Audio(Media):
    file = models.FileField(upload_to=_file_upload_pathing, validators=[ValidAudExtension()])
    type = models.ForeignKey(AudioType)
        
    class Meta:
        verbose_name = "Audio File"
        verbose_name_plural = "Audio Files"
        
    base_type = "audio"

class Document(Media):
    file = models.FileField(upload_to=_file_upload_pathing, validators=[ValidDocExtension()])
    type = models.ForeignKey(DocumentType)
    
    class Meta:
        verbose_name = "Document File"
        verbose_name_plural = "Document Files"

    base_type = "document"
    
class Object(Media):
    file = models.FileField(upload_to=_file_upload_pathing, validators=[ValidObjExtension()])
    type = models.ForeignKey(ObjectType)
    
    class Meta:
        verbose_name = "HTML Object File"
        verbose_name_plural = "HTML Object Files"
        
    base_type = "object"
        
class External(Media):
    data = models.TextField()
    
    class Meta:
        verbose_name = "External Embed"
        verbose_name_plural = "External Embeds"
        
    base_type = "external"
    
class RankedImage(models.Model):
    rank = models.PositiveIntegerField()
    image = models.ForeignKey(Image)
    playlist = models.ForeignKey('ImagePlaylist')
    class Meta:
        ordering = ['rank']
        verbose_name = 'Ranked Image'
        verbose_name_plural = 'Ranked Images'
        
class RankedVideo(models.Model):
    rank = models.PositiveIntegerField()
    video = models.ForeignKey(Video)
    playlist = models.ForeignKey('VideoPlaylist')
    class Meta:
        ordering = ['rank']
        verbose_name = 'Ranked Video'
        verbose_name_plural = 'Ranked Videos'
        
class RankedAudio(models.Model):
    rank = models.PositiveIntegerField()
    audio = models.ForeignKey(Audio)
    playlist = models.ForeignKey('AudioPlaylist')
    class Meta:
        ordering = ['rank']
        verbose_name = 'Ranked Audio'
        verbose_name_plural = 'Ranked Audios'
        
class RankedDocument(models.Model):
    rank = models.PositiveIntegerField()
    document = models.ForeignKey(Document)
    playlist = models.ForeignKey('DocumentPlaylist')
    class Meta:
        ordering = ['rank']
        verbose_name = 'Ranked Document'
        verbose_name_plural = 'Ranked Documents'
        
class RankedObject(models.Model): 
    rank = models.PositiveIntegerField()
    object = models.ForeignKey(Object)
    playlist = models.ForeignKey('ObjectPlaylist')
    class Meta:
        ordering = ['rank']
        verbose_name = 'Ranked Object'
        verbose_name_plural = 'Ranked Objects'
    
class MediaPlaylist(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    caption = models.TextField(blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)    
    modified = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)
    template = models.ForeignKey(MediaPlaylistTemplate)
    
    class Meta:
        ordering = ('-creation_date',)
        abstract = True
        
    def __unicode__(self):
        return self.title
        
class ImagePlaylist(MediaPlaylist):
    collection = models.ManyToManyField(Image, through=RankedImage)
    class Meta:
        verbose_name = 'Image Playlist'
        verbose_name_plural = 'Image Playlists'

class VideoPlaylist(MediaPlaylist):
    collection = models.ManyToManyField(Video, through=RankedVideo)
    class Meta:
        verbose_name = 'Video Playlist'
        verbose_name_plural = 'Video Playlists'
        
class AudioPlaylist(MediaPlaylist):
    collection = models.ManyToManyField(Audio, through=RankedAudio)
    class Meta:
        verbose_name = 'Audio Playlist'
        verbose_name_plural = 'Audio Playlists'
    
class DocumentPlaylist(MediaPlaylist):
    collection = models.ManyToManyField(Document, through=RankedDocument)
    class Meta:
        verbose_name = 'Document Playlist'
        verbose_name_plural = 'Document Playlists'
        
class ObjectPlaylist(MediaPlaylist):
    collection = models.ManyToManyField(Object, through=RankedObject)
    class Meta:
        verbose_name = 'HTML Object Playlist'
        verbose_name_plural = 'HTML Object Playlists'
