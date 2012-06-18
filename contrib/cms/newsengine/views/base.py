import logging
from datetime import datetime

from django.views.generic.dates import *
from django.views.generic import DetailView
from django.db.models import Q
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site

from libscampi.contrib.cms.communism.models import Javascript, StyleSheet
from libscampi.contrib.cms.communism.views.mixins import html_link_refs
from libscampi.contrib.cms.views.base import CMSPageNoView, PageNoView
from libscampi.contrib.cms.conduit.views.mixins import PickerMixin
from libscampi.contrib.cms.newsengine.models import StoryCategory
from libscampi.utils.dating import date_from_string, date_lookup_for_field

from .mixins import PublishStoryMixin, StoryMixin

logger = logging.getLogger('libscampi.contrib.cms.newsengine.views')

class NewsEngineArchivePage(PublishStoryMixin, PickerMixin, CMSPageNoView):
    """
    Base page for newsengine archives

    provides the picker-pruned initial queryset
    """

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

    def get_queryset(self):
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
        qs = self.model.objects.distinct()
        

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
                logger.critical(
                    "invalid picker: cannot build archives from picker {0:>s} [id: {1:d}]".format(self.picker.name,
                        self.picker.id))
                
        
        if self.picker.exclude_filters:
            if isinstance(self.picker.include_filters, list):
                for f in self.picker.exclude_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) #strips unneeded filters
                    qs = qs.exclude(**f)
            else:
                logger.critical(
                    "invalid picker: cannot build archives from picker {0:>s} [id: {1:d}]".format(self.picker.name,
                        self.picker.id))
        
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

    def get_page_title(self):
        return "more %s" % self.picker.name

class PickedStoryIndex(NewsEngineArchivePage, ArchiveIndexView):
    def get_page_title(self):
        return "%s, Archive - %s" % (self.picker.name, self.picker.commune.name)


    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/index.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/index.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/index.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/index.html".format(self.commune.theme.keyname),
        )
        
        return tpl_list
    

class PickedStoryYearArchive(NewsEngineArchivePage, YearArchiveView):
    make_object_list = True

    def get_page_title(self):
        return "{0:>s}, Archive {1:>s} - {2:>s}".format(self.picker.name, self.get_year(), self.picker.commune.name)

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/year.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/year.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/year.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/year.html".format(self.commune.theme.keyname),
        )
        
        return tpl_list

class PickedStoryMonthArchive(NewsEngineArchivePage, MonthArchiveView):
    def get_page_title(self):
        return "{0:>s}, Archive {1:>s}/{2:>s} - {3:>s}".format(self.picker.name, self.get_month(), self.get_year(), self.picker.commune.name)

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/month.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/month.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/month.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/month.html".format(self.commune.theme.keyname),
        )
        
        return tpl_list

class PickedStoryDayArchive(NewsEngineArchivePage, DayArchiveView):
    def get_page_title(self):
        return "{0:>s}, Archive {1:>s}/{2:>s}/{3:>s} - {4:>s}".format(self.picker.name, self.get_day(), self.get_month(), self.get_year(), self.picker.commune.name)

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/day.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/day.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/day.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/day.html".format(self.commune.theme.keyname),
        )
        
        return tpl_list
    
class PickerStoryTodayArchive(NewsEngineArchivePage, TodayArchiveView):
    def get_page_title(self):
        return "{0:>s}, Archive {1:>s}/{2:>s}/{3:>s} - {4:>s}".format(self.picker.name, self.get_day(), self.get_month(), self.get_year(), self.picker.commune.name)

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/today.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/day.html".format(self.commune.theme.keyname,self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/today.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/day.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/today.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/day.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/today.html".format(self.commune.theme.keyname),
            "{0:>s}/newsengine/archive/day.html".format(self.commune.theme.keyname),
        )
        
        return tpl_list
    
