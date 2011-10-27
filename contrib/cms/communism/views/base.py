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
    ----
    
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
    
    context
    -------
    
    I am well aware that these aren't terrible consistent, this is for backwards compatibility.
    At some point, Scampi will be updated to have clean context variable names
    
    - commune -> self.commune (:model:`communism.Commune`)
    - CMS_SECTION -> self.section (:model:`communism.Section`)
    - CMS_REALM -> self.realm (:model:`communism.Realm`)
    
    ----
        
    PageMixin
    =========
    
    member variables
    ----------------
    
    - title unicode string
    - onload unicode string
    
    methods
    -------
    
    get_page_title
        Not Implemented, you must override this method to allow populating page.title
    
    get_page_onload
        Returns value of self.onload, can be overridden
        
    context
    -------
    
    page.title -> self.title
    page.onload -> self.onload
    
    ----
    
    ThemeMixin
    ==========
    
    Requires CommuneMixin
    
    context
    -------
    
    page.theme -> self.commune.theme
    
    ----
    
    CSSMixin
    =========
    
    methods
    -------
    
    get_stylesheets
        Returns cached html_link_refs of stylesheets or builds cache and returns collection
        Can be overridden to allow different stylesheet loading mechanisms
    
    context
    -------
    
    page.styles -> self.get_stylesheets()
    
    ----
    
    JScriptMixin
    ============
    
    methods
    -------
    
    get_javascripts
        Returns cached html_link_refs of javascripts or builds cache and returns collection
        Can be overridden to allow different js loading mechanisms
        
    context
    -------
    
    page.scripts -> self.get_javascripts()    
    """