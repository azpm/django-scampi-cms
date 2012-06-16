from datetime import datetime
from django.db import models
from django.db.models import Avg, Max, Min, Count, Q, Variance, StdDev

class PublishedManager(models.Manager):
    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)

    def find_related(self, story):
        cats = story.categories.values_list('keyname', flat=True)

        qs = self.get_query_set().filter(Q(story__peers__in=[story]) | Q(story__categories__keyname__in=cats), start__lte=datetime.now()).exclude(story__id=story.pk)
        qs = qs.annotate(rel_count=Variance('story__categories'))

        return qs.order_by('-start', '-rel_count')


class CategoryGenera(models.Manager):
    def for_cloud(self, qs):
        return super(CategoryGenera, self).get_query_set().distinct().filter(story__publish__in=qs, browsable=True).annotate(occurances=Count('story')).values('id','title','keyname','occurances')
