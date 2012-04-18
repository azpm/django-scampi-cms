import urllib2

from django.core.files.storage import Storage, FileSystemStorage
from libscampi.core.files.storage import OverwriteStorage
from django.core.files.base import File

class URLStorage(Storage):
    def delete(self, name):
        raise NotImplementedError()

    def exists(self, name):
        return True

    def listdir(self, path):
        raise NotImplementedError()

    def size(self, name):
        return 0

    def url(self, name):
        return name

    def _open(self, name, mode):
        raise NotImplementedError()

    def _save(self, name, content):
        raise NotImplementedError()

    def get_available_name(self, name):
        raise NotImplementedError()

    def get_valid_name(self, name):
        raise NotImplementedError()