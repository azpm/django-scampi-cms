import markdown as _markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def markdown(value):
    extensions = ["nl2br", ]

    return mark_safe(
        _markdown.markdown(force_unicode(value), extensions=extensions, safe_mode=False, enable_attributes=False)
    )
