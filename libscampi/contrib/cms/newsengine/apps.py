from django.apps import AppConfig


class NewsEngineConfig(AppConfig):
    name = 'libscampi.contrib.cms.newsengine'
    verbose_name = 'News Engine'

    def ready(self):
        from libscampi.contrib.cms.conduit import picker
        from .picking import PublishPicking
        publish = self.get_model('Publish')

        picker.manifest.register(publish, PublishPicking)
