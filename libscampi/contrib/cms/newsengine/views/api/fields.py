from rest_framework.reverse import reverse
from rest_framework import serializers
from libscampi.contrib.cms.newsengine import models

class RelatedStoriesField(serializers.RelatedField):
    def to_native(self, obj):
        request = self.context.get('request', None)

        return reverse("cms:api:story-detail", kwargs={'pk': obj.id}, request=request)

    class Meta:
        model = models.Story