from libscampi.contrib.cms.newsengine.models import Publish

class PublishMixin(object):
    """
    Published Story Mixin for archives/pages
    
    Provides the model and appropriate field definitions to use Publish in view
    """

    model = Publish
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    date_field = 'start'
    month_format = '%m'
    paginate_by = 16
