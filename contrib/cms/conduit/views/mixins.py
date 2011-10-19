from django.core.cache import cache

from libscampi.contrib.cms.communism.models import NamedBox
from libscampi.contrib.cms.conduit.models import DynamicPicker, StaticPicker

class PickerGraph(object):
    pickers = None
    
    def generate_graph(self):
        #if there isn't a commune, there's no picker graph
        if not self.commune:
            return {}
            
        cached_collection_key = 'commune_picker_collection_%s' % self.commune.pk
        collection = cache.get(cached_collection_key, {})
            
        if not collection:
            statics = Commune.staticpicker_related.all()
            dynamics = Commune.dynamicpicker_related.all()
            
            for static in statics:
                collection[static.namedbox] = static
                
            for dynamic in dynamics:
                try:
                    key = dynamic.namedbox_set.get(slice__commune = self.commune)
                except (NamedBox.DoesNotExist, NamedBox.MultipleObjectsReturned):
                    continue
                else:
                    collection[key] = dynamic
            
            cache.set(cached_collection_key, collection, 60*20)
        
        return collection
    
    def get_context_data(self, *args, **kwargs):
        context = super(PickerGraph, self).get_context_data(*args, **kwargs)
        
        #populate the graph
        self.pickers = self.generate_graph()
        
        context.update({'pickers': self.pickers})
        
        return context