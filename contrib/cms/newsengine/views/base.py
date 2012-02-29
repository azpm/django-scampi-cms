import logging
from django.views.generic.dates import *
from django.db.models import Q, Max, Avg, Sum
from django.core.cache import cache

from libscampi.contrib.cms.communism.models import Javascript, StyleSheet
from libscampi.contrib.cms.communism.views.mixins import html_link_refs
from libscampi.contrib.cms.views.base import CMSPageNoView
from libscampi.contrib.cms.conduit.views.mixins import PickerMixin
from libscampi.contrib.cms.newsengine.models import StoryCategory

from .mixins import PublishStoryMixin

logger = logging.getLogger('libscampi.contrib.cms.newsengine.views')

class NewsEngineArchivePage(PublishStoryMixin, CMSPageNoView, PickerMixin):
    limits = None
    available_categories = None
    
    def get(self, request, *args, **kwargs):    
        logger.debug("NewsEngineArchivePage.get called")
        
        #keyname specified in url
        if 'c' in request.GET:
            limits = request.GET.get('c','').split(' ')
            logger.debug(limits)
            
            filters = [Q(keyname=value) for value in limits]
            query = filters.pop()            
            # Or the Q object with the ones remaining in the list
            for filter in filters:
                query |= filter
            
            self.limits = StoryCategory.objects.filter(Q(browsable=True) & query)
            
        #finally return the parent get method
        return super(NewsEngineArchivePage, self).get(request, *args, **kwargs)
    
    
    """
    Base page for newsengine archives
    
    provides the picker-pruned initial queryset
    """
    def get_queryset(self):        
        qs = self.model.objects.distinct().select_related().all()
        
        """
        this is a hardcoded "hack"
        
        the newsengine publish stories are displayed, by way of the CMS through
        dynamic pickers. Without having time to write a robust "archive" feature
        for dynamic pickers, we conclude that because contrib.CMS is not editable
        the Picking Filterset for Publish (published stories) is immutable and
        'start', 'end', 'end__isnull' are known keys of things we DON'T want to
        filter by for the archives.
        
        We do this because the archives themselves will exclude things that
        haven't been published yet, and will always show expired stories.
        """
        exclude_these = ('start', 'end', 'end__isnull')
        
        #loop over the inclusion filters and update the qs
        if self.picker.include_filters:
            if isinstance(self.picker.include_filters, list):
                for f in self.picker.include_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) #this strips anything we dont want
                    qs = qs.filter(**f)
            else:
                logger.critical("invalid picker: cannot build archives from picker %s [id: %d]" % (self.picker.name, self.picker.id))
                
        
        if self.picker.exclude_filters:
            if isinstance(self.picker.include_filters, list):
                for f in self.picker.exclude_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) #strips unneeded filters
                    qs = qs.exclude(**f)
            else:
                logger.critical("invalid picker: cannot build archives from picker %s [id: %d]" % (self.picker.name, self.picker.id))
        
        #cat_cache_key = "picker:avail:categories:%d" % self.picker.id
        #categories = cache.get(cat_cache_key, None)
        
        #if not categories:
        categories = StoryCategory.genera.for_cloud(qs).exclude(pk__in=self.base_categories)
        #    cache.set(cat_cache_key, categories, 60*60)
            
        if self.limits:
            filters = [Q(story__categories__pk=value[0]) for value in self.limits.values_list('id')]
            for filter in filters:
                qs = qs.filter(filter)
                
            self.available_categories = categories.exclude(pk__in=self.limits.values_list('id'))
        else:
            self.available_categories = categories
        
        return qs
                
    def get_context_data(self, *args, **kwargs):
        logger.debug("NewsEngineArchivePage.get_context_data started")
        #get the existing context
        context = super(NewsEngineArchivePage, self).get_context_data(*args, **kwargs)
        
        if self.limits:
            get_args = u"c=%s" % "+".join([t.keyname for t in self.limits])
        else:
            get_args = None
        
        #give the template the current picker
        context.update({'categories': self.available_categories, 'limits': self.limits, 'get_args': get_args})
        logger.debug("NewsEngineArchivePage.get_context_data ended")
        return context


class PickedStoryIndex(NewsEngineArchivePage, ArchiveIndexView):
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/index.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/index.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/index.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/index.html" % self.commune.theme.keyname,
        )
        
        return tpl_list
    

class PickedStoryYearArchive(NewsEngineArchivePage, YearArchiveView):
    make_object_list = True
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/year.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/year.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/year.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/year.html" % self.commune.theme.keyname,
        )
        
        return tpl_list

