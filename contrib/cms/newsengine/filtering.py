from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from libscampi.contrib.cms.newsengine.models import PublishCategory

class PublishTypeListFilter(SimpleListFilter):
    """
    Filter published list be things that have been seen
    """

    # title displayed on right
    title = _("Publish Kind")
    # url param name
    parameter_name = 'publish_kind'

    def lookups(self, request, model_admin):
        return PublishCategory.objects.values_list('keyname','title')

    def queryset(self, request, queryset):
        if self.value() is not None:
            queryset.filter(category__keyname = self.value())


class ArticleAuthorListFilter(SimpleListFilter):
    """
    Filter for my articles, or everyone elses
    """

    # title on right
    title = _("Author")
    # url param name
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        return (
            ('me', _('Me')),
            ('everyone', _('Everyone')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'me' or self.value() is None:
            return queryset.filter(Q(story__article__author = request.user) | Q(story__author = request.user))

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.selected_filter(lookup),
                'query_string': cl.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
                }

    def selected_filter(self, lookup):
        val = self.value()

        if val is None and lookup =="me":
            return True
        else:
            return val == lookup