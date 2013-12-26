import logging
import re
import json as simplejson
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.html import escape
from django.http import Http404, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _
from libscampi.contrib.cms.conduit.models import DynamicPicker, StaticPicker, PickerTemplate
from libscampi.contrib.cms.conduit.forms import DynamicPickerInitialForm, DynamicPickerForm
from libscampi.contrib.cms.conduit.picker import manifest, PickerError
from libscampi.contrib.cms.conduit.utils import build_filters, coerce_filters, uncoerce_pickled_value
from libscampi.contrib.cms.conduit.filtering import ContentTypeListFilter

__all__ = ['PickerTemplateAdmin', 'DynamicPickerAdmin', 'StaticPickerAdmin', 'StaticPickerInlineAdmin']

logger = logging.getLogger('libscampi.contrib.cms.conduit.admin')


class PickerTemplateAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Designation', {'fields': ['name']}),
        ('HTML Links', {'fields': ('stylesheet', 'javascript')}),
        (None, {'fields': ['content']}),
    )
    save_as = True
    save_on_top = True


class DynamicPickerAdmin(admin.ModelAdmin):
    list_display = ('name', 'keyname', 'active', 'commune', 'content', 'max_count', 'template')
    list_editable = ('max_count', 'template')
    list_filter = (ContentTypeListFilter, 'commune', 'active')
    search_fields = ('commune__name',)

    fieldsets = (
        #('Designation', {'fields': ('name', 'display_name', 'active', ('keyname', 'commune'))}), # TO DO enable display_name
        ('Designation', {'fields': ('name', 'active', ('keyname', 'commune'))}), # TO DO enable display_name
        ('Display', {'fields': ('template',)}),
        ('Picking', {'fields': ('content', 'max_count')}),
    )

    add_fieldsets = (
        (_('Designation'), {'fields': ('name', 'active', 'keyname')}),
        (_('Display'), {'fields': ('template', )}),
        (_('Picking'), {'fields': ('content', 'max_count')}),
    )

    save_on_top = True

    #provide the JS for the picking filter magic
    class Media:
        js = (
            "admin/js/core.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js',
            'admin/js/conduit.pickers.js',
        )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        db = kwargs.get('using')

        if db_field.name == "commune" and request.user.has_perm('conduit.change_picker_commune'):
            kwargs["widget"] = ForeignKeyRawIdWidget(db_field.rel, admin_site=self.admin_site, using=db)
        return super(DynamicPickerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        qs = super(DynamicPickerAdmin, self).queryset(request)

        return qs.prefetch_related('template', 'commune')

    def get_readonly_fields(self, request, obj=None):
        """
        commune can only be edited by super users
        content can only be set once
        """

        if obj:
            if request.user.has_perm('conduit.change_picker_commune'):
                return 'keyname', 'content'
            else:
                return 'commune', 'keyname', 'content'
        else:
            return 'active',

    #we have the "adding a picker" form and the "changing the picker" form
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(DynamicPickerAdmin, self).get_fieldsets(request, obj)

    #again, special form for creating vs changing
    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            self.form = DynamicPickerInitialForm
        else:
            self.form = DynamicPickerForm

        return super(DynamicPickerAdmin, self).get_form(request, obj, **kwargs)

    #provide the serialization of the inclusion and exclusion filters
    def save_model(self, request, obj, form, change):
        logger.debug("saving %s [%s]" % (obj.name, obj.keyname))

        has_pickers = request.POST.get("includes-pickers", False)

        #basically only do something if we are "changing" e.g. the picking fields are available
        if change and has_pickers:
            logger.debug("changing {0:>s} [{1:>s}]".format(obj.name, obj.keyname))

            content_model = obj.content.model_class()

            picking_filterset = manifest.get_registration_info(content_model)()

            factory = formset_factory(picking_filterset.form.__class__)
            inclusion = factory(request.POST, prefix="incl")
            exclusion = factory(request.POST, prefix="excl")

            inclusion_fs = []
            exclusion_fs = []

            if inclusion.is_valid():
                for form in inclusion:
                    setattr(picking_filterset, '_form', form)
                    try:
                        inclusion_fs.append(build_filters(picking_filterset))
                    except ValueError:
                        continue
            else:
                logger.debug("{0:>s} - inclusion was invalid: {1:>s}".format(obj.keyname, inclusion.errors))
                messages.error(request,
                               "There was an issue with the inclusion filters: {0:>s}".format(inclusion.errors))

            if exclusion.is_valid():
                for form in exclusion:
                    setattr(picking_filterset, '_form', form)
                    try:
                        exclusion_fs.append(build_filters(picking_filterset))
                    except ValueError:
                        continue
            else:
                logger.debug("{0:>s} - exclusion was invalid: {1:>s}".format(obj.keyname, inclusion.errors))
                messages.error(request,
                               "There was an issue with the exclusion filters: {0:>s}".format(exclusion.errors))

            logger.debug("[{0:>s}] final inclusion: {1:>s}".format(obj.name, inclusion_fs))
            logger.debug("[{0:>s}] final exclusion: {1:>s}".format(obj.name, exclusion_fs))

            obj.include_filters = inclusion_fs or False
            obj.exclude_filters = exclusion_fs or False

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
        from django.conf.urls import patterns, url

        urls = super(DynamicPickerAdmin, self).get_urls()

        my_urls = patterns('',
                           url(r'^p/formfields/$', self.admin_site.admin_view(self.picking_filters_fields),
                               name="conduit-picking-filters-fields"),
                           url(r'^p/preview-objects/$', self.admin_site.admin_view(self.preview_picked_objects),
                               name="conduit-picking-preview-picked"),
        )

        return my_urls + urls

    @staticmethod
    def preview_picked_objects(request, *args, **kwargs):
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

        model = content_model.model_class()
        if not manifest.is_registered(model):
            raise Http404

        try:
            picking_filterset = manifest.get_registration_info(model)()
        except PickerError:
            raise Http404("Picking Filterset not found")

        factory = formset_factory(picking_filterset.form.__class__)
        inclusion = factory(request.GET, prefix="incl")
        exclusion = factory(request.GET, prefix="excl")

        inclusion_fs = []
        exclusion_fs = []

        if inclusion.is_valid():
            for form in inclusion:
                setattr(picking_filterset, '_form', form)
                try:
                    inclusion_fs.append(build_filters(picking_filterset))
                except ValueError:
                    continue
        else:
            logger.debug("inclusion was invalid: {0:>s}".format(inclusion.errors))
            messages.error(request, "There was an issue with the inclusion filters: {0:>s}".format(inclusion.errors))

        if exclusion.is_valid():
            for form in exclusion:
                setattr(picking_filterset, '_form', form)
                try:
                    exclusion_fs.append(build_filters(picking_filterset))
                except ValueError:
                    continue
        else:
            logger.debug("exclusion was invalid: {0:>s}".format(inclusion.errors))
            messages.error(request, "There was an issue with the exclusion filters: {0:>s}".format(exclusion.errors))

        qs = model.objects.all()
        #first we handle any static defers - performance optimisation
        if hasattr(picking_filterset, 'static_defer'):
            defer = picking_filterset.static_defer()
            qs = qs.defer(*defer)

        #second we handle any static select_related fields - performance optimisation
        if hasattr(picking_filterset, 'static_select_related'):
            select_related = picking_filterset.static_select_related()
            qs = qs.select_related(*select_related)

        #third we handle any static prefetch_related fields - performance optimisation
        if hasattr(picking_filterset, 'static_prefetch_related'):
            prefetch_related = picking_filterset.static_prefetch_related()
            qs = qs.prefetch_related(*prefetch_related)

        #fourth we apply our inclusion filters
        if inclusion_fs:
            for f in inclusion_fs:
                if not f:
                    continue
                coerce_filters(f)
                qs = qs.filter(**f)

        #fifth we apply our exclusion filters
        if exclusion_fs:
            for f in exclusion_fs:
                if not f:
                    continue
                coerce_filters(f)
                qs = qs.exclude(**f)

        #before we limit the qs we let the picking filter set apply any last minute operations
        if hasattr(picking_filterset, 'static_chain') and callable(picking_filterset.static_chain):
            qs = picking_filterset.static_chain(qs)

        if not picker.max_count or picker.max_count > 10:
            limit = 10
        else:
            limit = picker.max_count

        ids = list(qs.values_list('id', flat=True)[:limit])

        picked = model.objects.filter(id__in=ids)
        #picked = model.objects.order_by('pk').in_bulk(ids)

        for_json = []
        for item in picked:
            for_json.append((item.pk, escape(repr(item))))

        response = HttpResponse(simplejson.dumps(for_json), content_type="application/json")

        return response

    @staticmethod
    def picking_filters_fields(request, *args, **kwargs):
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
        clean_produced = factory()
        clean_form = clean_produced[0]

        returns = {'existing': {}, 'filters': []}

        base_fields = []
        for field in clean_form:
            base_fields.append(field.name)
            returns['filters'].append((field.name, field.label, field.__unicode__()))

        field_matcher = re.compile("^(%s)?" % "|".join(base_fields))
        incl = picker.include_filters
        excl = picker.exclude_filters

        incl_picking_fields = []
        if incl:
            incl_sets = len(incl)
            for i in range(0, incl_sets):
                incl_picking_fields.append({})
                for key, val in incl[i].iteritems():
                    m = field_matcher.match(key)
                    if m is not None:
                        incl_picking_fields[i].update({m.group(): uncoerce_pickled_value(val)})

        excl_picking_fields = []
        if excl:
            excl_sets = len(excl)
            for i in range(0, excl_sets):
                excl_picking_fields.append({})
                for key, val in excl[i].iteritems():
                    m = field_matcher.match(key)
                    if m is not None:
                        excl_picking_fields[i].update({m.group(): uncoerce_pickled_value(val)})

        saved_inclusion = []
        saved_exclusion = []

        produced = factory(initial=incl_picking_fields)
        for i in range(0, len(produced) - 1):
            form = produced[i]
            saved_inclusion.append([])
            for field in form:
                if field.name in incl_picking_fields[i]:
                    saved_inclusion[i].append((field.name, field.label, field.__unicode__()))

        produced = factory(initial=excl_picking_fields)
        for i in range(0, len(produced) - 1):
            form = produced[i]
            saved_exclusion.append([])
            for field in form:
                if field.name in excl_picking_fields[i]:
                    saved_exclusion[i].append((field.name, field.label, field.__unicode__()))

        returns['existing'] = {'incl': saved_inclusion, 'excl': saved_exclusion}

        response = HttpResponse(simplejson.dumps(returns), content_type="application/json")

        return response


class StaticPickerAdmin(admin.ModelAdmin):
    list_display = ('name', 'namedbox')
    fieldsets = (
        (None, {'fields': ('name', 'content')}),
        ('Information', {'fields': ('namedbox', 'commune')}),
        ('HTML Links', {'fields': ('stylesheet', 'javascript')}),
    )
    save_on_top = True

    def get_readonly_fields(self, request, obj=None):
        """
        commune is always readonly
        content can only be set once
        """

        if obj:
            return 'commune', 'namedbox'
        else:
            return 'commune',


class StaticPickerInlineAdmin(admin.StackedInline):
    fieldsets = (
        (None, {'fields': ('name', 'content')}),
    )
    model = StaticPicker
    max_num = 1
    extra = 0
    verbose_name = "Static Content"
    verbose_name_plural = "Static Content"


admin.site.register(DynamicPicker, DynamicPickerAdmin)
admin.site.register(StaticPicker, StaticPickerAdmin)
admin.site.register(PickerTemplate, PickerTemplateAdmin)
