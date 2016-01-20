import logging

logger = logging.getLogger('libscampi.contrib.cms.views')

class PageMixin(object):
    title = None
    onload = None
    
    def get_context_data(self, *args, **kwargs):
        # it's okay pycharm
        context = super(PageMixin, self).get_context_data(*args, **kwargs)
        logger.debug("PageMixin.get_context_data started")
        if 'cms_page' in context:
            context['cms_page'].update({
                'title': self.get_page_title(),
                'onload': self.get_page_onload(),
                'description':self.get_page_description(),
            })
        else:
            if self.get_page_description:
                context.update({
                    'cms_page': {
                    'title': self.get_page_title(),
                    'onload': self.get_page_onload(),
                    'description':self.get_page_description(),
                }
            })
            else:
                context.update({
                    'cms_page': {
                        'title': self.get_page_title(),
                        'onload': self.get_page_onload(),
                    }
                })
        logger.debug("PageMixin.get_context_data ended")
        return context
        
    def get_page_title(self):
        if self.title is None:
            raise ValueError(
                "Page requires either a defintion of "
                "'title' or an implementation of 'get_page_title()'")
        else:
            return self.title
        
    def get_page_onload(self):
        return self.onload
        
def static_script(url):
    html_ref = type("legacy_script", (object,), {
        'file': type("legacy_file", (object, ), {'url': u""})()
    })
    
    t = html_ref()
    t.file.url = url
    
    return t
    
def static_style(url, media = "screen", for_ie = False):
    html_ref = type("legacy_style", (object,), {
        'for_ie': False,
        'media': u"",
        'file': type("legacy_file", (object, ), {'url': u""})()
    })
    
    t = html_ref()
    
    t.media = media
    t.for_ie = for_ie
    t.file.url = url
    
    return t
