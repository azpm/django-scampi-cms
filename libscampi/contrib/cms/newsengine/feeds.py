import logging
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from libscampi.contrib.cms.conduit.models import DynamicPicker
from libscampi.contrib.cms.newsengine.models import Publish

logger = logging.getLogger("libscampi.contrib.cms.newsengine.feeds")

class PublishedStoryFeed(Feed):
    picker = None

    def get_object(self, request, *args, **kwargs):
        keyname = kwargs.pop("picker", None)
        self.picker = get_object_or_404(DynamicPicker, keyname=keyname)
        return self.picker

    def title(self, obj):
        return "{0:>s} - {1:>s} rss".format(obj.commune.realm.site.domain, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "{0:>s}".format(obj.name)

    def items(self, obj):
        qs = Publish.objects.distinct()
        exclude_these = ('start', 'end', 'end__isnull')

        #loop over the inclusion filters and update the qs
        if obj.include_filters:
            if isinstance(obj.include_filters, list):
                for f in obj.include_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) # this strips anything we don't want
                    qs = qs.filter(**f)
            else:
                logger.critical(
                    "invalid picker: cannot build archives from picker {0:>s} [id: {1:d}]".format(obj.name, obj.id))


        if obj.exclude_filters:
            if isinstance(obj.include_filters, list):
                for f in obj.exclude_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) #strips unneeded filters
                    qs = qs.exclude(**f)
            else:
                logger.critical(
                    "invalid picker: cannot build archives from picker {0:>s} [id: {1:d}]".format(obj.name, obj.id))

        return qs.order_by('-start')[:30]

    def item_link(self, item):
        return reverse('cms:publish:pubstory-detail', kwargs={'picker': self.picker.keyname, 'year': item.start.year, 'month': item.start.month, 'day': item.start.day, 'slug': item.slug})

    def item_title(self, item):
        return item.story.article.headline

    def item_description(self, item):
        if item.story.article.synopsis:
            return item.story.article.synopsis
        else:
            return item.story.article.sub_headline

    def item_author_name(self, item):
        return item.story.author.get_full_name()

    def item_pubdate(self, item):
        return item.start