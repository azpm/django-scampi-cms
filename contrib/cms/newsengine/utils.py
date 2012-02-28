import math
import logging

from django.core.cache import cache
from django.db.models import Q, Max
from django.contrib.contenttypes.models import ContentType

from libscampi.contrib.cms.newsengine.models import StoryCategory

logger = logging.getLogger('libscampi.contrib.cms.newsengine.utils')

# Font size distribution algorithms
LOGARITHMIC, LINEAR = 1, 2

def _calculate_thresholds(min_weight, max_weight, steps):
    delta = (max_weight - min_weight) / float(steps)
    return [min_weight + i * delta for i in range(1, steps + 1)]

def _calculate_weight(weight, max_weight, distribution):
    """
    Logarithmic tag weight calculation is based on code from the
    `Tag Cloud`_ plugin for Mephisto, by Sven Fuchs.

    .. _`Tag Cloud`: http://www.artweb-design.de/projects/mephisto-plugin-tag-cloud
    """
    if distribution == LINEAR or max_weight == 1:
        return weight
    elif distribution == LOGARITHMIC:
        return math.log(weight) * max_weight / math.log(max_weight)
    raise ValueError(_('Invalid distribution algorithm specified: %s.') % distribution)

def calculate_cloud(categories, steps=4, distribution=LOGARITHMIC):
    """
    Add a ``font_size`` attribute to each category according to the
    frequency of its use, as indicated by its ``occurances``
    attribute.

    ``steps`` defines the range of font sizes - ``font_size`` will
    be an integer between 1 and ``steps`` (inclusive).

    ``distribution`` defines the type of font size distribution
    algorithm which will be used - logarithmic or linear. It must be
    one of ``LOGARITHMIC`` or ``LINEAR``.
    """
    if len(categories) > 0:
        counts = [category.occurances for category in categories]
        min_weight = float(min(counts))
        max_weight = float(max(counts))
        thresholds = _calculate_thresholds(min_weight, max_weight, steps)
        for category in categories:
            font_set = False
            weight = _calculate_weight(category.occurances, max_weight, distribution)
            for i in range(steps):
                if not font_set and weight <= thresholds[i]:
                    category.font_size = i + 1
                    font_set = True
    
    return categories
    
def cache_publishpicker_base_cats(sender, instance, **kwargs):
    if instance.content == ContentType.objects.get_by_natural_key('newsengine','Publish'):
        #every PublishPicking picker has base story categories that define it
        cat_cache_key = "picker:base:categories:%d" % instance.pk
        keep_these = ('story__categories__id__in','story__categories__id__exact')
        categories = set()
        
        if isinstance(instance.include_filters, list):
            for f in self.picker.include_filters:
                for k in f.keys():
                    if k in keep_these:
                        categories|=set(f[k]) #build a set of our base categories
        else:
            logger.critical("invalid picker: cannot build archives from picker %s [id: %d]" % (self.picker.name, self.picker.id))
            
        base_cats = StoryCategory.objects.filter(pk__in=categories, browsable=True)
        cache.set(cat_cache_key, base_cats, 60*60)