from django import forms
from django.contrib import admin
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseServerError
from django.contrib.contenttypes.models import ContentType
from django.core.context_processors import csrf
from django.utils import simplejson
from django.conf import settings
from django.forms.formsets import formset_factory


from .models import DynamicPicker, StaticPicker, PickerTemplate
from .forms import DynamicPickerForm, DynamicPickerFormForInstance
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
        ('Designation', {'fields': ('name', 'commune')}),
        ('Display', {'fields': ('template',)}),
        ('Selectors', {'fields': ('content', 'max_count')}), 
    )
    
    readonly_fields = ('commune',)
    
    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js',
            'http://ajax.microsoft.com/ajax/jquery.templates/beta1/jquery.tmpl.js',
            settings.MASTER_MEDIA_URL+'admin/js/conduit.pickers.js',
        )

    def get_form(self, request, obj=None, **kwargs):
        self.form = DynamicPickerForm
        return super(DynamicPickerAdmin, self).get_form(request, obj, **kwargs)
        
    def save_model(self, request, obj, form, change):
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
        
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(DynamicPickerAdmin, self).get_urls()
        
        my_urls = patterns('',
            url(r'^picking/getformfields/$', self.admin_site.admin_view(self.picking_filters_fields), name="conduit-picking-filters-fields"),
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
    model = StaticPicker
    max_num = 1
    extra = 1
    verbose_name = "Static Content"
    verbose_name_plural = "Static Content"
    
admin.site.register(DynamicPicker, DynamicPickerAdmin)
admin.site.register(StaticPicker)
admin.site.register(PickerTemplate, PickerTemplateAdmin)