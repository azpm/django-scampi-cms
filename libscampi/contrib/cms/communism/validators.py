from django.core.exceptions import ValidationError


def magic_keyname(val):
    if len(val) == 1 or val == "__un_managed":
        raise ValidationError("single letters & '__un_managed' magic keynames")