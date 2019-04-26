from django.contrib.contenttypes.models import ContentType
from django.apps import apps as django_apps


class PickerError(Exception):
    """
    model cannot be picked
    """


class PickerManager(object):
    """ Manages what can and cannot be picked """

    # this seemed cool
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
            raise PickerError("{0!r:s} has already been registered".format(model_class))

        self._registry[model_class] = picking_class

    def get_registration_info(self, model_class):
        try:
            fields = self._registry[model_class]
        except KeyError:
            raise PickerError("{0!r:s} has not be registered as a pickable model".format(model_class))
        else:
            return fields

    def unregister(self, model_class):
        """ Removes a model class from the picking registry """
        try:
            fields = self._registry.pop(model_class)
        except KeyError:
            raise PickerError("{0!r:s} cannot be unregistered before it has been registered".format(model_class))

    def available(self):
        return self._registry.keys()

    def contenttypes_for_available(self):
        """ Returns list of valid ContentTypes for picking """
        models = self._registry.keys()

        ids = []
        for model in models:
            ids.append(ContentType.objects.get_by_natural_key(model._meta.app_label, model._meta.module_name).id)

        return ContentType.objects.filter(id__in=list(ids))

    def get_for_picking(self, ct):
        """ Returns class instance of a given model ContentType"""
        if type(ct) is not ContentType:
            raise TypeError("cannot call get_for_picking without a valid ContentType, called with {0:>s}".format)

        model = django_apps.get_model(ct.app_label, ct.model)

        if not model:
            raise RuntimeError("({0:>s}, {1:>s}) is not registered for picking".format(ct.app_label, ct.model))
            # TODO see if this block needs to be ported to django 1.11+
            # try:
            #     app_cache.write_lock.acquire()
            #     module = app_cache.load_app('libscampi.contrib.{0:>s}'.format(ct.app_label))
            #     app_cache.write_lock.release()
            #     model = app_cache.get_model(ct.app_label, ct.model)
            # except ImportError:
            #     raise NameError("cannot get ({0:>s}, {1:>s}) from any path".format(ct.app_label, ct.model))

        if not self.is_registered(model):
            raise NameError("({0:>s}, {1:>s}) is not registered for picking".format(ct.app_label, ct.model))

        try:
            fs = self.get_registration_info(model)()
        except PickerError:
            raise NameError("({0:>s}, {1:>s}) has no filter set".format(ct.app_label, ct.model))

        return model, fs


manifest = PickerManager()
