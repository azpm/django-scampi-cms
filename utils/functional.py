from functools import wraps, update_wrapper


class cached_property(object):
    """
    Decorator that creates converts a method with a single
    self argument into a property cached on the instance.
    
    see django/trunk/utils/functional
    """
    def __init__(self, func):
        self.func = func
	
    def __get__(self, instance, type):
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res