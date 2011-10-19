from django.views.generic import View, TemplateView
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.http import Http404, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.db.models import Q, Max
from django.core.cache import cache

from libscampi.contrib.cms.communism.models import *

import collections, copy

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
    
class CSSMixin(object):
    def get_stylesheets(self):
        #try to get the cached css for this commune
        cached_css_key = 'commune_css_%s' % self.commune.pk
        styles = cache.get(cached_css_key, None)
        
        #cache empty, get the styles and refill the cache
        if not styles:
            styles = StyleSheet.objects.filter(active=True).filter(
                Q(pickertemplate__dynamicpicker__namedbox__slice__commune=self.commune) & 
                Q(pickertemplate__dynamicpicker__namedbox__active=True) | 
                Q(base=True)
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
        
        css = self.get_stylesheets()
        
        #add the collection to the context
        if 'page' in context:
            context['page'].update({
                'styles': css,
            })
        else:
            context.update({
                'page': {
                    'styles': css,
                }
            })
            
        return context
    
class JScriptMixin(object):
    def get_javascripts(self):
        #try to get the cached javascript for this commune
        cached_scripts_key = 'commune_scripts_%s' % self.commune.pk
        scripts = cache.get(cached_scripts_key, None)
        
        #cache empty, get the scripts and refill the cache
        if not scripts:
            scripts = Javascript.objects.filter(active=True).filter(
                Q(pickertemplate__dynamicpicker__namedbox__slice__commune=self.commune) & 
                Q(pickertemplate__dynamicpicker__namedbox__active=True) | 
                Q(base=True)
            ).order_by('precedence')
            cache.set(cached_scripts_key, scripts, 60*20)
           
        #build a simple collection of styles
        script_collection = html_link_refs()
        for script in scripts:
            script_collection.add(script)
        
        return script_collection

    def get_context_data(self, *args, **kwargs):
        #get the existing context
        context = super(JScriptMixin, self).get_context_data(*args, **kwargs)
        
        js = self.get_javascripts()
        
        #add the collection to the context
        if 'page' in context:
            context['page'].update({
                'scripts': js,
            })
        else:
            context.update({
                'page': {
                    'scripts': js,
                }
            })
            
        return context
        
class ThemeMixin(object):
    theme = None
    
    def get_context_data(self, *args, **kwargs):
        context = super(ThemeMixin, self).get_context_data(*args, **kwargs)
        
        if 'page' in context:
            context['page'].update({
                'theme': self.commune.theme,
            })
        else:
            context.update({
                'page': {
                    'theme': self.commune.theme,
                }
            })
            
        return context
        
class CommuneMixin(object):
    commune = None
    section = None
    realm = None
    
    def get(self, request, *args, **kwargs):
        #get the realm
        self.realm = get_object_or_404(Realm, site = Site.objects.get_current())
    
        #keyname specified in url
        if 'keyname' in kwargs:
            actual = kwargs['keyname'].split('.') #get the actual last commune key: /<parent>.<child>.<desired>/
            self.commune = get_object_or_404(Commune.localised.select_related(), section__keyname = actual[-1]) 
            self.section = self.commune.section
        else:
            #no keyname specified, we need the "primary" section
            
            self.section = self.realm.primary_section #get the primary section of this realm
            
            if self.section.generates_navigation:
                #this section has a keyword argument, we should use it
                return redirect(self.section.element.get_absolute_url())
            
            if self.section.generates_navigation == False and type(self.section.element) != Commune:
                #this section doesn't generate navigation and isn't a commune (we have no idea what it is)
                return HttpResponseServerError
                
            #set the commune
            self.commune = self.section.element
        
        #finally return the parent get method
        return super(CommuneMixin, self).get(request, *args, **kwargs)

    #overrides base page title functionality
    def get_page_title(self):
        return "%s | %s" % (self.commune.realm.name, self.commune.name)

    def get_template_names(self):
        return [self.commune.override_template, self.commune.generic_realm_template, self.commune.generic_template] 
    
    def get_context_data(self, *args, **kwargs):
        context = super(CommuneMixin, self).get_context_data(*args, **kwargs)
        
        #set the context commune
        context.update({
            'commune': self.commune,
            'CMS_SECTION': self.section,
            'CMS_REALM': self.realm,
        })
        
        return context
        
class PageMixin(object):
    title = None
    onload = None
    
    def get_context_data(self, *args, **kwargs):
        context = super(PageMixin, self).get_context_data(*args, **kwargs)
        
        if 'page' in context:
            context['page'].update({
                'title': self.get_page_title(),
                'onload': self.get_page_onload(),
            })
        else:
            context.update({
                'page': {
                    'title': self.get_page_title(),
                    'onload': self.get_page_onload(),
                }
            })
            
        return context
        
    def get_page_title(self):
        if self.title is None:
            raise ImproperlyConfigured(
                "Page requires either a defintion of "
                "'title' or an implementation of 'get_page_title()'")
        else:
            return self.title
        
    def get_page_onload(self):
        return self.onload