class PickedStoryMonthArchive(NewsEngineArchivePage, MonthArchiveView):
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/month.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/month.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/month.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/month.html" % self.commune.theme.keyname,
        )
        
        return tpl_list

class PickedStoryDayArchive(NewsEngineArchivePage, DayArchiveView):
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/day.html" % self.commune.theme.keyname,
        )
        
        return tpl_list
    
class PickerStoryTodayArchive(NewsEngineArchivePage, TodayArchiveView):  
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/today.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/today.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/today.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/today.html" % self.commune.theme.keyname,
            "%s/newsengine/archive/day.html" % self.commune.theme.keyname,
        )
        
        return tpl_list
    
class PickedStoryDetailArchive(NewsEngineArchivePage, DateDetailView):
    def get_stylesheets(self):
        
        publish = self.object
        story = publish.story
        article = story.article
        theme = self.get_theme()
                
        #try to get the cached css for this published story
        cached_css_key = 'picker:%d:publish:css:%s' % (self.picker.id, publish.id)
        if self.request.GET.get('refresh_cache', False):
            #invalidate on refresh_cache
            cache.delete(cached_css_key)
        styles = cache.get(cached_css_key, None)
        
        #cache empty, get the styles and refill the cache
        if not styles:
            logger.debug("missed css cache on %s" % cached_css_key)
            styles = StyleSheet.objects.filter(active=True).filter(
                #playlist finders
                Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id) |
                Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id) |
                Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id) |
                Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id) |
                Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id) |
                #inline finders
                Q(mediainlinetemplate__videotype__video__id__in=article.video_inlines.values_list('id')) |
                Q(mediainlinetemplate__imagetype__image__id__in=article.image_inlines.values_list('id')) |
                Q(mediainlinetemplate__audiotype__audio__id__in=article.audio_inlines.values_list('id')) |
                Q(mediainlinetemplate__documenttype__document__id__in=article.document_inlines.values_list('id')) |
                Q(mediainlinetemplate__objecttype__object__id__in=article.object_inlines.values_list('id')) |
                #always include base
                Q(base=True),
                #force to the current theme
                Q(theme__id=theme.id)
            ).order_by('precedence')
            logger.debug("stylsheet sql: %s" % styles.query)
            cache.set(cached_css_key, styles, 60*10)
           
        #build a simple collection of styles
        css_collection = html_link_refs()
        for style in styles:
            css_collection.add(style)
            
        return css_collection

    def get_javascripts(self):
        publish = self.object
        story = publish.story
        article = story.article
        theme = self.get_theme()
        
        #try to get the cached javascript for this published story
        cached_scripts_key = 'picker:%d:publish:js:%s' % (self.picker.id, publish.id)
        if self.request.GET.get('refresh_cache', False):
            #invalidate on refresh_cache
            cache.delete(cached_scripts_key)
        scripts = cache.get(cached_scripts_key, None)
        
        #cache empty, get the scripts and refill the cache
        if not scripts:
            logger.debug("missed css cache on %s" % cached_scripts_key)
            scripts = Javascript.objects.filter(active=True).filter(
                #playlist finders
                Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id) |
                Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id) |
                Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id) |
                Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id) |
                Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id) |
                #inline finders
                Q(mediainlinetemplate__videotype__video__id__in=article.video_inlines.values_list('id')) |
                Q(mediainlinetemplate__imagetype__image__id__in=article.image_inlines.values_list('id')) |
                Q(mediainlinetemplate__audiotype__audio__id__in=article.audio_inlines.values_list('id')) |
                Q(mediainlinetemplate__documenttype__document__id__in=article.document_inlines.values_list('id')) |
                Q(mediainlinetemplate__objecttype__object__id__in=article.object_inlines.values_list('id')) |
                #always include base
                Q(base=True),
                #force to the current theme
                Q(theme__id=theme.id)
            ).order_by('precedence')
            logger.debug("scripts sql: %s" % scripts.query)
            cache.set(cached_scripts_key, scripts, 60*20)
                       
        #build a simple collection of styles
        script_collection = html_link_refs()
        for script in scripts:
            script_collection.add(script)
        
        return script_collection    
    
    def get_template_names(self):
    
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/%s.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname, self.object.slug),
            "%s/newsengine/archive/%s/%s/%s/detail.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/detail.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/detail.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/detail.html" % self.commune.theme.keyname,
        )
        
        return tpl_list