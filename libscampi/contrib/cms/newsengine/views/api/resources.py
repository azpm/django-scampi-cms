from rest_framework import generics, status
from rest_framework.response import Response
from datetime import timedelta, datetime

from libscampi.contrib.cms.newsengine import models
from libscampi.contrib.cms.newsengine.views.api import serializers


class StoryCategoryList(generics.ListAPIView):
    serializer_class = serializers.StoryCategorySerializer
    model = models.StoryCategory


class StoryList(generics.ListAPIView):
    serializer_class = serializers.StorySerializer
    model = models.Story

    paginate_by = 16
    paginate_by_param = 'page_size'

    def get_queryset(self):
        qs = super(StoryList, self).get_queryset()

        return qs.select_related('categories', 'author')


class StoryDetail(generics.RetrieveAPIView):
    serializer_class = serializers.StorySerializer
    model = models.Story

    def get_queryset(self):
        qs = super(StoryDetail, self).get_queryset()

        return qs.select_related('categories', 'author')


class PublishCategoryList(generics.ListAPIView):
    serializer_class = serializers.PublishCategorySerializer
    model = models.PublishCategory


class PublishList(generics.ListAPIView):
    serializer_class = serializers.PublishSerializer
    model = models.Publish

    paginate_by = 16
    paginate_by_param = 'page_size'

    def get_queryset(self):
        qs = super(PublishList, self).get_queryset()

        return qs.select_related('story', 'story__author', 'category')


class PublishDetail(generics.RetrieveAPIView):
    serializer_class = serializers.PublishSerializer
    model = models.Publish

    def get_queryset(self):
        qs = super(PublishDetail, self).get_queryset()

        return qs.select_related('story', 'story__author', 'category')