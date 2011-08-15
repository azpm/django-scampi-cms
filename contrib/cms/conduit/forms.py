from django import forms
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

#libazpm stuff
from libscampi.contrib.cms.conduit.picker import manifest
from libscampi.contrib.cms.conduit.models import DynamicPicker

class ContentWidget(forms.widgets.Select):
    def render(self, name, value, attrs=None):
        #admin view urls
        view_path = reverse("admin:conduit-picking-filters-form")
        
        #basic html for the widget
        html = super(ContentWidget, self).render(name, value, attrs)
        
        #build "picker" links
        links = "<a id=\"incf-%(val)s\">Inclusion Filters</a>, <a id=\"excf-%(val)s\">Exclusion Filters</a>" % {'val': attrs['id']}
        js_build = """<script type="text/javascript">django.jQuery("#%s").picking_form({script: '%s', content: "#%s", filter_method: '%s'});</script>"""

        js_inclusion = js_build % ("incf-%s" % attrs['id'], view_path, attrs['id'], 'include')
        js_exclusion = js_build % ("excf-%s" % attrs['id'], view_path, attrs['id'], 'exclude')
        
        return mark_safe("\n".join([html, links, js_inclusion, js_exclusion]))
    
    class Media:
        js = (settings.MASTER_MEDIA_URL+'admin/js/jquery.conduit.pickingform.js',settings.MASTER_MEDIA_URL+'admin/js/jquery.colorbox.js',settings.MASTER_MEDIA_URL+'admin/js/jquery.form.js')
        css = {
            'all': (settings.MASTER_MEDIA_URL+'admin/css/colorbox.css',),
        }

class DynamicPickerForm(forms.ModelForm):
    content = forms.ModelChoiceField(queryset = manifest.contenttypes_for_available())
    class Meta:
        model = DynamicPicker
        
class DynamicPickerFormForInstance(forms.ModelForm):
    content = forms.ModelChoiceField(widget = ContentWidget, queryset = manifest.contenttypes_for_available())
    class Meta:
        model = DynamicPicker