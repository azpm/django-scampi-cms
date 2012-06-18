import logging

from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponseServerError
from django.contrib.sites.models import Site
from django.db.models import Q
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from libscampi.contrib.cms.communism.models import *
from libscampi.contrib.cms.views.func import static_script, static_style

import collections

logger = logging.getLogger('libscampi.contrib.cms.communism.views')

class html_link_refs(collections.MutableSet):
    def __init__(self, iterable = None):
        self.elements = lst = []
        if not iterable:
            return
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

    def discard(self, value):
        if self.__contains__(value):
            del(self.elements[value])

    def __del__(self):
        self.clear()

    def reset(self):
        self.elements = []
        
class SectionMixin(object):
    section = None
    realm = None
    refresh_caches = False

    def _process_request(self, request, *args, **kwargs):
        """
        get the section, realm and set refresh_caches flag for GET & POST Requests
        """
        site = Site.objects.get_current()
        try:
            self.realm = site.realm
        except Realm.DoesNotExist:
            raise Http404("No Realm Configured")

        cache_control = request.META.get('HTTP_CACHE_CONTROL', None)
        if cache_control and cache_control == "max-age=0":
            self.refresh_caches = True

        #keyname specified in url
        if 'keyname' in kwargs:
            keyname = kwargs.pop('keyname')
            actual = keyname.split('.') #get the actual last commune key: /<parent>.<child>.<desired>/
            logger.debug("requested cms section: {0:>s}".format(actual))

            if "__un_managed" in actual:
                if "__un_managed" in request.path:
                    # always strip __un_managed from the URL if anyone manages to put it in
                    return redirect(self.realm.get_absolute_url())
                    # if the magic identifier __un_managed appears from the view object graph, we set view section to special "un-managed" section
                self.section = MagicSection(id=0, realm=self.realm, display_order = 0, active = True, generates_navigation=False, extends=None)
            else:
                self.section = get_object_or_404(Section.localised.prefetch_related('element'), keyname = actual[-1])
        else:
            try:
                # we'll see if the section is embedded in the url (it's always the first thing after the domain)
                current_section = request.path.split('/',2)[1]
            except IndexError:
                logger.critical("something bad went wrong with the request, %s" % request.path)
                raise HttpResponseServerError

            if current_section != '':
                # section keyname is in the url but not in the view graph/passed args
                # self.section = get_object_or_404(Section.localised.select_related(), keyname = current_section)
                self.section = get_object_or_404(Section.localised.prefetch_related('element'), keyname = current_section)
            else:
                # no keyname specified, we need the "primary" section
                try:
                    self.section = self.realm.primary_section #get the primary section of this realm
                except ObjectDoesNotExist:
                    raise Http404("No CMS Sections Active")

                if self.section.generates_navigation:
                    # this section has a keyword argument, we should use it
                    return redirect(self.section.element.get_absolute_url())

            if not self.section:
                raise Http404("Section Not Found")

        if hasattr(request, 'toolbar') and request.user.is_staff:
            request.toolbar.show_toolbar = True

    def get(self, request, *args, **kwargs):
        logger.debug("SectionMixin.get called")

        self._process_request(request, *args, **kwargs)
                   
        # finally return the parent get method
        return super(SectionMixin, self).get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        logger.debug("SectionMixin.post called")

        self._process_request(request, *args, **kwargs)

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
        if hasattr(request, 'toolbar'):
            request.toolbar.scampi_managed = True

        #finally return the parent get method
        return super(CommuneMixin, self).get(request, *args, **kwargs)

    #overrides base page title functionality
    def get_page_title(self):
        return "{0:>s} | {1:>s}".format(self.realm.name, self.commune.name)

    def get_template_names(self):
        tpl_list = (
            "{0:>s}/communism/{1:>s}/{2:>s}.html".format(self.commune.theme.keyname, self.realm.keyname, self.section.keyname),
            "{0:>s}/communism/{1:>s}/commune.html".format(self.commune.theme.keyname, self.realm.keyname),
            "{0:>s}/communism/commune.html".format(self.commune.theme.keyname),
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

class ApplicationMixin(object):
    """
    Implements themed stylesheets and javascripts for libscampi.contrib.cms.communism.models.Application
    """
    cached_css_key = None
    cached_js_key = None

    def get_stylesheets(self):
        if self.cached_css_key is None or self.get_theme() is None:
            return None

        if self.refresh_caches:
            #invalidate on refresh_cache
            cache.delete(self.cached_css_key)
        styles = cache.get(self.cached_css_key, None)

        #cache empty, get the styles and refill the cache
        if not styles:
            logger.debug("missed css cache on {0:>s}".format(self.cached_css_key))
            styles = StyleSheet.objects.filter(active=True, base=True, theme=self.get_theme()).order_by('precedence')
            cache.set(self.cached_css_key, styles, 60*20)

        #build a simple collection of styles
        css_collection = html_link_refs()
        for style in styles:
            css_collection.add(style)

        #add the static css for this app
        static_styles = self.get_static_styles()
        if static_styles:
            for style in static_styles:
                css_collection.add(static_style(**style))

        return css_collection

    def get_javascripts(self):
        if self.cached_js_key is None or self.get_theme() is None:
            return None

        if self.refresh_caches:
            #invalidate on refresh_cache
            cache.delete(self.cached_js_key)
        script_ids = cache.get(self.cached_js_key, None)

        #cache empty, get the styles and refill the cache
        if not script_ids:
            logger.debug("missed script cache on {0:>s}".format(self.cached_js_key))
            scripts = Javascript.objects.filter(active=True, base=True, theme=self.get_theme()).order_by('precedence')
            cache.set(self.cached_js_key, list(scripts.values_list('id', flat=True)), 60*20)
        else:
            scripts = Javascript.objects.filter(id__in=script_ids).order_by('precedence')

        #build a simple collection of styles
        js_collection = html_link_refs()
        for script in scripts:
            js_collection.add(script)

        #add the static js for this app
        static_scripts = self.get_static_scripts()
        if static_scripts:
            for script in static_scripts:
                js_collection.add(static_script(**script))

        return js_collection

    def get_static_styles(self):
        return None

    def get_static_scripts(self):
        return None

    def get_theme(self):
        raise NotImplementedError("view using ApplicationMixin must provide get_theme method")
    
class CSSMixin(object):
    def get_stylesheets(self):
        theme = self.get_theme()
        logger.debug("CSSMixin.get_stylesheets called")

        #try to get the cached css for this commune
        cached_css_key = 'commune:css:{0:d}'.format(self.commune.pk)
        if self.refresh_caches:
            #invalidate on refresh_cache
            cache.delete(cached_css_key)
        styles = cache.get(cached_css_key, None)
        
        #cache empty, get the styles and refill the cache
        if not styles:
            logger.debug("missed css cache on {0:>s}".format(cached_css_key))
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
        cached_scripts_key = 'commune:scripts:{0:d}'.format(self.commune.pk)
        if self.refresh_caches:
            #invalidate on refresh_cache
            cache.delete(cached_scripts_key)
        script_ids = cache.get(cached_scripts_key, None)

        #build a simple collection of styles
        script_collection = html_link_refs()

        #cache empty, get the scripts and refill the cache
        if not script_ids:
            logger.debug("missed js cache on {0:>s}".format(cached_scripts_key))
            scripts = Javascript.objects.filter(active=True).filter(
                Q(pickertemplate__dynamicpicker__namedbox__slice__commune=self.commune) & 
                Q(pickertemplate__dynamicpicker__namedbox__active=True) | 
                Q(staticpicker__namedbox__slice__commune=self.commune) &
                Q(staticpicker__namedbox__active=True) |
                Q(base=True),
                Q(theme__pk=theme.id)
            ).order_by('precedence')
            cache.set(cached_scripts_key, list(scripts.values_list('id', flat = True)), 60*20)
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