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
        ('Designation', {'fields': ('name',)}),
        ('Display', {'fields': ('template',)}),
        ('Selectors', {'fields': ('content', 'max_count')}), 
    )
    
    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js',
            'http://ajax.microsoft.com/ajax/jquery.templates/beta1/jquery.tmpl.js',
            settings.MASTER_MEDIA_URL+'admin/js/conduit.pickers.js',
        )
    """
    def get_form(self, request, obj=None, **kwargs):
        if obj is not None:
            self.form = DynamicPickerFormForInstance
        elif obj is None:
            self.form = DynamicPickerForm
        return super(DynamicPickerAdmin, self).get_form(request, obj, **kwargs)
    """    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(DynamicPickerAdmin, self).get_urls()
        
        my_urls = patterns('',
            url(r'^picking/getformfields/$', self.admin_site.admin_view(self.picking_filters_fields), name="conduit-picking-filters-fields"),
            url(r'^picking/getform/$', self.admin_site.admin_view(self.picking_filters_form), name="conduit-picking-filters-form"),
            url(r'^picking/getresult/$', self.admin_site.admin_view(self.picking_filters_result), name="conduit-picking-filters-result"),
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
        
        returns = []
        for field in form:
            returns.append((field.name, field.label, field.__unicode__()))
            
        response = HttpResponse(simplejson.dumps(returns), content_type="application/json")
        
        return response
                
    def picking_filters_form(self, request, *args, **kwargs):            
        content_id = request.REQUEST.get('content_id', None)       
        picker_id = request.REQUEST.get('picker_id', None)
        method = request.REQUEST.get('method', '')
        
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
        
        if method not in ('include', 'exclude'):
            raise Http404
        
        picking_filterset = manifest.get_registration_info(content_model.model_class())()
        
        if method == 'include':
            existing_filters = picker.include_filters
        elif method == 'exclude':
            existing_filters = picker.exclude_filters
        
        context = {
            'content_id': content_id,
            'picker': picker,
            'method': method,
            'filter': picking_filterset,
            'model': content_model,
            'existing': existing_filters
        }
        
        context.update(csrf(request))
        
        return render_to_response("admin/conduit/widgets/picker_form.html", context)
        
    def picking_filters_result(self, request, *args, **kwargs):
        content_id = request.REQUEST.get('content_id', None)       
        picker_id = request.REQUEST.get('picker_id', None)
        method = request.REQUEST.get('method', '')
        
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
        
        if method not in ('include', 'exclude'):
            raise Http404
        
        picking_filterset = manifest.get_registration_info(content_model.model_class())(request.REQUEST)
        fs = build_filters(picking_filterset)
        
        if method == 'include':
            picker.include_filters = fs
            picker.save()
            return HttpResponse()
        elif method == 'exclude':
            picker.exclude_filters = fs
            picker.save()
            return HttpResponse()
            
        return HttpResponseServerError()

class StaticPickerInlineAdmin(admin.StackedInline):
    model = StaticPicker
    max_num = 1
    extra = 1
    verbose_name = "Static Content"
    verbose_name_plural = "Static Content"
    
admin.site.register(DynamicPicker, DynamicPickerAdmin)
admin.site.register(StaticPicker)
admin.site.register(PickerTemplate, PickerTemplateAdmin)