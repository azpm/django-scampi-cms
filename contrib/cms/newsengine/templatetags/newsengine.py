from datetime import datetime

from django import template
from django.core.cache import cache
from django.conf import settings
from django.contrib.markup.templatetags.markup import markdown
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.templatetags.comments import BaseCommentNode

from libscampi.contrib.cms.conduit.models import *
from libscampi.contrib.cms.newsengine.utils import calculate_cloud
from libscampi.contrib.cms.newsengine.signals import SolidSender, preprocess_article, postprocess_article


register = template.Library()

class article_node(template.Node):
    def __init__(self, article):
        self.article = template.Variable(article)
    
    def render(self, context):
        try:
            article = self.article.resolve(context)
        except template.VariableDoesNotExist:
            return u""
        
        language_code = context['request'].LANGUAGE_CODE
        refresh_cache = context['request'].GET.get('refresh_cache', False)
        
        key = 'article:compiled:%s:%s' % (language_code, article.pk)
        html = cache.get(key, None)
        if refresh_cache or not html or article.modified > html['ts']:        
            preprocess_article.send(sender=SolidSender, article=article, context=context, language=language_code)
            postprocess_article.send(sender=SolidSender, article=article, context=context, language=language_code)
            
            html = {'ts': datetime.now(),'html': markdown(getattr(article, "compiled_body_%s" % language_code, article.body))}
            cache.set(key, html, 60*60)
                
        return html['html']       
    
@register.tag('render_article')
def render_article(parser, token):
    try:
        tag, article = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("'%s' requires an argument: an article" % token.contents.split()[0])
        
    return article_node(article)
    
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
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 4 and len_bits not in range(6, 9):
        raise TemplateSyntaxError(_('%s tag requires either three or between five and seven arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    kwargs = {}
    if len_bits > 5:
        if bits[4] != 'with':
            raise TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'with'") % bits[0])
        for i in range(5, len_bits):
            try:
                name, value = bits[i].split('=')
                if name == 'steps' or name == 'min_count':
                    try:
                        kwargs[str(name)] = int(value)
                    except ValueError:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid integer: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                elif name == 'distribution':
                    if value in ['linear', 'log']:
                        kwargs[str(name)] = {'linear': LINEAR, 'log': LOGARITHMIC}[value]
                    else:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid choice: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                else:
                    raise TemplateSyntaxError(_("%(tag)s tag was given an invalid option: '%(option)s'") % {
                        'tag': bits[0],
                        'option': name,
                    })
            except ValueError:
                raise TemplateSyntaxError(_("%(tag)s tag was given a badly formatted option: '%(option)s'") % {
                    'tag': bits[0],
                    'option': bits[i],
                })
    return cloud_node(bits[1], bits[3], **kwargs)
    
"""
Some helpers for our ridiculously large website configuration & commenting
"""

class xsite_BaseCommentNode(BaseCommentNode):
    """fetch comments without resepct to a site"""
    def get_query_set(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.comment_model.objects.none()

        qs = self.comment_model.objects.filter(
            content_type = ctype,
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