class PickedStoryDetailArchive(NewsEngineArchivePage, DateDetailView):
    def get_page_title(self):
        return "%s" % self.object.story.article.headline

    def get_stylesheets(self):
        publish = self.object
        story = publish.story
        article = story.article
        theme = self.get_theme()
                
        #try to get the cached css for this published story
        cached_css_key = 'theme:{0:d}:story:css:{1:d}'.format(story.id, theme.id)
        if self.refresh_caches:
            #invalidate on refresh_cache
            cache.delete(cached_css_key)
        styles = cache.get(cached_css_key, None)
        
        #cache empty, get the styles and refill the cache
        if not styles:
            logger.debug("missed css cache on {0:>s}".format(cached_css_key))
            
            playlist_filters = Q(base = True)
            
            if story.video_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id)
            
            if story.image_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id)
                
            if story.audio_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id)
                
            if story.document_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id)
                
            if story.object_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id)
                                  
            styles = StyleSheet.objects.filter(active=True, theme__id=theme.id).filter(
                #playlist finders
                playlist_filters | 
                #inline finders
                Q(mediainlinetemplate__videotype__video__id__in=article.video_inlines.values_list('id')) |
                Q(mediainlinetemplate__imagetype__image__id__in=article.image_inlines.values_list('id')) |
                Q(mediainlinetemplate__audiotype__audio__id__in=article.audio_inlines.values_list('id')) |
                Q(mediainlinetemplate__documenttype__document__id__in=article.document_inlines.values_list('id')) |
                Q(mediainlinetemplate__objecttype__object__id__in=article.object_inlines.values_list('id'))
            ).order_by('precedence').distinct()
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
        cached_scripts_key = 'theme:{0:d}:story:js:{1:d}'.format(story.id, theme.id)
        if self.refresh_caches:
            #invalidate on refresh_cache
            cache.delete(cached_scripts_key)
        script_ids = cache.get(cached_scripts_key, None)
        
        #cache empty, get the scripts and refill the cache
        if not script_ids:
            logger.debug("missed css cache on {0:>s}".format(cached_scripts_key))
            
            playlist_filters = Q(base = True)
            
            if story.video_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id)
            
            if story.image_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id)
                
            if story.audio_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id)
                
            if story.document_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id)
                
            if story.object_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id)
            
            scripts = Javascript.objects.filter(active=True, theme__id=theme.id).filter(
                playlist_filters |
                #inline finders
                Q(mediainlinetemplate__videotype__video__id__in=article.video_inlines.values_list('id')) |
                Q(mediainlinetemplate__imagetype__image__id__in=article.image_inlines.values_list('id')) |
                Q(mediainlinetemplate__audiotype__audio__id__in=article.audio_inlines.values_list('id')) |
                Q(mediainlinetemplate__documenttype__document__id__in=article.document_inlines.values_list('id')) |
                Q(mediainlinetemplate__objecttype__object__id__in=article.object_inlines.values_list('id'))
            ).order_by('precedence').distinct()
            cache.set(cached_scripts_key, list(scripts.values_list('id', flat = True)), 60*20)
        else:
            scripts = Javascript.objects.filter(id__in=script_ids).order_by('precedence')
                       
        #build a simple collection of styles
        script_collection = html_link_refs()
        for script in scripts:
            script_collection.add(script)
        
        return script_collection    
    
    def get_template_names(self):
    
        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/{4:>s}.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname, self.object.slug),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/{3:>s}/detail.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/{2:>s}/detail.html".format(self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "{0:>s}/newsengine/archive/{1:>s}/detail.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/detail.html".format(self.commune.theme.keyname),
        )
        
        return tpl_list

class RelatedStoryDetailView(PickedStoryDetailArchive):
    """
    Overrides get_object to allow related object that exists outside of current picker context
    """

    def get_object(self, queryset=None):
        """
        Get the object this request displays.
        """
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = date_from_string(year, self.get_year_format(),
            month, self.get_month_format(),
            day, self.get_day_format())

        qs = self.model.objects.distinct()

        if not self.get_allow_future() and date > datetime.date.today():
            raise Http404(_(u"Future %(verbose_name_plural)s not available because %(class_name)s.allow_future is False.") % {
                'verbose_name_plural': qs.model._meta.verbose_name_plural,
                'class_name': self.__class__.__name__,
                })

        # Filter down a queryset from self.queryset using the date from the URL
        date_field = self.get_date_field()
        field = qs.model._meta.get_field(date_field)
        lookup = date_lookup_for_field(field, date)
        qs = qs.filter(**lookup)

        slug = self.kwargs.get(self.slug_url_kwarg, None)
        if slug is not None:
            slug_field = self.get_slug_field()
            qs = qs.filter(**{slug_field: slug})
        else:
            raise AttributeError(u"RelatedStoryDetailView must be called with "
                                 u"either an object pk or a slug.")

        # actually grab the published story
        try:
            obj = qs.get()
        except self.model.DoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        except self.model.MultipleObjectsReturned:
            try:
                obj = qs[0]
            except IndexError:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                              {'verbose_name': queryset.model._meta.verbose_name})
        return obj

