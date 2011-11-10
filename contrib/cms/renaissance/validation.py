from django.core import validators
from django.core.exceptions import ValidationError

def has_extension(value):
    f = value.name
    assert False