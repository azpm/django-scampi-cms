from django.conf.urls.defaults import *

from libscampi.contrib.django_filters.tests.models import Book

urlpatterns = patterns('',
    (r'^books/$', 'django_filters.views.object_filter', {'model': Book}),
)
