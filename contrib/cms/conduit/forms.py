import logging

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

#libazpm stuff
from libscampi.contrib.cms.conduit.picker import manifest
from libscampi.contrib.cms.conduit.models import DynamicPicker

logger = logging.getLogger('libscampi.contrib.cms.conduit.forms')

class DynamicPickerInitialForm(forms.ModelForm):
    content = forms.ModelChoiceField(queryset = manifest.contenttypes_for_available(), help_text = _("What model will populate this picker?"))
    class Meta:
        model = DynamicPicker
        
class DynamicPickerForm(forms.ModelForm):
    class Meta:
        model = DynamicPicker
        
    def clean(self):
        cleaned_data = self.cleaned_data
        
        if len(self._errors) > 0:
            logger.debug("DynamicPicker Form Errors: %s" % self._errors)
            
        return cleaned_data