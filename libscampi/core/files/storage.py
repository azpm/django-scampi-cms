from django.core.files.storage import DefaultStorage


class OverwriteStorage(DefaultStorage):
    """
    A simple storage engine that replaces an uploaded file
    """

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(OverwriteStorage, self)._save(name, content)

    def get_available_name(self, name):
        return name