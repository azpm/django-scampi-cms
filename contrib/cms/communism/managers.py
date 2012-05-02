from django.db import models
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

__all__ = ['localised_section_manager', 'localised_element_manager', 'ThemeManager', 'RealmManager', 'SectionManager', 'CommuneManager', 'SliceManager', 'NamedBoxManager', 'ApplicationManager']

class localised_section_manager(models.Manager):
    def get_query_set(self):
        return super(localised_section_manager, self).get_query_set().filter(realm__site=Site.objects.get_current())

class localised_element_manager(models.Manager):
    def get_query_set(self):
        return super(localised_element_manager, self).get_query_set().filter(section__realm__site=Site.objects.get_current())
        
class ThemeManager(models.Manager):
    def get_by_natural_key(self, keyname):
        return self.get(keyname = keyname)
        
class RealmManager(models.Manager):
    def get_by_natural_key(self, keyname):
        return self.get(keyname = keyname)
        
class SectionManager(models.Manager):
    def get_by_natural_key(self, realm, keyname):
        return self.get(realm__keyname = realm, keyname = section)
        
class CommuneManager(models.Manager):
    def get_query_set(self):
        qs = super(CommuneManager, self).get_query_set()

        ctype = ContentType.objects.get_for_model(self.model)

        return qs.extra(select={
            'r_order': """
                select display_order from communism_realm
                inner join communism_section on
                    (
                        communism_realm.id = communism_section.realm_id
                        and communism_section.element_type_id = %d
                        and communism_section.element_id = communism_commune.id
                    )
            """,
            's_order': """
                select display_order from communism_section cs
                where cs.element_type_id = %d
                and cs.element_id = communism_commune.id
            """
        }, select_params=[ctype.id], order_by=['r_order','s_order'])

    def get_by_natural_key(self, realm, section):
        return self.get(section__realm__keyname = realm, section__keyname = section)
        
class SliceManager(models.Manager):
    def get_by_natural_key(self, commune, display_order):
        return self.get(commune__keyname = commune, display_order = display_order)
        
class NamedBoxManager(models.Manager):
    def get_by_natural_key(self, commune, slice_order, gridy, gridx, display_order, keyname):
        return self.get(slice__commune__keyname = commune, slice__display_order = slice_order, gridx = gridx, gridy = gridy, display_order = display_order, pkeyname = keyname)
        
class ApplicationManager(models.Manager):
    def get_by_natural_key(self, realm, section):
        return self.get(section__realm__keyname = realm, section__keyname = section)