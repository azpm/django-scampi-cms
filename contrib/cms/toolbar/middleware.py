import thread
from libscampi.contrib.cms.toolbar.scampitoolbar import ScampiToolbar

_HTML_TYPES = ('text/html', 'application/xhtml+xml')

class ScampiToolbarMiddleware(object):
    def process_request(self, request):
        request.toolbar = ScampiToolbar(request)