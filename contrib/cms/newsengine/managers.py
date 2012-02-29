from django.db import connection, models
from django.db.models import Avg, Max, Min, Count

class PublishedManager(models.Manager):
    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)
        
class CategoryGenera(models.Manager):
    def for_cloud(self, qs):
        return super(CategoryGenera, self).get_query_set().distinct().filter(story__publish__in=qs, browsable=True).annotate(occurances=Count('story')).values('id','title','keyname','occurances')
