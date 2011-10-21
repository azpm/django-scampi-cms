from libscampi.contrib.cms.newsengine.models import Publish

class PublishStoryMixin(object):
    #queryset = Publish.objects.all()

    model = Publish
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    date_field = 'start'
    