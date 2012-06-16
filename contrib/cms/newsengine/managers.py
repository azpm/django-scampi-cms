from datetime import datetime, timedelta
from django.db import models
from django.db.models import Avg, Max, Min, Count, Q, Variance, StdDev
from django.contrib.contenttypes.models import ContentType

class PublishedManager(models.Manager):
    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)

    def find_related(self, story):
        cats = story.categories.values_list('keyname', flat=True)

        right_now = datetime.now()
        long_ago = right_now - timedelta(days=30)

        story_model = ContentType.objects.get_for_model(story).model_class()

        qs = story_model.objects.distinct().filter(
            Q(peers__in=[story]) | Q(categories__keyname__in=cats),
        ).exclude(pk=story.pk)
        qs = qs.annotate(rel_count=Count('categories')).order_by('-rel_count')

        return self.get_query_set().filter(story__in=[qs], start__lte=right_now, start__gte=long_ago)


class CategoryGenera(models.Manager):
    def for_cloud(self, qs):
        return super(CategoryGenera, self).get_query_set().distinct().filter(story__publish__in=qs, browsable=True).annotate(occurances=Count('story')).values('id','title','keyname','occurances')
