#
#  context_processors.py
#  
#
#  Created by Joey Leingang on 12/7/07.
#  Copyright (c) 2007 Arizona Board Of Regents. All rights reserved.
#

from django.conf import settings
import re

def local_media(request):
    return {'LOCAL_MEDIA_URL': settings.MEDIA_URL}
    
def master_media(request):
    return {'MASTER_MEDIA_URL': settings.MASTER_MEDIA_URL}
    
def current_section(request):
    current_section = request.path.split('/',2)
    return {'CURRENT_SECTION_KEYNAME': current_section[1]}