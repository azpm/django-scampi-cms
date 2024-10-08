import logging
from datetime import datetime

from django import template
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
from django.contrib.sites.models import Site
from django.contrib.markup.templatetags.markup import markdown
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _, get_language_from_request
from django.contrib.comments.templatetags.comments import BaseCommentNode
from classytags.core import Tag, Options
from classytags.arguments import Argument, IntegerArgument

from libscampi.contrib.cms.newsengine.models import Article, Story
from libscampi.contrib.cms.newsengine.utils import calculate_cloud

register = template.Library()

logger = logging.getLogger('libscampi.contrib.cms.newsengine.templatetags')

class PublishedByAuthor(Tag):
    """
    {% recent_stories_by [author :model:`auth.User`] as [varname str] <limit optional int, default 3> %}

    returns: values query set of stories by author

    example:
        {% recent_stories_by pub.story.author as author_stories 6 %}
        {% for story in author_stories %}
            <a data-story-id="{{ story.id }}" href="{% url cms:story:story-detail story.slug %}" title="{{ story.article.headline }}">{{ story.article.headline }}</a><br/>
        {% endfor %}

    """
    name = "recent_stories_by"

    options = Options(
        Argument('author', required=True, resolve=True),
        'as',
        Argument('varname', required=True, resolve=False),
        IntegerArgument('limit', default=3, required=False, resolve=False),
    )

    def render_tag(self, context, **kwargs):
        author = kwargs.pop('author')
        varname = kwargs.pop('varname')
        limit = kwargs.pop('limit')

        cache_key = "stories:recent:by:{0:d}".format(author.id)
        related = cache.get(cache_key, None)

        if not related:
            logger.debug("missed authors story cache on {0:>s}".format(cache_key))

            right_now = datetime.now()
            related = Story.objects.filter(
                publish__published=True,
                publish__start__lte=right_now,
                author=author
            ).values('id','slug','article')[:limit]

            for item in related:
                item['article'] = Article.objects.get(pk=item['article'])

            cache.set(cache_key, list(related), 60*20)

        context[varname] = related

        return u""

register.tag(PublishedByAuthor)

class RenderArticle(Tag):
    """
    {% render_article [article :model:`newsengine.Article`] %}

    returns: a fully rendered article in users language, if available

    example: {% render_article publish.story.article %}
    """
    name = "render_article"

    options = Options(
        Argument('article', required=True, resolve=True),
        Argument('pref_lang', required=False, resolve=True),
    )

    def render_tag(self, context, **kwargs):


        article = kwargs.pop('article', None)
        p_lang = kwargs.pop('pref_lang', None)

        if not article:
            return ''

        try:
            lang = get_language_from_request(context['request'])
        except KeyError:
            lang = "en"

        #override the language from the URL, if specified
        if p_lang:
            lang = p_lang

        # try to get the article in the correct language default to RANDOM language if not available
        body = getattr(article, "body_%s" % lang, None)
        if not body:
            body = article.body

        # first pass, scampi 2.0+ style media
        tpl = template.Template(u" ".join(["{% load renaissance %}", body]), name="internal_article_tpl")
        c = template.Context({'article': article})
        first_pass = tpl.render(c)

        # second pass, scampi 1.0 style media
        inlined_images = article.image_inlines.all()
        if inlined_images.count() > 0:
            md_friendly = "\n".join([u"[%s]: %s" % (t.slug, t.file.url) for t in inlined_images])
            second_pass = "\n".join([first_pass, md_friendly])
        else:
            second_pass = first_pass


        final = markdown(second_pass)
        return final

register.tag(RenderArticle)

