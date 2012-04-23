import logging

from django.core.cache import cache
from django.db.models import Q, Max
from django.http import Http404, HttpResponseServerError
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.contrib.contenttypes.models import ContentType

from libscampi.contrib.cms.newsengine.models import StoryCategory
from libscampi.contrib.cms.communism.models import Javascript, StyleSheet, Theme
from libscampi.contrib.cms.conduit.models import DynamicPicker

logger = logging.getLogger('libscampi.contrib.cms.conduit.views')

class PickerMixin(object):
    picker = None
    base_categories = None
    
    def get(self, request, *args, **kwargs):
        """
        provides the picker to the view for base QuerySet limits
        """
        
        if 'picker' in kwargs:
            picker_key = kwargs['picker']
            self.picker = get_object_or_404(DynamicPicker, keyname = picker_key, commune = self.commune)
        else:
            raise Http404
            
        if self.picker.content != ContentType.objects.get_by_natural_key('newsengine','Publish'):
            raise Http404("Picker Archives only work for Published Stories")
            
        #every PublishPicking picker has base story categories that define it
        cat_cache_key = "picker:base:categories:%d" % self.picker.id
        categories = cache.get(cat_cache_key, set())
        if not categories:
            categories = set() #no result queryset evals to none, reset it to a blank set
            keep_these = ('story__categories__id__in','story__categories__id__exact')
            if isinstance(self.picker.include_filters, list):
                for f in self.picker.include_filters:
                    for k in f.keys():
                        if k in keep_these:
                            categories|=set(f[k]) #build a set of our base categories
            else:
                logger.critical("invalid picker: cannot build archives from picker %s [id: %d]" % (self.picker.name, self.picker.id))
            
            categories = StoryCategory.objects.filter(pk__in=list(categories), browsable=True)
            cache.set(cat_cache_key, categories, 60*60)
            
        self.base_categories = categories

        #add section to the graph by way of the picker
        kwargs.update({'keyname': self.picker.commune.section.keyname})

        return super(PickerMixin, self).get(request, *args, **kwargs)
        
    def get_context_data(self, *args, **kwargs):
        logger.debug("PickerMixin.get_context_data started")
        #get the existing context
        context = super(PickerMixin, self).get_context_data(*args, **kwargs)
        
        #give the template the current picker
        context.update({'picker': self.picker, 'base_categories': self.base_categories})
        logger.debug("PickerMixin.get_context_data ended")
        
        return context