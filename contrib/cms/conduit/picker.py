from django.contrib.contenttypes.models import ContentType
from django.db.models.loading import cache as app_cache
from django.db import models


class PickerError(Exception):
    """
    model cannot be picked
    """
    
class PickerManager(object):
    """ Manages what can and cannot be picked """
    
    #this seemed cool
    __slots__ = "__weakref__", "_registry", 
    
    def __init__(self):
        self._registry = {}
    
    def is_registered(self, model_class):
        """
        Checks whether the given model has been registered with the picker
        """
        return model_class in self._registry
        
    def register(self, model_class, picking_class):
        """ Registers a model to be pickable """
        if self.is_registered(model_class):
            raise PickerError,  "%r has already been registered" % model_class
        #if model_class._meta.proxy:
        #    raise PickerError, "%r cannot be pickable, proxy models aren't allowed (I'm lazy)" % model_class
                
        self._registry[model_class] = picking_class
        return
        
    def get_registration_info(self, model_class):
        try:
            fields = self._registry[model_class]
        except KeyError:
            raise PickerError, "%r has not be registered as a pickable model" % model_class
        else:
            return fields
            
    def unregister(self, model_class):
        try:
            fields = self._registry.pop(model_class)
        except KeyError:
            raise PickerError, "%r cannot be unregistered before it has been registered" % model_class
            
    def available(self):
        return self._registry.keys()
    
    def contenttypes_for_available(self):
        models = self._registry.keys()
        
        ids = []
        for model in models:
            ids.append(ContentType.objects.get_by_natural_key(model._meta.app_label, model._meta.module_name).id)
        
        return ContentType.objects.filter(id__in=ids)
        
    #this is a magic method that returns a Class instance of the model
    def get_for_picking(self, ct):
        if type(ct) is not ContentType:
            raise TypeError, "cannot call get_for_picking without a valid ContentType, called with %s" % type(ct)
    
        model = app_cache.get_model(ct.app_label, ct.model)
        
        if not model:
            try:
                app_cache.write_lock.acquire()
                module = app_cache.load_app('libscampi.contrib.%s' % ct.app_label)
                app_cache.write_lock.release()
                model = app_cache.get_model(ct.app_label, ct.model)
            except ImportError:
                raise NameError, "cannot get (%s, %s) from any path" % (ct.app_label, ct.model)        
        
        if not self.is_registered(model):
            raise NameError, "(%s, %s) is not registerd for picking" % (ct.app_label, ct.model)

        try:
            fs = self.get_registration_info(model)()
        except PickerError:
            raise NameError, "(%s, %s) has no filterset" % (ct.app_label, ct.model)
            
        return (model, fs)
    
        
manifest = PickerManager()