class RelatedStories(Tag):
    """
    {% related_stories [story :model:`newsengine.Story`] as [varname str] <limit optional int, default 3, max 10> %}

    returns: values query set of stories related to input story

    example:
        {% related_stories pub.story as rel_stories 6 %}
        {% for story in rel_stories %}
            <a data-story-id="{{ story.id }}" href="{% url cms:story:story-detail story.slug %}" title="{{ story.article.headline }}">{{ story.article.headline }}</a><br/>
        {% endfor %}

    """
    name = "related_stories"

    options = Options(
        Argument('story', required=True, resolve=True),
        'as',
        Argument('varname', required=True, resolve=False),
        IntegerArgument('limit', default=3, required=False, resolve=False),
    )

    def render_tag(self, context, **kwargs):
        story = kwargs.pop('story')
        varname = kwargs.pop('varname')
        limit = kwargs.pop('limit')

        if limit > 10:
            limit = 10

        cache_key = "stories:related:to:{0:d}".format(story.id)
        related = cache.get(cache_key, None)

        if not related:
            logger.debug("missed related story cache on {0:>s}".format(cache_key))
            related = story.related()[:limit]

            for item in related:
                item['article'] = Article.objects.get(pk=item['article'])

            cache.set(cache_key, list(related), 60*20)

        context[varname] = related

        return u""

register.tag(RelatedStories)

class StoryPermaLink(Tag):
    """
    {% story_permalink [story :model:`newsengine.Story`] %}

    returns: URL for a story

    example:
        {% story_permalink publish.story %}
    """
    name = "story_permalink"

    options = Options(
        Argument('story', required=True, resolve=True)
    )

    def render_tag(self, context, **kwargs):
        story = kwargs.pop('story')
        site = Site.objects.get_current()

        if story.publish_set.filter(Q(site__id = site.pk)|Q(site__isnull=True)).exists():
            return "{0:>2}{1:>s}".format(site.realm.get_base_url(), story.get_absolute_url())
        else:
            try:
                first_pub = story.publish_set.select_related('site__domain','realm__secure','site__realm').filter(site__isnull=False)[0]
            except IndexError:
                return ""
            else:
                return "{0:>2}{1:>s}".format(first_pub.site.realm.get_base_url(), story.get_absolute_url())

register.tag(StoryPermaLink)

class cloud_node(template.Node):
    def __init__(self, categories, context_var, **kwargs):
        self.categories = template.Variable(categories)
        self.context_var = context_var            
        self.kwargs = kwargs

    def render(self, context):
        context[self.context_var] = calculate_cloud(self.categories.resolve(context), **self.kwargs)
        return ''
    
