import re
from datetime import datetime

from django import template
from django.utils.translation import ugettext_lazy as _

from libscampi.contrib.cms.communism.models import *

register = template.Library()

class notifications_node(template.Node):
    def __init__(self, varname):
        self.varname = varname
    
    def render(self, context):
        try:
            notifications = RealmNotification.objects.filter(realm = context['CMS_REALM'], display_start__lte=datetime.now()).exclude(display_end__lte=datetime.today(), display_end__isnull=False)
        except (ValueError, KeyError):
            notifications = RealmNotification.objects.none()
            
        context[self.varname] = notifications
        
        return ''
        
def get_notifications(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    try:
        varname = m.groups()[0]
    except:
        varname = "notifications"
        
    return notifications_node(varname)

register.tag('get_notifications', get_notifications)