class StoryDetail(StoryMixin, PageNoView, DetailView):
    """
    Raw Story Detail
    """
    theme = None

    def get_page_title(self):
        return "%s" % self.object.story.article.headline

    def get(self, request, *args, **kwargs):
        logger.debug("StoryDetail.get called")

        try:
            realm = Site.objects.get_current().realm
        except (AttributeError, ObjectDoesNotExist):
            raise Http404("SCAMPI Improperly Configured, no Realm available.")
        else:
            self.theme = realm.theme

        #add section to the graph by way of the picker
        kwargs.update(dict(keyname="__un_managed"))

        #finally return the parent get method
        return super(StoryDetail, self).get(request, *args, **kwargs)

    def get_stylesheets(self):
        story = self.object
        article = story.article
        theme = self.theme

        #try to get the cached css for this published story
        cached_css_key = 'theme:{0:d}:story:css:{1:d}'.format(story.id, theme.id)
        if self.refresh_caches:
            #invalidate on refresh_cache
            cache.delete(cached_css_key)
        styles = cache.get(cached_css_key, None)

        #cache empty, get the styles and refill the cache
        if not styles:
            logger.debug("missed css cache on {0:>s}".format(cached_css_key))

            playlist_filters = Q(base = True)

            if story.video_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id)

            if story.image_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id)

            if story.audio_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id)

            if story.document_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id)

            if story.object_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id)

            styles = StyleSheet.objects.filter(active=True, theme__id=theme.id).filter(
                #playlist finders
                playlist_filters |
                #inline finders
                Q(mediainlinetemplate__videotype__video__id__in=article.video_inlines.values_list('id')) |
                Q(mediainlinetemplate__imagetype__image__id__in=article.image_inlines.values_list('id')) |
                Q(mediainlinetemplate__audiotype__audio__id__in=article.audio_inlines.values_list('id')) |
                Q(mediainlinetemplate__documenttype__document__id__in=article.document_inlines.values_list('id')) |
                Q(mediainlinetemplate__objecttype__object__id__in=article.object_inlines.values_list('id'))
            ).order_by('precedence').distinct()
            cache.set(cached_css_key, styles, 60*10)

        #build a simple collection of styles
        css_collection = html_link_refs()
        for style in styles:
            css_collection.add(style)

        return css_collection

    def get_javascripts(self):
        story = self.object
        article = story.article
        theme = self.theme

        #try to get the cached javascript for this published story
        cached_scripts_key = 'theme:{0:d}:story:js:{1:d}'.format(story.id, theme.id)
        if self.refresh_caches:
            #invalidate on refresh_cache
            cache.delete(cached_scripts_key)
        script_ids = cache.get(cached_scripts_key, None)

        #cache empty, get the scripts and refill the cache
        if not script_ids:
            logger.debug("missed css cache on {0:>s}".format(cached_scripts_key))

            playlist_filters = Q(base = True)

            if story.video_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id)

            if story.image_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id)

            if story.audio_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id)

            if story.document_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id)

            if story.object_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id)

            scripts = Javascript.objects.filter(active=True, theme__id=theme.id).filter(
                playlist_filters |
                #inline finders
                Q(mediainlinetemplate__videotype__video__id__in=article.video_inlines.values_list('id')) |
                Q(mediainlinetemplate__imagetype__image__id__in=article.image_inlines.values_list('id')) |
                Q(mediainlinetemplate__audiotype__audio__id__in=article.audio_inlines.values_list('id')) |
                Q(mediainlinetemplate__documenttype__document__id__in=article.document_inlines.values_list('id')) |
                Q(mediainlinetemplate__objecttype__object__id__in=article.object_inlines.values_list('id'))
            ).order_by('precedence').distinct()
            cache.set(cached_scripts_key, list(scripts.values_list('id', flat = True)), 60*20)
        else:
            scripts = Javascript.objects.filter(id__in=script_ids).order_by('precedence')

        #build a simple collection of styles
        script_collection = html_link_refs()
        for script in scripts:
            script_collection.add(script)

        return script_collection

    def get_template_names(self):

        tpl_list = (
            "{0:>s}/newsengine/archive/{1:>s}/detail.html".format(self.theme.keyname, self.realm.keyname),
            "{0:>s}/newsengine/archive/detail.html".format(self.theme.keyname),
            )

        return tpl_list
