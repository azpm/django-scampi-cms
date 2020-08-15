import django_filters
from django.contrib.admin.widgets import FilteredSelectMultiple

from libscampi.contrib.cms.newsengine.models import Publish, StoryCategory


class PublishPicking(django_filters.FilterSet):
    start = django_filters.filters.DateRangeFilter(lookup_expr=('lt', 'gt', 'lte', 'gte'))
    end = django_filters.filters.DateRangeFilter(name="end", lookup_expr=('lt', 'gt', 'lte', 'gte'))
    story__categories = django_filters.filters.ModelMultipleChoiceFilter(queryset=StoryCategory.objects.all(),
                                                                         widget=FilteredSelectMultiple(
                                                                             "Story Categories", False, {'class': 'selectfilter'}))

    class Meta:
        model = Publish
        fields = ['site', 'start', 'end', 'category', 'published', 'story__categories']

    @staticmethod
    def static_chain(qs):
        qs = qs.distinct()
        return qs

    @staticmethod
    def static_select_related():
        return (
            'thumbnail',
            'story__author',
        )

    @staticmethod
    def static_prefetch_related():
        return (
            'story__article',
            'story__article__image_inlines',
            'story__article__video_inlines',
            'story__article__audio_inlines',
            'story__article__document_inlines',
            'story__article__object_inlines',
            'story__article__external_inlines',
        )

    @staticmethod
    def static_defer():
        return (
            'end',
            'approved_by',
            'category',
            'seen',
            'published',
            'thumbnail__author',
            'thumbnail__creation_date',
            'thumbnail__reproduction_allowed',
            'thumbnail__modified',
            'thumbnail__mime_type',
            'story__author__email',
            'story__author__password',
            'story__author__is_staff',
            'story__author__is_active',
            'story__author__is_superuser',
            'story__author__last_login',
            'story__author__date_joined',
            'story__creation_date',
            'story__modified',
            'story__image_playlist',
            'story__video_playlist',
            'story__audio_playlist',
            'story__document_playlist',
            'story__object_playlist',
        )
