from libscampi.contrib.cms.newsengine.models import Publish

class PublishStoryeMixin(object):
    model = Publish
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    