from django import template
from django.template.loader import render_to_string
from django.core.cache import cache
from django.utils.safestring import mark_safe
from classytags.core import Tag, Options
from classytags.arguments import Argument

from libscampi.contrib.cms.renaissance.models import Image, Video, Audio, Document, Object, External
from libscampi.contrib.cms.newsengine.models import Article

TYPE_MAP = {"image": Image, "video": Video, "audio": Audio, "document": Document, "object": Object, "external": External}

register = template.Library()

class InlinedMedia(Tag):
    name = "inline"

    options = Options(
        Argument('type', required=True, resolve=False),
        Argument('slug', required=True, resolve=False),
        Argument('attrs', required=False, resolve=False),
    )

    def render_tag(self, context, type, slug, **kwargs):
        if type not in TYPE_MAP.keys():
            # if the type isn't recognized, just return an empty string
            return u""

        article = context.get('article', None)
        attributes = kwargs.pop("attrs", None)

        context_inliner = {}
        if attributes is not None:
            attrs = attributes.split(",")
            for attribute in attr:
                inline = attribute.split("=")
                try:
                    context_inliner.update({inline[0]: inline[1]})
                except (IndexError, AttributeError, ValueError):
                    continue

        mapped = TYPE_MAP[type]
        if type(article) is Article:
            m_getter = getattr(article, "%s_inlines" % type, None)
            if type != 'external':
                try:
                    media = m_getter.select_related('type__inline_template__content').get(slug=slug)
                except (mapped.DoesNotExit, AttributeError):
                    # if there's no media, or something went wrong, just return an empty string
                    return u""
            else:
                try:
                    media = m_getter.get(slug=slug)
                except (mapped.DoesNotExit, AttributeError):
                    # if there's no media, or something went wrong, just return an empty string
                    return u""
        else:
            if type != 'external':
                try:
                    media = mapped.objects.select_related('type__inline_template__content').get(slug=slug)
                except (mapped.DoesNotExit, AttributeError):
                    # if there's no media, or something went wrong, just return an empty string
                    return u""
            else:
                try:
                    media = mapped.objects.get(slug=slug)
                except (mapped.DoesNotExit, AttributeError):
                    # if there's no media, or something went wrong, just return an empty string
                    return u""

        if type == "external":
            return mark_safe(media.data)

        tpl = template.Template(media.type.inline_template.content, name="%s inline tpl" % type)
        c = template.Context({'media': media, 'inliner': context_inliner})

        return tpl.render(c)

register.tag(InlinedMedia)