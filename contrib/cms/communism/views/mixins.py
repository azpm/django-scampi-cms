import logging

from django.views.generic import View, TemplateView
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.http import Http404, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.db.models import Q, Max
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from libscampi.contrib.cms.communism.models import *

import collections, copy

logger = logging.getLogger('libscampi.contrib.cms.communism.views')

class html_link_refs(collections.MutableSet):
    def __init__(self, iterable = None):
        self.elements = lst = []
        if not iterable:
            return None
        try:
            for value in iterable:
                if value not in lst:
                    lst.append(value)
        except TypeError:
            if iterable not in lst:
                lst.append(iterable)
                
    def __iter__(self):
        return iter(self.elements)
        
    def __contains__(self, element):
        return element.file.url in [link_ref.file.url for link_ref in self.elements]
            
    def __len__(self):
        return len(self.elements)
    
    def add(self, element):
        if not self.__contains__(element):
            self.elements.append(element)
    
    def discard(self):
        return ''
    
    def reset(self):
        self.elements = []
        
class SectionMixin(object):
    section = None
    realm = None
    
    def get(self, request, *args, **kwargs):
        logger.debug("SectionMixin.get called")
        logger.debug(request.META.get('HTTP_CACHE_CONTROL', None))
        #get the realm
        site = Site.objects.get_current()
        try:
            self.realm = site.realm
        except Realm.DoesNotExist:
            raise Http404("No Realm Configured")

        #keyname specified in url
        if 'keyname' in kwargs:
            keyname = kwargs.pop('keyname')
            actual = keyname.split('.') #get the actual last commune key: /<parent>.<child>.<desired>/
            logger.debug("requested cms section: %s" % actual)
            
            #self.section = get_object_or_404(Section.localised.select_related(), keyname = actual[-1])
            self.section = get_object_or_404(Section.localised.prefetch_related('element'), keyname = actual[-1])
        else:
            try:
                #we'll see if the section is embedded in the url (it's always the first thing after the domain)
                current_section = request.path.split('/',2)[1]
            except IndexError:
                logger.critical("something bad went wrong with the request, %s" % request.path)
                raise HttpResponseServerError
            
            if current_section != '':
                #section keyname is in the url but not in the view graph/passed args
                #self.section = get_object_or_404(Section.localised.select_related(), keyname = current_section)          
                self.section = get_object_or_404(Section.localised.prefetch_related('element'), keyname = current_section)
            else:
                #no keyname specified, we need the "primary" section
                try:
                    self.section = self.realm.primary_section #get the primary section of this realm
                except ObjectDoesNotExist:
                    raise Http404("No CMS Sections Active")
                    
                if self.section.generates_navigation:
                    #this section has a keyword argument, we should use it
                    return redirect(self.section.element.get_absolute_url())
            
            if not self.section:
                raise Http404("Section Not Found")
                
            
                   
        #finally return the parent get method
        return super(SectionMixin, self).get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        logger.debug("SectionMixin.post called") 
        #get the realm
        site = Site.objects.get_current()
        self.realm = site.realm
        
        #keyname specified in url
        if 'keyname' in kwargs:
            keyname = kwargs.pop('keyname')
            actual = keyname.split('.') #get the actual last commune key: /<parent>.<child>.<desired>/
            logger.debug("requested cms section: %s" % actual)
            
            self.section = get_object_or_404(Section.localised.prefetch_related('element'), keyname = actual[-1])
        else:
            #no keyname specified, we need the "primary" section
            self.section = self.realm.primary_section #get the primary section of this realm
            
            if self.section.generates_navigation:
                #this section has a keyword argument, we should use it
                return redirect(self.section.element.get_absolute_url())
                   
        #finally return the parent get method
        return super(SectionMixin, self).post(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(SectionMixin, self).get_context_data(*args, **kwargs)
        logger.debug("SectionMixin.get_context_data started")
        #set the context commune
        context.update({
            'cms_section': self.section,
            'cms_realm': self.realm,
        })
        logger.debug("SectionMixin.get_context_data ended")
        return context

class CommuneMixin(object):
    commune = None
        
    def get(self, request, *args, **kwargs):
        logger.debug("CommuneMixin.get called") 
        self.commune = self.section.element
        
        #finally return the parent get method
        return super(CommuneMixin, self).get(request, *args, **kwargs)

    #overrides base page title functionality
    def get_page_title(self):
        return "%s | %s" % (self.realm.name, self.commune.name)

    def get_template_names(self):
        tpl_list = (
            "%s/communism/%s/%s.html" % (self.commune.theme.keyname, self.realm.keyname, self.section.keyname),
            "%s/communism/%s/commune.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/communism/commune.html" % self.commune.theme.keyname,
        )
        
        return tpl_list 
    
    def get_context_data(self, *args, **kwargs):
        context = super(CommuneMixin, self).get_context_data(*args, **kwargs)
        logger.debug("CommuneMix.get_context_data started")
        #set the context commune
        context.update({
            'cms_commune': self.commune,
        })
        logger.debug("CommuneMixin.get_context_data ended")
        return context
    
class CSSMixin(object):
    def get_stylesheets(self):
        theme = self.get_theme()
        logger.debug("CSSMixin.get_stylesheets called")
        
        #try to get the cached css for this commune
        cached_css_key = 'commune:css:%s' % self.commune.pk
        if self.request.GET.get('refresh_cache', False):
            #invalidate on refresh_cache
            cache.delete(cached_css_key)
        styles = cache.get(cached_css_key, None)
        
        #cache empty, get the styles and refill the cache
        if not styles:
            logger.debug("missed css cache on %s" % cached_css_key)
            styles = StyleSheet.objects.filter(active=True).filter(
                Q(pickertemplate__dynamicpicker__namedbox__slice__commune=self.commune) & 
                Q(pickertemplate__dynamicpicker__namedbox__active=True) | 
                Q(staticpicker__namedbox__slice__commune=self.commune) &
                Q(staticpicker__namedbox__active=True) |
                Q(base=True),
                Q(theme__pk=theme.id)
            ).order_by('precedence')
            cache.set(cached_css_key, styles, 60*20)
           
        #build a simple collection of styles
        css_collection = html_link_refs()
        for style in styles:
            css_collection.add(style)
            
        return css_collection

    def get_context_data(self, *args, **kwargs):
        #get the existing context
        context = super(CSSMixin, self).get_context_data(*args, **kwargs)
        logger.debug("CSSMixin.get_context_data started")
        css = self.get_stylesheets()
        
        #add the collection to the context
        if 'cms_page' in context:
            context['cms_page'].update({
                'styles': css,
            })
        else:
            context.update({
                'cms_page': {
                    'styles': css,
                }
            })
        logger.debug("CSSMixin.get_context_data ended")
        return context
    
class JScriptMixin(object):
    def get_javascripts(self):
        theme = self.get_theme()
        
        logger.debug("JScriptMixin.get_javascripts called")
        #try to get the cached javascript for this commune
        cached_scripts_key = 'commune:scripts:%s' % self.commune.pk
        if self.request.GET.get('refresh_cache', False):
            #invalidate on refresh_cache
            cache.delete(cached_scripts_key)
        script_ids = cache.get(cached_scripts_key, None)

        #build a simple collection of styles
        script_collection = html_link_refs()

        #cache empty, get the scripts and refill the cache
        if not script_ids:
            logger.debug("missed css cache on %s" % cached_scripts_key)
            scripts = Javascript.objects.filter(active=True).filter(
                Q(pickertemplate__dynamicpicker__namedbox__slice__commune=self.commune) & 
                Q(pickertemplate__dynamicpicker__namedbox__active=True) | 
                Q(staticpicker__namedbox__slice__commune=self.commune) &
                Q(staticpicker__namedbox__active=True) |
                Q(base=True),
                Q(theme__pk=theme.id)
            ).order_by('precedence')
            cache.set(cached_scripts_key, scripts.values_list('id', flat = True), 60*20)

        else:
            scripts = Javascript.objects.filter(id__in=script_ids).order_by('precedence')

        for script in scripts:
            script_collection.add(script)

        return script_collection

    def get_context_data(self, *args, **kwargs):
        #get the existing context
        context = super(JScriptMixin, self).get_context_data(*args, **kwargs)
        logger.debug("JScriptMixin.get_context_data started")
        js = self.get_javascripts()
        
        #add the collection to the context
        if 'cms_page' in context:
            context['cms_page'].update({
                'scripts': js,
            })
        else:
            context.update({
                'cms_page': {
                    'scripts': js,
                }
            })
        logger.debug("JScript.get_context_data ended")    
        return context
        
class ThemeMixin(object):
    def get_theme(self):
        logger.debug("ThemeMixin.get_theme called")
        return self.commune.theme

    def get_context_data(self, *args, **kwargs):
        context = super(ThemeMixin, self).get_context_data(*args, **kwargs)
        
        if 'cms_page' in context:
            context['cms_page'].update({
                'theme': self.get_theme()
            })
        else:
            context.update({
                'cms_page': {
                    'theme': self.get_theme(),
                }
            })
        logger.debug("ThemeMixin.get_context_data ended")
        return context