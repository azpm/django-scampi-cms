from django.db.models import fields
from django.db.models import signals
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext_lazy as _

PREFER_FILE = 1
PREFER_URL = 2

class URLorFileField(fields.Field):
    description = _("File or URL")

    def __init__(self, verbose_name = None, name=None, upload_to=None, storage=None, prefer=PREFER_FILE, **kwargs):
        # TODO Finish this model
        pass