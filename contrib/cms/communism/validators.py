from django.core.exceptions import ValidationError

def magic_keyname(val):
    if val == "p" or val == "c":
        raise ValidationError("the letters p & c are magic keynames")