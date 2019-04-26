from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

from libscampi.contrib.cms.conduit.picker import manifest


class ContentTypeListFilter(SimpleListFilter):
    """
    Filter list by available picking contenttypes
    """
    title = _("Content Source")
    parameter_name = 'cs'

    def lookups(self, request, model_admin):
        return manifest.contenttypes_for_available().values_list('id', 'name')

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(content_id=self.value())
