from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

from libscampi.contrib.cms.communism import models


class BaseRealmFilter(SimpleListFilter):
    title = _("Realm / Site")
    parameter_name = 'realm'

    def lookups(self, request, model_admin):
        return models.Realm.objects.values_list('id', 'name')


class BaseCommuneFilter(SimpleListFilter):
    title = _("Commune")
    parameter_name = 'commune'

    def lookups(self, request, model_admin):
        realm_limit = request.GET.get('realm', None)

        if realm_limit:
            return models.Commune.objects.filter(section__realm_id=realm_limit).values_list('id', 'name')

        return models.Commune.objects.values_list('id', 'name')


class SliceRealmFilter(BaseRealmFilter):
    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(commune__section__realm_id=self.value())


class SliceCommuneFilter(BaseCommuneFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(commune_id=self.value())


class NamedBoxRealmFilter(BaseRealmFilter):
    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(slice__commune__section__realm_id=self.value())


class NamedBoxCommuneFilter(BaseCommuneFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(slice__commune_id=self.value())
