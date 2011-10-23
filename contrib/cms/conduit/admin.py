from django import forms
from django.contrib import admin
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseServerError
from django.contrib.contenttypes.models import ContentType
from django.core.context_processors import csrf
from django.utils import simplejson
from django.conf import settings
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext, ugettext_lazy as _

from .models import DynamicPicker, StaticPicker, PickerTemplate
from .forms import DynamicPickerForm
from .picker import manifest
from .utils import build_filters, coerce_filters

class PickerTemplateAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Designation', {'fields': ['name']}),
        ('HTML Links', {'fields': ('stylesheet', 'javascript')}), 
        (None, {'fields': ['content']}),
    )
    save_as = True
    


class DynamicPickerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Designation', {'fields': ('name', 'keyname', 'commune')}),
        ('Display', {'fields': ('template',)}),
        ('Picking', {'fields': ('content', 'max_count')}), 
    )
    
    add_fieldsets = (
        (_('Designation'), {'fields': ('name', 'keyname')}),
        (_('Display'), {'fields': ('template', )}),
        (_('Picking'), {'fields': ('content', 'max_count')}),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """
        commune is always readonly
        content can only be set once
        """
        
        if obj:
            return ('commune', 'keyname', 'content')
        
        return super(DynamicPickerAdmin, self).get_readonly_fields(request, obj)
    
    #provide the JS for the picking filter magic
    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js',
            'http://ajax.microsoft.com/ajax/jquery.templates/beta1/jquery.tmpl.js',
            settings.MASTER_MEDIA_URL+'admin/js/conduit.pickers.js',
        )

    #we have the "adding a picker" form and the "changing the picker" form
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(DynamicPickerAdmin, self).get_fieldsets(request, obj)

    #again, special form for creating vs changing
    def get_form(self, request, obj=None, **kwargs):
        
        if not obj:
            self.form = DynamicPickerForm
        
        return super(DynamicPickerAdmin, self).get_form(request, obj, **kwargs)
        
    #provide the serialization of the inclusion and exclusion filters
    def save_model(self, request, obj, form, change):
        
        #basically only do something if we are "changing" e.g. the picking fields are available
        if change:
            content_model = obj.content.model_class()
        
            picking_filterset = manifest.get_registration_info(content_model)()
            
            factory = formset_factory(picking_filterset.form.__class__)
            inclusion = factory(request.POST, prefix="incl")
            exclusion = factory(request.POST, prefix="excl")

            inclusion_fs = []
            if inclusion.is_valid():
                for form in inclusion:
                    setattr(picking_filterset, '_form', form)
                    inclusion_fs.append(build_filters(picking_filterset))
                    
            exclusion_fs = []
            if exclusion.is_valid():
                for form in exclusion:
                    setattr(picking_filterset, '_form', form)
                    exclusion_fs.append(build_filters(picking_filterset))
                    
            obj.include_filters = inclusion_fs
            obj.exclude_filters = exclusion_fs
            
        
        obj.save()
        
    def response_add(self, request, obj, post_url_continue='../%s'):
        """
        This method provides similar functionality to the User admin in django
        so that after a picker is created you are given the ability to build filters
        """
        if '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1
        
        return super(DynamicPickerAdmin, self).response_add(request, obj, post_url_continue)
        
    #override the urls method to add our picking form fields return
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(DynamicPickerAdmin, self).get_urls()
        
        my_urls = patterns('',
            url(r'^p/formfields/$', self.admin_site.admin_view(self.picking_filters_fields), name="conduit-picking-filters-fields"),
        )

        return my_urls + urls
        
    def picking_filters_fields(self, request, *args, **kwargs):            
        content_id = request.REQUEST.get('content_id', None)       
        picker_id = request.REQUEST.get('picker_id', None)
        
        try:
            content_model = ContentType.objects.get(pk=content_id)
        except ContentType.DoesNotExist:
            raise Http404
          
        try:
            picker = DynamicPicker.objects.get(pk=picker_id)
        except DynamicPicker.DoesNotExist:
            raise Http404
        
        if not manifest.is_registered(content_model.model_class()):
            raise Http404
        
        picking_filterset = manifest.get_registration_info(content_model.model_class())()
        
        factory = formset_factory(picking_filterset.form.__class__)
        produced = factory()
        form = produced[0]
        
        returns = {'existing': {}, 'filters': []}
        for field in form:
            returns['filters'].append((field.name, field.label, field.__unicode__()))
            
        returns['existing'] = {'incl': picker.include_filters, 'excl': picker.exclude_filters}
            
        response = HttpResponse(simplejson.dumps(returns), content_type="application/json")
        
        return response
                
class StaticPickerInlineAdmin(admin.StackedInline):
    readonly_fields = ('commune',)
    model = StaticPicker
    max_num = 1
    extra = 1
    verbose_name = "Static Content"
    verbose_name_plural = "Static Content"
    
admin.site.register(DynamicPicker, DynamicPickerAdmin)
admin.site.register(StaticPicker)
admin.site.register(PickerTemplate, PickerTemplateAdmin)