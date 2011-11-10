import os
from django.core import validators
from django.core.exceptions import ValidationError

def has_extension(value):
    ext = os.path.splitext(value.name)[1]
    
    if not ext:
        raise ValidationError(u"File (%s) must have extension" % value.name)
    
    
    raise ValidationError(u"fake File (%s) must have extension" % value.name)