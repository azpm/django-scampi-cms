from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

#libazpm stuff
from libscampi.contrib.cms.conduit.picker import manifest
from libscampi.contrib.cms.conduit.models import DynamicPicker

class DynamicPickerForm(forms.ModelForm):
    content = forms.ModelChoiceField(queryset = manifest.contenttypes_for_available(), help_text = _("What model will populate this picker?"))
    class Meta:
        model = DynamicPicker