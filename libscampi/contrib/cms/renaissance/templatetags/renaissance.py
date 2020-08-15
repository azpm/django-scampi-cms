from django import template
from django.utils.safestring import mark_safe
from classytags.core import Tag, Options
from classytags.arguments import Argument

from libscampi.contrib.cms.renaissance.models import Image, Video, Audio, Document, Object, External
from libscampi.contrib.cms.newsengine.models import Article

TYPE_MAP = {"image": Image, "video": Video, "audio": Audio, "document": Document, "object": Object,
            "external": External}

register = template.Library()


class InlinedMedia(Tag):
    name = "inline"

    options = Options(
        Argument('media_type', required=True, resolve=False),
        Argument('slug', required=True, resolve=False),
        Argument('attrs', required=False, resolve=False),
    )

    def render_tag(self, context, **kwargs):
        media_type, slug = kwargs.pop('media_type'), kwargs.pop('slug')

        if media_type not in TYPE_MAP.keys():
            # if the type isn't recognized, just return an empty string
            return u""

        article = context.get('article', None)
        attributes = kwargs.pop("attrs", None)

        context_inliner = {}
        if attributes is not None:
            attrs = attributes.split(",")
            for attribute in attrs:
                inline = attribute.split("=")
                try:
                    context_inliner.update({inline[0]: inline[1]})
                except (IndexError, AttributeError, ValueError):
                    continue

        mapped = TYPE_MAP[media_type]
        if type(article) is Article:
            m_getter = getattr(article, "{0:>s}_inlines".format(media_type), None)
            if media_type != 'external':
                try:
                    media = m_getter.select_related('type__inline_template__content').get(slug=slug)
                except (mapped.DoesNotExist, AttributeError):
                    # if there's no media, or something went wrong, just return an empty string
                    return u""
            else:
                try:
                    media = m_getter.get(slug=slug)
                except (mapped.DoesNotExist, AttributeError):
                    # if there's no media, or something went wrong, just return an empty string
                    return u""
        else:
            if media_type != 'external':
                try:
                    media = mapped.objects.select_related('type__inline_template__content').get(slug=slug)
                except (mapped.DoesNotExist, AttributeError):
                    # if there's no media, or something went wrong, just return an empty string
                    return u""
            else:
                try:
                    media = mapped.objects.get(slug=slug)
                except (mapped.DoesNotExist, AttributeError):
                    # if there's no media, or something went wrong, just return an empty string
                    return u""

        if media_type == "external":
            return mark_safe(media.data)

        tpl = template.Template(media.type.inline_template.content, name="{0:>s} inline tpl".format(media_type))
        c = template.Context({'media': media, 'inliner': context_inliner})

        return tpl.render(c)


register.tag(InlinedMedia)
