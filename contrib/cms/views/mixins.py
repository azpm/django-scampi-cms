class PageMixin(object):
    title = None
    onload = None
    
    def get_context_data(self, *args, **kwargs):
        context = super(PageMixin, self).get_context_data(*args, **kwargs)
        
        if 'page' in context:
            context['page'].update({
                'title': self.get_page_title(),
                'onload': self.get_page_onload(),
            })
        else:
            context.update({
                'page': {
                    'title': self.get_page_title(),
                    'onload': self.get_page_onload(),
                }
            })
            
        return context
        
    def get_page_title(self):
        if self.title is None:
            raise ImproperlyConfigured(
                "Page requires either a defintion of "
                "'title' or an implementation of 'get_page_title()'")
        else:
            return self.title
        
    def get_page_onload(self):
        return self.onload