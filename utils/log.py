import logging
from django.conf import settings

class RequireDebugTrue(logging.Filter):
    def filter(self, record):
        if record.levelno > 10 or settings.DEBUG:
            return True
        return False