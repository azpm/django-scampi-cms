import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from libscampi.contrib.cms.conduit.picker import manifest
from libscampi.contrib.cms.conduit.models import DynamicPicker

logger = logging.getLogger('libscampi.contrib.cms.conduit.forms')


class DynamicPickerInitialForm(forms.ModelForm):
    content = forms.ModelChoiceField(queryset=manifest.contenttypes_for_available(),
                                     help_text=_("What model will populate this picker?"))

    class Meta:
        model = DynamicPicker
        fields = '__all__'


class DynamicPickerForm(forms.ModelForm):
    class Meta:
        model = DynamicPicker
        fields = '__all__'

    def clean(self):
        cleaned_data = self.cleaned_data

        active = cleaned_data.get('active')
        commune = cleaned_data.get('commune')

        if active and not commune:
            # We know these are not in self._errors now (see discussion
            # below).
            msg = u"You cannot activate a dynamic picker without associating a primary commune"
            self._errors["active"] = self.error_class([msg])
            self._errors["commune"] = self.error_class([msg])

            # These fields are no longer valid. Remove them from the
            # cleaned data.
            del cleaned_data["active"]

        if len(self._errors) > 0:
            logger.debug("DynamicPicker Form Errors: {0:>s}".format(self._errors))

        return cleaned_data
