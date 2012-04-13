from django import template
from django.contrib.markup.templatetags.markup import markdown
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.simple_tag(takes_context=True)
def render_article_translation(context, article, translation):

    article_template = "%s %s" % ("{% load renaissance_private %}", translation['body'])
    c = template.Context({'article': article})

    try:
        tpl = template.Template(article_template, name="newsengine.ArticleTranslation private render")
        rendered = tpl.render(c)
    except template.TemplateSyntaxError:
        rendered = translation['body']

    return markdown(rendered)