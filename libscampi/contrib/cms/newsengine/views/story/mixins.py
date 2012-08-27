from libscampi.contrib.cms.newsengine.models import Story

class StoryMixin(object):
    paginate_by = 16
    model = Story
    slug_field = "slug"
    slug_url_kwarg = "slug"