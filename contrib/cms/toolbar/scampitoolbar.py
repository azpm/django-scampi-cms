
class ScampiToolbar(object):
    def __init__(self, request):
        self.request = request
        self.setup()

    def setup(self):
        self.is_staff = self.request.user.is_staff
        self.show_toolbar = False
        self.scampi_managed = False
        self.cms_items = None