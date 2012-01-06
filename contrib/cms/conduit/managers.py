from django.db import models

class DynamicPickerManager(models.Manager):
    def get_by_natural_key(self, commune, keyname):
        if commune:
            return self.get(commune__keyname = commune, keyname = keyname)
        else:
            return self.get(keyname = keyname)
            
class StaticPickerManager(models.Manager):
    def get_by_natural_key(self, commune, slice_order, gridy, gridx, display_order, keyname):
        return self.get(commune__keyname = commune, namedbox__slice__display_order = slice_order, namedbox__gridx = gridx, namedbox__gridy = gridy, namedbox__keyname = keyname)