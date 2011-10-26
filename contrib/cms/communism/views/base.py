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
    
    CommuneMixin 
    ============
    
    member variables
    ----------------
    
    - commune :model:`communism.Commune`
    - section :model:`communism.Section`
    - realm :model:`communism.Realm`
    
    methods
    -------
    
    get_page_title
        Sets the {{ page.title }} value to "realm.Name | commune.name"
        
    get_template_names
        Returns a list of possible templates to use: 
        1. <theme.keyname>/commune/<realm.keyname>/<commune.keyname>.html
        2. <theme.keyname>/commune/<realm.keyname>/generic.html
        3. <theme.keyname>/commune/generic.html
        
    
    """