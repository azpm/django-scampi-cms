from django.db.models import Q, Max
from django.http import Http404, HttpResponseServerError
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.contrib.contenttypes.models import ContentType

#from libscampi.contrib.cms.newsengine.models import Publish
from libscampi.contrib.cms.communism.models import Javascript, StyleSheet, Theme
from libscampi.contrib.cms.conduit.models import DynamicPicker

class PickerMixin(object):
    picker = None
    
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
        #ContentType.objects.get_for_model(Publish):
            raise Http404("Picker Archives only work for Published Stories")
            
        return super(PickerMixin, self).get(request, *args, **kwargs)