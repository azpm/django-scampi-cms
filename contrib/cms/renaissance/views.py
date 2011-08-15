from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.http import Http404, HttpResponse, HttpResponseServerError
from django.contrib.sites.models import Site
from django import template

from libscampi.contrib.cms.renaissance.models import Image, Audio, Video, Document, Object

def view_media(request, type, slug):

    if type not in ["image", "video", "audio", "document", "object"]:
        return Http404("Media Type Undefined/Unkown")

    #view for image
    if type == "image":
        media = get_object_or_404(Image, slug=slug)
    
    #view for video
    if type == "video":
        media = get_object_or_404(Video, slug=slug)
    
    #view for audio
    if type == "audio":
        media = get_object_or_404(Audio, slug=slug)
        
    #view for document
    if type == "document":
        media = get_object_or_404(Document, slug=slug)
    
    #view for object
    if type == "object":
        media = get_object_or_404(Object, slug=slug)
        
    
    #set the template
    try:
        view_tpl = media.type.view_template.content
    except AttributeError:
        view_tpl = u""
        
    tpl = template.Template(view_tpl)
    c = template.RequestContext(request, {'media': media})
    
    return HttpResponse(tpl.render(c))