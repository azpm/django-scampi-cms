from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

class ReviewedListFilter(SimpleListFilter):
    """
    Filter published list be things that have been seen
    """

    # title displayed on right
    title = _("Reviewed")
    # url param name
    parameter_name = 'reviewed'

    def lookups(self, request, model_admin):
        return (
            ('no', _('No')),
            ('yes', _('Yes')),
            ('all', _('All')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(seen=True)
        if self.value() == 'no':
            return queryset.filter(seen=False)

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.selected_filter(lookup),
                'query_string': cl.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def selected_filter(self, lookup):
        val = self.value()

        if val is None and lookup =="no":
            return True
        else:
            return val == lookup

class ArticleAuthorListFilter(SimpleListFilter):
    """
    Filter for my articles, or everyone elses
    """

    # title on right
    title = _("Article Author")
    # url param name
    parameter_name = 'article_author'

    def lookups(self, request, model_admin):
        return (
            ('me', _('Me')),
            ('everyone', _('Everyone')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'me':
            return queryset.filter(story__article__author = request.user)

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