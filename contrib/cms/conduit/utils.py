import logging

import django_filters

from datetime import datetime, timedelta
from django.core.cache import cache
from django.db.models.sql.constants import QUERY_TERMS
from django.utils.translation import ugettext_lazy as _
from django import forms

from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger('libscampi.contrib.cms.conduit.utils')

DATE_RANGE_COERCION = {
    '-today': lambda name, lookup: {'%s__%s' % (name, lookup): datetime.now()},
    '-past7days': lambda name, lookup: {'%s__%s' % (name, lookup): datetime.now() - timedelta(days=7)},
    '-thismonth': lambda name, lookup: {'%s__year' % name: datetime.today().year, '%s__month__%s' % (name, lookup): datetime.now().month},
    '-thisyear': lambda name, lookup: {'%s__year__%s' % (name,lookup): datetime.now().year},
}

DATE_RANGE_PICKLE_MAPPING = {
    1: lambda name, lookup: {'%s' % name: ('coerce-datetime', lookup, '-today')},
    2: lambda name, lookup: {'%s' % name: ('coerce-datetime', lookup, '-past7days')},
    3: lambda name, lookup: {'%s' % name: ('coerce-datetime', lookup, '-thismonth')},
    4: lambda name, lookup: {'%s' % name: ('coerce-datetime', lookup, '-thisyear')},
}

def build_filters(filterset):
    picking_form = filterset.form
    
    filters = {}
        
    for name, filter in filterset.filters.iteritems():
        fs = None
        try:
            #get the data from the cleaned form
            if picking_form.is_bound:
                data = picking_form[name].data
            else:
                data = picking_form.initial.get(name, picking_form[name].field.initial)
            value = picking_form.fields[name].clean(data)
            
            #see if the instance has a lookup associated with it
            if isinstance(value, (list, tuple)) and len(value) > 0:
                lookup = str(value[1])
                if not lookup:
                    lookup = 'exact'
                value = value[0]
            elif isinstance(value, (list, tuple)) and len(value) == 0:
                continue
            else:
                lookup = filter.lookup_type
            
            
            if type(filter) is django_filters.filters.ModelMultipleChoiceFilter:
                """
                Handle model multiple choice fields -- because django explicitly says
                pickled querysets DO NOT work across django versions we need to pickle
                a FOO__id__in: [LIST OF IDS] for the pickler
                """
                value = value or ()
                if not len(value) == len(list(picking_form.fields[name].choices)):
                    fs = {"%s__id__in" % filter.name: [t.pk for t in value]}
            elif type(filter) is django_filters.filters.ModelChoiceFilter:
                """
                handle single model choice fields, again because querysets are not likely
                to work across django versions we cannot pickle the QS we need to pickle
                proper qs lookup
                """
                if value is None:
                    continue
                fs = {"%s__id__%s" % (filter.name, lookup): value.pk}
            elif type(filter) is django_filters.filters.DateRangeFilter:
                """
                Handle daterange objects: django_filters says "today" is literally today, 
                at initial execute.  We must pickle a coercable concept so that date ranges
                are always proper at all execute times
                """
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    continue
                fs = DATE_RANGE_PICKLE_MAPPING[value](filter.name, lookup)
            elif value is not None:
                """
                this is a non-relational, non-datetime lookup
                """
                fs = {"%s__%s" % (filter.name, lookup): value}
                
            if fs:
                filters.update(fs)
                
        except forms.ValidationError:
            pass
    
    if len(filters) is 0:
        raise ValueError("No valid filters")
    
    return filters
    
def coerce_filters(filters):
    for key, value in filters.iteritems():
        if isinstance(value, tuple) and value[0] == 'coerce-datetime':
            try:
                newfilter = DATE_RANGE_COERCION[value[2]](key, value[1])
                del(filters[key])
                filters.update(newfilter)
            except (ValueError, KeyError, TypeError):
                continue
                
                
#map a picker (static or dynamic) to a commune
def map_picker_to_commune(sender, instance, **kwargs):
    commune = instance.slice.commune
    
    #give no fucks, set the commune even if it hasn't changed
    if instance.content:
        instance.content.commune = commune
        instance.content.save()        
        
    try:
        picker = instance.staticpicker
    except ObjectDoesNotExist:
        pass
    else:
        picker.commune = commune
        picker.save()
                
def unmap_orphan_picker(sender, instance, **kwargs):  
    #give no fucks, unset the commune
    if instance.content:
        instance.content.commune = None
        instance.content.save()
        
    try:
        picker = instance.staticpicker
    except ObjectDoesNotExist:
        pass
    else:
        picker.commune = None
        picker.save()
        
def cache_picker_template(sender, instance, **kwargs):
    cache_key = "conduit:dp:tpl:%d" % instance.pk
    tpl = instance.content
    cache.set(cache_key, tpl)
    
    logger.info("updating cached template %s [PickerTemplate]" % cache_key)


            