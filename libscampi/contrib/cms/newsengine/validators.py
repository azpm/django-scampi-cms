from django.core.exceptions import ValidationError
from django.template import Template, TemplateEncodingError, TemplateSyntaxError

def validate_article(val):
    article_template = u"{0:>s} {1:>s}".format("{% load renaissance %}", val)

    try:
        Template(article_template)
    except (TemplateEncodingError, TemplateSyntaxError):
        raise ValidationError("Article has inline media errors")

