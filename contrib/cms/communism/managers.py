from django.db import models
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

__all__ = ['localised_section_manager', 'localised_element_manager', 'ThemeManager', 'BaseActiveLinkRefs','RealmManager', 'SectionManager', 'CommuneManager', 'SliceManager', 'NamedBoxManager', 'ApplicationManager']

class localised_section_manager(models.Manager):
    def get_query_set(self):
        return super(localised_section_manager, self).get_query_set().filter(realm__site=Site.objects.get_current())

class localised_element_manager(models.Manager):
    def get_query_set(self):
        return super(localised_element_manager, self).get_query_set().filter(section__realm__site=Site.objects.get_current())
        
class ThemeManager(models.Manager):
    def get_by_natural_key(self, keyname):
        return self.get(keyname = keyname)

class BaseActiveLinkRefs(models.Manager):
    def get_query_set(self):
        return super(BaseActiveLinkRefs, self).get_query_set().filter(base=True, active=True)

    def for_theme(self, theme):
        return self.get_query_set().filter(theme=theme).order_by('precedence')
        
class RealmManager(models.Manager):
    def get_by_natural_key(self, keyname):
        return self.get(keyname = keyname)
        
class SectionManager(models.Manager):
    def get_by_natural_key(self, realm, keyname):
        return self.get(realm__keyname = realm, keyname = keyname)

class CommuneManager(models.Manager):
    def get_query_set(self):
        qs = super(CommuneManager, self).get_query_set()

        c_type = ContentType.objects.get_for_model(self.model)


        return qs.extra(select={
            'r_order': """
                select cm.display_order from communism_realm cm
                inner join communism_section  on
                    (cm.id = communism_section.realm_id)
                where communism_section.element_type_id = %s
                and communism_section.element_id = communism_commune.id
            """,
            's_order': """
                select cs.display_order from communism_section cs
                where cs.element_type_id = %s
                and cs.element_id = communism_commune.id
            """
        }, select_params=[c_type.id,c_type.id], order_by=['r_order','s_order'])

    def get_by_natural_key(self, realm, section):
        return self.get(section__realm__keyname = realm, section__keyname = section)
        
class SliceManager(models.Manager):
    def get_by_natural_key(self, commune, display_order):
        return self.get(commune__keyname = commune, display_order = display_order)
        
class NamedBoxManager(models.Manager):
    def get_by_natural_key(self, commune, slice_order, grid_y, grid_x, display_order, keyname):
        return self.get(slice__commune__keyname = commune, slice__display_order = slice_order, gridx = grid_x, gridy = grid_y, display_order = display_order, pkeyname = keyname)
        
class ApplicationManager(models.Manager):
    def get_query_set(self):
        qs = super(ApplicationManager, self).get_query_set()

        c_type = ContentType.objects.get_for_model(self.model)

        return qs.extra(select={
            'r_order': """
                select cm.display_order from communism_realm cm
                inner join communism_section  on
                    (cm.id = communism_section.realm_id)
                where communism_section.element_type_id = %s
                and communism_section.element_id = communism_application.id
            """,
            's_order': """
                select cs.display_order from communism_section cs
                where cs.element_type_id = %s
                and cs.element_id = communism_application.id
            """
        }, select_params=[c_type.id,c_type.id], order_by=['r_order','s_order'])

    def get_by_natural_key(self, realm, section):
        return self.get(section__realm__keyname = realm, section__keyname = section)
