# -*- coding: utf-8 -*
from django.conf import settings

# Valid media extensions, edit at your own risk
valid_extensions = {
    'img': getattr(settings, 'VALID_IMG_EXT', ('.gif', '.jpg', '.jpeg', '.png')),
    'vid': getattr(settings, 'VALID_VID_EXT', ('.mov', '.mp4', '.m4v', '.flv', '.webm')),
    'aud': getattr(settings, 'VALID_AUD_EXT', ('.mp3', '.m4a')),
    'obj': getattr(settings, 'VALID_OBJ_EXT', ('.swf', '.xml')),
    'doc': getattr(settings, 'VALID_DOC_EXT', ('.doc', '.pdf', '.ppt')),
}

# Information quality for parsing metadata (0.0=fastest, 1.0=best, and default is 0.5)
INFO_QUALITY = getattr(settings, 'INFO_QUALITY', 1.0)

# Size of thumbnail to take for the admin preview
THUMB_SIZE = getattr(settings, 'THUMB_SIZE', (100, 80))

# Extra mime types to monkey patch to mimetypes.types_map
EXTRA_MIME_TYPES = getattr(settings, 'EXTRA_MIME_TYPES', {
    '.flv': 'video/x-flv',
    '.7z': 'application/x-7z-compressed',
    '.m4v': 'video/mp4',
    '.mp4': 'video/mp4',

})
