import logging

from django.core.cache import cache
from django.db.models import Q
from libscampi.contrib.cms.communism.models import Javascript, StyleSheet
from libscampi.contrib.cms.communism.views.mixins import HtmlLinkRefs

logger = logging.getLogger("libscampi.contrib.cms.newsengine.views")

def story_stylesheets(story, theme, refresh_cache = False):
    article = story.article

    #try to get the cached css for this story / theme combination
    cached_css_key = 'theme:{0:d}:story:css:{1:d}'.format(story.id, theme.id)
    if refresh_cache:
        #invalidate on refresh_cache
        cache.delete(cached_css_key)
    styles = cache.get(cached_css_key, None)

    #cache empty, get the styles and refill the cache
    if not styles:
        logger.debug("missed css cache on {0:>s}".format(cached_css_key))

        playlist_filters = Q(base = True)

        if story.video_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id)
        if story.image_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id)
        if story.audio_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id)
        if story.document_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id)
        if story.object_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id)

        styles = StyleSheet.objects.filter(active=True, theme__id=theme.id).filter(
            #playlist finders
            playlist_filters |
            #inline finders
            Q(mediainlinetemplate__videotype__video__id__in=list(article.video_inlines.values_list('id', flat=True))) |
            Q(mediainlinetemplate__imagetype__image__id__in=list(article.image_inlines.values_list('id', flat=True))) |
            Q(mediainlinetemplate__audiotype__audio__id__in=list(article.audio_inlines.values_list('id', flat=True))) |
            Q(mediainlinetemplate__documenttype__document__id__in=list(article.document_inlines.values_list('id', flat=True))) |
            Q(mediainlinetemplate__objecttype__object__id__in=list(article.object_inlines.values_list('id', flat=True)))
        ).order_by('precedence').distinct()
        cache.set(cached_css_key, styles, 60*10)

    #build a simple collection of styles
    css_collection = HtmlLinkRefs()
    for style in styles:
        css_collection.add(style)

    return css_collection

def story_javascripts(story, theme, refresh_cache = False):
    article = story.article

    #try to get the cached javascript for this published story
    cached_scripts_key = 'theme:{0:d}:story:js:{1:d}'.format(story.id, theme.id)
    if refresh_cache:
        #invalidate on refresh_cache
        cache.delete(cached_scripts_key)
    script_ids = cache.get(cached_scripts_key, None)

    #cache empty, get the scripts and refill the cache
    if not script_ids:
        logger.debug("missed css cache on {0:>s}".format(cached_scripts_key))

        playlist_filters = Q(base = True)

        if story.video_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id)

        if story.image_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id)

        if story.audio_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id)

        if story.document_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id)

        if story.object_playlist:
            playlist_filters |= Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id)

        scripts = Javascript.objects.filter(active=True, theme__id=theme.id).filter(
            playlist_filters |
            #inline finders
            Q(mediainlinetemplate__videotype__video__id__in=list(article.video_inlines.values_list('id', flat=True))) |
            Q(mediainlinetemplate__imagetype__image__id__in=list(article.image_inlines.values_list('id', flat=True))) |
            Q(mediainlinetemplate__audiotype__audio__id__in=list(article.audio_inlines.values_list('id', flat=True))) |
            Q(mediainlinetemplate__documenttype__document__id__in=list(article.document_inlines.values_list('id', flat=True))) |
            Q(mediainlinetemplate__objecttype__object__id__in=list(article.object_inlines.values_list('id', flat=True)))
        ).order_by('precedence').distinct()
        cache.set(cached_scripts_key, list(scripts.values_list('id', flat = True)), 60*20)
    else:
        scripts = Javascript.objects.filter(id__in=script_ids).order_by('precedence')

    #build a simple collection of styles
    script_collection = HtmlLinkRefs()
    for script in scripts:
        script_collection.add(script)

    return script_collection