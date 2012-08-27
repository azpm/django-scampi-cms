import threading
from django.core.urlresolvers import reverse

scampi_locals = threading.local()

class DjangoAdmin(object):
    def process_view(self, request, view_func, args, kwargs):
        if request.path.startswith(reverse('admin:index')):
            scampi_locals.admin = True
        else:
            scampi_locals.admin = False

        return None

