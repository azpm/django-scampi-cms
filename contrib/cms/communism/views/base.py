from libscampi.contrib.cms.views.base import Page

class Index(Page):
    """
    Index/Commune landing page for Scampi CMS
    
    Index inherits from: libscamp.contrib.cms.views.base.Page which in turn inherits from:
    
    1. libscampi.contrib.cms.communism.views.mixins.CommuneMixin
    2. libscampi.contrib.cms.views.mixins.PageMixin
    3. libscampi.contrib.cms.communism.views.mixins.ThemeMixin
    4. libscampi.contrib.cms.communism.views.mixins.CSSMixin
    5. libscampi.contrib.cms.communism.views.mixins.JScriptMixin
    
    CommuneMixin provides several instance members:
        commune - :model:`communism.Commune`
        section - :model:`communism.Section`
        realm - :model:`communism.Realm`
    """