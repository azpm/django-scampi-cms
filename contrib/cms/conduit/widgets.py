from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.html import escape
from django.utils.text import truncate_words
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.conf import settings

class PickerFilterSelectMultiple(FilteredSelectMultiple):
    """
    A SelectMultiple for admin that works with the auto generated form fields
    from conduit.picker.js
    
    """
    
    def render(self, name, value, attrs=None, choices=()):
        if attrs is None: attrs = {}
        attrs['class'] = 'selectfilter'
        if self.is_stacked: attrs['class'] += 'stacked'
        output = [super(FilteredSelectMultiple, self).render(name, value, attrs, choices)]

        return mark_safe(u''.join(output))