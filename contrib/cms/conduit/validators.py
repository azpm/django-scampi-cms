from django.core.exceptions import ValidationError

def magic_keyname(val):
    if len(val) == 1:
        raise ValidationError("single letters are magic keynames")