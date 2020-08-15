import math
import logging

from django.utils.translation import ugettext_lazy as _

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
        counts = [category['occurances'] for category in categories]
        min_weight = float(min(counts))
        max_weight = float(max(counts))
        thresholds = _calculate_thresholds(min_weight, max_weight, steps)
        for category in categories:
            font_set = False
            weight = _calculate_weight(category['occurances'], max_weight, distribution)
            for i in range(steps):
                if not font_set and weight <= thresholds[i]:
                    category['font_size'] = i + 1
                    font_set = True

    return categories



