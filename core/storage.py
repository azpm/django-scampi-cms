from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os

class SCAMPIStorage(FileSystemStorage):
    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.BASE_MEDIA_URL):
        self.location = os.path.abspath(location)
        self.base_url = base_url