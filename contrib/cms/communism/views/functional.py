import datetime, calendar

from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.http import Http404, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.views.generic import date_based
from django.template import TemplateDoesNotExist, loader as tpl_loader
from django.core.cache import cache
from django.db.models import Q, Max

from libscampi.contrib.cms.communism.models import *
from libscampi.contrib.cms.newsengine.models import Publish, PublishCategory
from libscampi.contrib.cms.pages import Page, html_link_refs

def get_cached_htmlrefs(commune):
    if type(commune) is not Commune:
        return {'styles': [], 'scripts': []}
    
    cached_css_key = 'commune_css_%s' % commune.pk
    styles = cache.get(cached_css_key, None)
    if not styles:
        styles = StyleSheet.objects.filter(active=True).filter(
            Q(pickertemplate__dynamicpicker__namedbox__slice__commune=commune) & 
            Q(pickertemplate__dynamicpicker__namedbox__active=True) | 
            Q(base=True)
        ).order_by('precedence')
        cache.set(cached_css_key, styles, 60*20)
    
    cached_script_key = 'commune_scipts_%s' % commune.pk
    scripts = cache.get(cached_script_key, None)
    if not scripts:
        scripts = Javascript.objects.filter(active=True).filter(
            Q(pickertemplate__dynamicpicker__namedbox__slice__commune=commune) & 
            Q(pickertemplate__dynamicpicker__namedbox__active=True) | 
            Q(base=True)
        ).order_by('precedence')
        cache.set(cached_script_key, scripts, 60*20)
    
    return {'styles': styles, 'scripts': scripts}    
    
def preprocess_story_generics(keyname, publishword, tpl):
    actual = keyname.split('.')
    commune = get_object_or_404(Commune.localised.select_related(), section__keyname = actual[-1])
    publish_activity = get_object_or_404(PublishCategory, keyname = publishword)
    
    try:
        today = datetime.date.today()
        clip = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1], 23, 59, 59)
        qs = Publish.active.distinct().filter(category=publish_activity, start__lte=clip)
    except (ValueError, IndexError): 
        qs = Publish.active.distinct().filter(category=publish_activity)
    
    
    archival_categories = list(commune.archive_categories.all())

    if len(archival_categories) > 0:
        qs = qs.filter(story__categories__in=archival_categories)
    
    
    try:
        tpl = template_name="%s/newsengine/%s" % (commune.theme.keyname, tpl)
    except (ValueError, TypeError):
        raise Http404("theme gone")
        
    page = Page()
    page.theme = commune.theme
    #page.context['commune'] = commune
    
    for style in commune.theme.stylesheet_set.filter(active=True, base=True):
        page.styles.add(style)
    for script in commune.theme.javascript_set.filter(active=True, base=True):
        page.scripts.add(script)
        
    return {'qs': qs, 'tpl': tpl, 'context': {'page': page.bound_context, 'publishword': publish_activity}}

def story_archive(request, keyname, publishword):
    meta = preprocess_story_generics(keyname, publishword, 'generic.story.archive.html')
    
    try:
        return date_based.archive_index(request, meta['qs'], date_field='start', 
            template_name=meta['tpl'], extra_context=meta['context'])
    except TemplateDoesNotExist:
        raise Http404("Generic View Failed")

def story_archive_year(request, keyname, publishword, year):
    meta = preprocess_story_generics(keyname, publishword, 'generic.story.archive.year.html')
        
    try:
        return date_based.archive_year(request, int(year),
            meta['qs'], date_field='start', template_name=meta['tpl'], extra_context=meta['context'])
    except (TemplateDoesNotExist, ValueError):
        raise Http404("Generic View Failed")
 
def story_archive_month(request, keyname, publishword, year, month):
    meta = preprocess_story_generics(keyname, publishword, 'generic.story.archive.month.html')
    
    try:
        date = datetime.date(int(year), int(month), 1)
    except (ValueError, TypeError):
        raise Http404("invalid date")
    
    try:
        return date_based.archive_month(request, date.strftime("%Y"), date.strftime("%b"),
            meta['qs'], date_field='start', template_name=meta['tpl'], extra_context=meta['context'])
    except TemplateDoesNotExist:
        raise Http404("Generic View Failed")
          
def story_archive_day(request, keyname, publishword, year, month, day):
    meta = preprocess_story_generics(keyname, publishword, 'generic.story.archive.day.html')
    
    try:
        date = datetime.date(int(year), int(month), int(day))
    except (ValueError, TypeError):
        raise Http404("invalid date")
    
    try:
        return date_based.archive_day(request, date.strftime("%Y"), date.strftime("%b"), date.strftime("%d"), 
            meta['qs'], date_field='start', template_name=meta['tpl'], extra_context=meta['context'])
    except TemplateDoesNotExist:
        raise Http404("Generic View Failed")
    
def story_detail(request, keyname, publishword, year, month, day, slug):
    meta = preprocess_story_generics(keyname, publishword, 'generic.story.detail.html')
    
    #process date
    try:
        date = datetime.date(int(year), int(month), int(day))
    except (ValueError, TypeError):
        raise Http404("invalid date")
    
    try:
        return date_based.object_detail(request, date.strftime("%Y"), date.strftime("%b"), date.strftime("%d"), 
            meta['qs'], date_field='start', slug=slug, template_name=meta['tpl'], extra_context=meta['context'])
    except TemplateDoesNotExist:
        raise Http404("Generic View Failed")

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        