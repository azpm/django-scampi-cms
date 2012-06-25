from django import template
from django.contrib.markup.templatetags.markup import markdown

register = template.Library()

@register.simple_tag(takes_context=True)
def render_article_translation(context, article, translation):

    article_template = u"{0:>s} {1:>s}".format("{% load renaissance %}", translation['body'])
    c = template.Context({'article': article})

    try:
        tpl = template.Template(article_template, name="newsengine.ArticleTranslation private render")
        rendered = tpl.render(c)
    except template.TemplateSyntaxError:
        rendered = translation['body']

    return markdown(rendered)
