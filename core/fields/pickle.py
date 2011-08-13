import binascii
import datetime
import random
import string
import sys

from django import forms
from django.db import models
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode

USE_CPICKLE = getattr(settings, 'USE_CPICKLE', False)

if USE_CPICKLE:
    import cPickle as pickle
else:
    import pickle
    
class PickleField(models.TextField):
    __metaclass__ = models.SubfieldBase

    editable = False
    serialize = False

    def get_db_prep_value(self, value, connection=None, prepared=False):
        return pickle.dumps(value)

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        # Tries to convert unicode objects to string, cause loads pickle from
        # unicode excepts ugly ``KeyError: '\x00'``.
        try:
            return pickle.loads(smart_str(value))
        # If pickle could not loads from string it's means that it's Python
        # string saved to PickleField.
        except ValueError:
            return value