from django import template

from libscampi.contrib.cms.renaissance.models import Image, Video, Audio, Document, Object, External

register = template.Library()

class inline_media_node(template.Node):
    def __init__(self, type, slug, attrs):
        self.type = type
        self.slug = slug
        self.attrs = attrs
    
    def render(self, context):
        article = context.get('article', None)
        
        if not article:
            return u""
            
            
        inliner = {}
        if self.attrs is not None:
            attrs_split = self.attrs.split(',')
            for attr in attrs_split:
                inline_attr = attr.split('=')
                try:
                    inliner.update({inline_attr[0]: inline_attr[1]})
                except (AttributeError, ValueError):
                    continue
        
        if self.type not in ["image", "video", "audio", "document", "object", "external"]:
            return u""
            
        #inline for image
        if self.type == "image":
            try:
                media = article.image_inlines.get(slug=self.slug)
            except Image.DoesNotExist:
                media = Image.objects.none()
        
        #inline for video
        if self.type == "video":
            try:
                media = article.video_inlines.get(slug=self.slug)
            except Video.DoesNotExist:
                media = Video.objects.none()
        
        #inline for audio
        if self.type == "audio":
            try:
                media = article.audio_inlines.get(slug=self.slug)
            except Audio.DoesNotExist:
                media = Audio.objects.none()
            
        #inline for document
        if self.type == "document":
            try:
                media = article.document_inlines.get(slug=self.slug)
            except Document.DoesNotExist:
                media = Document.objects.none()
        
        #inline for object
        if self.type == "object":
            try:
                media = article.object_inlines.get(slug=self.slug)
            except Object.DoesNotExist:
                media = Object.objects.none()
            
        #inline for external
        if self.type == "external":
            try:
                media = article.external_inlines.get(slug=self.slug)
            except External.DoesNotExist:
                media = External.objects.none()
        
        
        #set the template
        try:
            inline_tpl = media.type.inline_template.content
        except AttributeError:
            inline_tpl = u""
        
        tpl = template.Template(inline_tpl)
        c = template.Context({'media': media, 'inliner': inliner})
        
        return tpl.render(c)
    
@register.tag('inline')
def render_inline_media(parser, token):
    try:
        tag, type, slug, attrs = token.split_contents()
    except ValueError:
        try:
            tag, type, slug = token.split_contents()
            attrs = None
        except ValueError:
            raise template.TemplateSyntaxError("'%s' requires two or three arguments: type, slug, optional attributes" % token.contents.split()[0])
        
    return inline_media_node(type, slug, attrs)