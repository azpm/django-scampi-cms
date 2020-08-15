import re
from datetime import datetime

from django import template

from libscampi.contrib.cms.communism import models

register = template.Library()


class NotificationsNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        realm = context.get('cms_realm', None)
        if realm:
            notifications = models.RealmNotification\
                .objects\
                .filter(realm=realm, display_start__lte=datetime.now())\
                .exclude(display_end__lte=datetime.today(), display_end__isnull=False)
        else:
            notifications = models.RealmNotification.objects.none()

        context[self.varname] = notifications

        return ''


def get_notifications(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "{0!r:s} tag requires arguments".format(token.contents.split()[0])

    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "{0!r:s} tag had invalid arguments".format(tag_name)
    try:
        varname = m.groups()[0]
    except IndexError:
        varname = "notifications"

    return NotificationsNode(varname)


register.tag('get_notifications', get_notifications)
