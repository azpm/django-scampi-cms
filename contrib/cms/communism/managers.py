from django.db import models
from django.contrib.sites.models import Site

class localised_section_manager(models.Manager):
    def get_query_set(self):
        return super(localised_section_manager, self).get_query_set().filter(realm__site=Site.objects.get_current())

class localised_element_manager(models.Manager):
    def get_query_set(self):
        return super(localised_element_manager, self).get_query_set().filter(section__realm__site=Site.objects.get_current())