from django.core.exceptions import ValidationError

def magic_keyname(val):
    if val == "p" or val == "c" or val == "r":
        raise ValidationError("the letters r, p & c are magic keynames")