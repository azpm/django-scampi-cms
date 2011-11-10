from django import template

from libscampi.contrib.cms.newsengine.signals import ArticleNotChanged, ArticleChanged

def legacy_inline_images(sender, article, context, language, **kwargs):
    if not article:
        return ArticleNotChanged()
        
    md_body = getattr(article, "compiled_body_%s" % language, None)
    if not md_body:
        md_body = getattr(article, "body_%s" % language, None)
    if not md_body:
        md_body = article.body
    
    inlined_images = article.image_inlines.all()
    
    if len(inlined_images) > 0:
        md_friendly = "\n".join(["[%s]: %s" % (t.slug, t.file.url) for t in inlined_images])
        setattr(article, "compiled_body_%s" % language, "\n".join([md_body, md_friendly]))
    else:
        setattr(article, "compiled_body_%s" % language, md_body)
        
    return ArticleChanged()
    
def inlined_media(sender, article, context, language, **kwargs):
    if not article:
        return ArticleNotChanged()
        
    body = getattr(article, "compiled_body_%s" % language, None)
    if not body:
        body = getattr(article, "body_%s" % language, None)
    if not body:
        body = article.body
        
    article_template = "%s %s" % ("{% load renaissance_private %}", body)
    
    try:
        tpl = template.Template(article_template, name="newsengine.Article private render target")
        c = template.Context({'article': article})
        rendered = tpl.render(c)
    except template.TemplateSyntaxError:
        rendered = body
    
    
    setattr(article, "compiled_body_%s" % language, rendered)        
    return ArticleChanged()