@register.tag('category_cloud')
def category_cloud(parser, token):
    """
    Usage::

       {% category_cloud [categories] as [varname] %}


    Extended usage::

       {% category_cloud [categories] as [varname] with [options] %}

    Extra options can be provided after an optional ``with`` argument,
    with each option being specified in ``[name]=[value]`` format. Valid
    extra options are:

       ``steps``
          Integer. Defines the range of font sizes.

       ``min_count``
          Integer. Defines the minimum number of times a tag must have
          been used to appear in the cloud.

       ``distribution``
          One of ``linear`` or ``log``. Defines the font-size
          distribution algorithm to use when generating the tag cloud.

    """
    LOGARITHMIC, LINEAR = 1, 2

    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 4 and len_bits not in range(6, 9):
        raise template.TemplateSyntaxError(_('%s tag requires either three or between five and seven arguments') % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    kwargs = {}
    if len_bits > 5:
        if bits[4] != 'with':
            raise template.TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'with'") % bits[0])
        for i in range(5, len_bits):
            try:
                name, value = bits[i].split('=')
                if name == 'steps' or name == 'min_count':
                    try:
                        kwargs[str(name)] = int(value)
                    except ValueError:
                        raise template.TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid integer: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                elif name == 'distribution':
                    if value in ['linear', 'log']:
                        kwargs[str(name)] = {'linear': LINEAR, 'log': LOGARITHMIC}[value]
                    else:
                        raise template.TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid choice: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                else:
                    raise template.TemplateSyntaxError(_("%(tag)s tag was given an invalid option: '%(option)s'") % {
                        'tag': bits[0],
                        'option': name,
                    })
            except ValueError:
                raise template.TemplateSyntaxError(_("%(tag)s tag was given a badly formatted option: '%(option)s'") % {
                    'tag': bits[0],
                    'option': bits[i],
                })
    return cloud_node(bits[1], bits[3], **kwargs)
    
@register.simple_tag
def build_pagelist(pages, current_page, get_args = None):
    """
    {% build_pagelist [pages int] [current_page int] <get_args optional string> %}

    returns: html list elements <li> with class="active" for current page, 4 pages in each direction of current,
    if available

    example:
        <ul>
            {% build_pagelist paginator.page_range page_obj.number get_args %}
        </ul>
    """
    if current_page > pages[-1]:
        return u""

    list = []
    if current_page < 8:
        if current_page-4 > pages[0]:
            list = pages[current_page-4:current_page+4:1]
        else:
            max = 8-current_page
            list = pages[0:current_page+max:1]
    elif current_page >= 8:
        if current_page+4 < pages[-1]:
            list = pages[current_page-4:current_page+4:1]
        else:
            max = pages[-1] - current_page
            list = pages[current_page-4:current_page+max:1]
    
    if get_args:
        li = """<li {class:>s}><a href="?page={page:d}&{get_args:>s}">{page:d}</a></li>"""
    else:
        li = """<li {class:>s}><a href="?page={page:d}">{page:d}</a></li>"""
    html = []
    
    for page in list:
        if page == current_page:
            css = 'class="active"'
        else:
            css = ""
        
        if get_args:
            html.append(li.format(**{'class': css, 'page': page, 'get_args': get_args}))
        else:
            html.append(li.format(**{'class': css, 'page': page}))
            
    return "".join(html)
    
@register.simple_tag()
def chain_archival_categories(needle, haystack):
    """
    {% chain_archival_categories new current %}

    returns: ?c=new+current or ?c=new if current is empty
    """
    if haystack:
        category_path = "{0:>s}+{1:>s}".format("+".join([t.keyname for t in haystack]), needle['keyname'])
    else:
        category_path = "{0:>s}".format(needle['keyname'])
        
    url = "?c={0:>s}".format(category_path)
    
    return url
    
@register.simple_tag()
def dechain_archival_categories(needle, haystack):
    """
    {% dechain_archival_categories needle current %}

    returns: strips needle from current ?c=updated or ./ if current is empty
    """
    category_path= "{0:>s}".format("+".join([t.keyname for t in haystack if t.id != needle.id]))
    
    if category_path == '':
        url = "./"
    else:
        url = "?c={0:>s}".format(category_path)
    
    return url

# Some helpers for our ridiculously large website configuration & commenting

class xsite_BaseCommentNode(BaseCommentNode):
    """fetch comments without respect to a site"""
    def get_query_set(self, context):
        c_type, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.comment_model.objects.none()

        qs = self.comment_model.objects.filter(
            content_type = c_type,
            object_pk    = smart_unicode(object_pk),
        )

        # The is_public and is_removed fields are implementation details of the
        # built-in comment model's spam filtering system, so they might not
        # be present on a custom comment model subclass. If they exist, we
        # should filter on them.
        field_names = [f.name for f in self.comment_model._meta.fields]
        if 'is_public' in field_names:
            qs = qs.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True) and 'is_removed' in field_names:
            qs = qs.filter(is_removed=False)

        return qs
        
class xsite_CommentListNode(xsite_BaseCommentNode):
    """Insert a list of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return list(qs)

class xsite_CommentCountNode(xsite_BaseCommentNode):
    """Insert a count of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return qs.count()
        
@register.tag
def get_xsite_comment_count(parser, token):
    """
    see django.contrib.comments.templatetags.comments.get_comment_count
    """
    return xsite_CommentCountNode.handle_token(parser, token)
    
@register.tag
def get_xsite_comment_list(parser, token):
    """
    see django.contrib.comments.templatetags.comments.get_comment_list
    """
    return xsite_CommentListNode.handle_token(parser, token)
