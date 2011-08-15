from libscampi.contrib.cms.conduit.models import DynamicPicker, StaticPicker

class PickerGraph(object):
    """ Maintains an object graph of pickers for a given commune"""
    
    __slots__ = "__weakref__", "_registry", "_commune"
    
    def __init__(self, commune):
        self._registry = {
            'static': OrderedDict(),
            'dynamic': OrderedDict()
        }
        self._commune = commune

    def build_graph(self):
        dynamic_picker_qs = DynamicPicker.objects.filter(namedbox__slice__commune = self._commune)
        
        for dynamic_picker in dynamic_picker_qs:
            self._registry.update(
                {dynamic_picker.name: dynamic_picker}
            )