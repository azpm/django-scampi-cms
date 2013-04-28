from rest_framework import serializers
from libscampi.contrib.cms.newsengine.views.api import fields
from libscampi.contrib.cms.newsengine import models


class StoryCategorySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.StoryCategory


class StorySerializer(serializers.HyperlinkedModelSerializer):
    categories = serializers.RelatedField(source="visible_categories", many=True)
    related = fields.RelatedStoriesField(source="api_related_stories", many=True)
    peers = serializers.HyperlinkedRelatedField(queryset="api_peer_stories", many=True, view_name="cms:api:story-detail")
    headline = serializers.CharField(source="article.headline")
    sub_headline = serializers.CharField(source="article.sub_headline")
    author = serializers.CharField(source="author.get_full_name")

    _default_view_name = "cms:api:story-detail"

    class Meta:
        fields = ('url', 'author', 'headline', 'sub_headline', 'categories', 'peers', 'related', 'slug', 'important')
        model = models.Story


class PublishCategorySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.PublishCategory


class PublishSerializer(serializers.HyperlinkedModelSerializer):
    headline = serializers.CharField(source="story.article.headline")
    sub_headline = serializers.CharField(source="story.article.sub_headline")
    story = serializers.HyperlinkedRelatedField(source="story", view_name="cms:api:story-detail")
    category = serializers.RelatedField(source='category')
    author = serializers.CharField(source="story.author.get_full_name")

    _default_view_name = "cms:api:publish-detail"

    class Meta:
        fields = ('url', 'author', 'headline', 'sub_headline', 'story', 'slug', 'category', 'published', 'sticky')
        model = models.Publish

