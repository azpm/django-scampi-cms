from datetime import datetime, timedelta
from django.db import models
from django.db.models import Count, Q

class PublishedManager(models.Manager):
    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)

    def find_related(self, story):
        cats = story.categories.values_list('keyname', flat=True)

        right_now = datetime.now()
        long_ago = right_now - timedelta(days=30)

        qs = self.get_query_set().filter(
            Q(story__peers__in=[story]) | Q(story__categories__keyname__in=cats),
            start__lte=right_now, start__gte=long_ago
        ).exclude(story__id = story.pk)
        qs = qs.annotate(rel_count=Count('story__categories'))

        return qs.order_by('-rel_count').values('rel_count','story','story__slug','story__article','start','slug').distinct()


class CategoryGenera(models.Manager):
    def for_cloud(self, qs):
        return super(CategoryGenera, self).get_query_set().distinct().filter(story__publish__in=qs, browsable=True).annotate(occurances=Count('story')).values('id','title','keyname','occurances')
