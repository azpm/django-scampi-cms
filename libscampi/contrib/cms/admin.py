from django.contrib.admin.sites import AdminSite
from libscampi.contrib.cms.renaissance import models as renaissance_models, admin as renaissance_admin
from libscampi.contrib.cms.conduit import models as conduit_models, admin as conduit_admin
from libscampi.contrib.cms.communism import models as communism_models, admin as communism_admin
from libscampi.contrib.cms.newsengine import models as newsengine_models, admin as newsengine_admin

cms_admin = AdminSite()

# Admin for communism
cms_admin.register(communism_models.Theme)
cms_admin.register(communism_models.StyleSheet, communism_admin.GenericDOMElementAdmin)
cms_admin.register(communism_models.Javascript, communism_admin.GenericDOMElementAdmin)
cms_admin.register(communism_models.Realm, communism_admin.RealmAdmin)
cms_admin.register(communism_models.RealmNotification, communism_admin.RealmNotificationAdmin)
cms_admin.register(communism_models.Section, communism_admin.SectionAdmin)
cms_admin.register(communism_models.Slice, communism_admin.SliceAdmin)
cms_admin.register(communism_models.NamedBox, communism_admin.BoxAdmin)
cms_admin.register(communism_models.Commune, communism_admin.CommuneAdmin)
cms_admin.register(communism_models.Application, communism_admin.ApplicationAdmin)

# Admin for conduit
cms_admin.register(conduit_models.DynamicPicker, conduit_admin.DynamicPickerAdmin)
cms_admin.register(conduit_models.StaticPicker)
cms_admin.register(conduit_models.PickerTemplate, conduit_admin.PickerTemplateAdmin)

# Admin for newsengine
cms_admin.register(newsengine_models.Article, newsengine_admin.ArticleAdmin)
cms_admin.register(newsengine_models.ArticleTranslation)
cms_admin.register(newsengine_models.StoryCategory)
cms_admin.register(newsengine_models.Story, newsengine_admin.StoryAdmin)
cms_admin.register(newsengine_models.PublishCategory, newsengine_admin.PublishCategoryAdmin)
cms_admin.register(newsengine_models.Publish, newsengine_admin.PublishStoryAdmin)

# Admin for renaissance
cms_admin.register(renaissance_models.Image, renaissance_admin.FileBasedMediaAdmin)
cms_admin.register(renaissance_models.Video, renaissance_admin.FileBasedMediaAdmin)
cms_admin.register(renaissance_models.Audio, renaissance_admin.FileBasedMediaAdmin)
cms_admin.register(renaissance_models.Document, renaissance_admin.FileBasedMediaAdmin)
cms_admin.register(renaissance_models.Object, renaissance_admin.FileBasedMediaAdmin)
cms_admin.register(renaissance_models.External, renaissance_admin.ExternalAdmin)

cms_admin.register(renaissance_models.ImagePlaylist, renaissance_admin.ImagePlaylistAdmin)
cms_admin.register(renaissance_models.VideoPlaylist, renaissance_admin.VideoPlaylistAdmin)
cms_admin.register(renaissance_models.AudioPlaylist, renaissance_admin.AudioPlaylistAdmin)
cms_admin.register(renaissance_models.DocumentPlaylist, renaissance_admin.DocumentPlaylistAdmin)
cms_admin.register(renaissance_models.ObjectPlaylist, renaissance_admin.ObjectPlaylistAdmin)

cms_admin.register(renaissance_models.ImageType, renaissance_admin.DimensionalMediaTypeAdmin)
cms_admin.register(renaissance_models.VideoType, renaissance_admin.DimensionalMediaTypeAdmin)
cms_admin.register(renaissance_models.ObjectType, renaissance_admin.DimensionalMediaTypeAdmin)
cms_admin.register(renaissance_models.AudioType, renaissance_admin.MediaTypeAdmin)
cms_admin.register(renaissance_models.DocumentType, renaissance_admin.MediaTypeAdmin)

cms_admin.register(renaissance_models.MediaInlineTemplate)
cms_admin.register(renaissance_models.MediaPlaylistTemplate)