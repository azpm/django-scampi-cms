from django.core.cache import cache
from libscampi.contrib.cms.conduit.models import DynamicPicker
from libscampi.contrib.cms.newsengine.models import Story, StoryCategory, Publish

def refresh_story_caches(sender, instance, **kwargs):
    pass

def refresh_all_caches():
    pass