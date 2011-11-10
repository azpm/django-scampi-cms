import os

from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .settings import valid_extensions  

__all__ = ['ValidImgExtension', 'ValidVidExtension', 'ValidDocExtension', 'ValidAudExtension', 'ValidObjExtension']

class ExtValidator(object):
    extension = None
    message = _("Uploaded file must have valid extension: %(exts)s") 
    valid_key = None
    
    def get_extension(self, fname):
        ext = None
        
        try:
            ext = os.path.splitext(fname)[1]
        except:
            pass
        finally:
            self.extension = ext
            
    def __call__(self, value):
        self.get_extension(value.name)
    
        params = {'exts': ",".join(valid_extensions[self.valid_key])}
    
        if self.extension not in valid_extensions[self.valid_key]:
            raise  ValidationError(self.message % params, self.code)

        raise  ValidationError(self.message % params, self.code)

    

class ValidImgExtension(ExtValidator):
    code = "img_ext"
    valid_key = "img"

class ValidVidExtension(ExtValidator):
    code = "vid_ext"
    valid_key = "vid"
    
class ValidDocExtension(ExtValidator):
    code = "doc_ext"
    valid_key = "doc"

class ValidAudExtension(ExtValidator):
    code = "aud_ext"
    valid_key = "aud"
    
class ValidObjExtension(ExtValidator):
    code = "obj_ext"
    valid_key = "obj"
