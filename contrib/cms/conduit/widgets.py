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
        """output.append(u
            <script type="text/javascript">jQuery(document).bind('filter_id_update', function (e, id) { 
                var form_field = jQuery("#"+id);
                if (form_field.is('select') && form_field.attr('multiple') == 'multiple' && form_field.attr('class') == 'selectfilter') 
                {
                    console.log('id', id);
                    console.log('field', form_field);
                }
            });
            </script>
        )"""
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        #output.append(u'SelectFilter.init("id_%s", "%s", %s, "%s"); });</script>\n' % \
        #    (name, self.verbose_name.replace('"', '\\"'), int(self.is_stacked), settings.ADMIN_MEDIA_PREFIX))
        return mark_safe(u''.join(output))