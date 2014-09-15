import re
from datetime import datetime
from django import template
from libscampi.contrib.cms.communism.models import *

register = template.Library()


class NotificationsNode(template.Node):
    def __init__(self, variable_name):
        self.variable_name = variable_name
    
    def render(self, context):
        try:
            notifications = RealmNotification.objects.filter(
                realm=context['cms_realm'],
                display_start__lte=datetime.now()
            ).exclude(
                display_end__lte=datetime.today(),
                display_end__isnull=False
            )
        except (ValueError, KeyError):
            notifications = RealmNotification.objects.none()
            
        context[self.variable_name] = notifications
        
        return ''

@register.tag
def get_notifications(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "{0!r:s} tag requires arguments".format(token.contents.split()[0])
    
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "{0!r:s} tag had invalid arguments".format(tag_name)
    try:
        variable_name = m.groups()[0]
    except IndexError:
        variable_name = "notifications"

    return NotificationsNode(variable_name)
