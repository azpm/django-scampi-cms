import json
import logging
import re
from collections import namedtuple

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.html import escape
from django.http import Http404, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _

from .models import DynamicPicker, StaticPicker, PickerTemplate
from .forms import DynamicPickerInitialForm, DynamicPickerForm
from .picker import manifest, PickerError
from .utils import build_filters, coerce_filters, uncoerce_pickled_value
from .filtering import ContentTypeListFilter

logger = logging.getLogger('libscampi.contrib.cms.conduit.admin')


Pickable = namedtuple('Pickable', ('model', 'picker', 'filterset', 'factory'))


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
    list_select_related = ('commune', 'template', 'content')
    search_fields = ('commune__name',)

    fieldsets = (
        ('Designation', {'fields': ('name', 'active', ('keyname', 'commune'))}),  # TODO enable display_name
        ('Display', {'fields': ('template',)}),
        ('Picking', {'fields': ('content', 'max_count')}),
    )

    add_fieldsets = (
        (_('Designation'), {'fields': ('name', 'active', 'keyname')}),
        (_('Display'), {'fields': ('template',)}),
        (_('Picking'), {'fields': ('content', 'max_count')}),
    )

    save_on_top = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get('using')

        if db_field.name == "commune" and request.user.has_perm('conduit.change_picker_commune'):
            kwargs["widget"] = ForeignKeyRawIdWidget(db_field.rel, admin_site=self.admin_site, using=db)
        return super(DynamicPickerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

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

        # return super(DynamicPickerAdmin, self).get_readonly_fields(request, obj)

    # provide the JS for the picking filter magic
    class Media:
        js = (
            "admin/js/core.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
            'admin/js/conduit.pickers.js',
        )

    # we have the "adding a picker" form and the "changing the picker" form
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(DynamicPickerAdmin, self).get_fieldsets(request, obj)

    # again, special form for creating vs changing
    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            self.form = DynamicPickerInitialForm
        else:
            self.form = DynamicPickerForm

        return super(DynamicPickerAdmin, self).get_form(request, obj, **kwargs)

    # provide the serialization of the inclusion and exclusion filters
    def save_model(self, request, obj, form, change):
        logger.debug("saving %s [%s]" % (obj.name, obj.keyname))

        has_pickers = request.POST.get("includes-pickers", False)

        # basically only do something if we are "changing" e.g. the picking fields are available
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

    # override the urls method to add our picking form fields return
    def get_urls(self):

        urls = super(DynamicPickerAdmin, self).get_urls()

        my_urls = [
            url(r'^p/formfields/$', self.admin_site.admin_view(self.picking_filters_fields),
                name="conduit-picking-filters-fields"),
            url(r'^p/preview-objects/$', self.admin_site.admin_view(self.preview_picked_objects),
                name="conduit-picking-preview-picked"),
        ]

        return my_urls + urls

    def get_pickable(self, request):
        content_id = request.GET.get('content_id', None)
        picker_id = request.GET.get('picker_id', None)

        try:
            content_model = ContentType.objects.get(pk=content_id)
        except ContentType.DoesNotExist:
            raise Http404

        try:
            picker = DynamicPicker.objects.get(pk=picker_id)
        except DynamicPicker.DoesNotExist:
            picker = DynamicPicker.objects.none()

        model = content_model.model_class()
        if not manifest.is_registered(model):
            raise Http404

        if picker:
            form = self.get_form(request, picker)(request.POST, instance=picker)
        else:
            form = self.get_form(request)(request.POST)

        if not form.is_valid():
            raise Http404(form.errors)

        try:
            picking_filterset = manifest.get_registration_info(model)()
        except PickerError:
            raise Http404("Picking Filterset not found")

        factory = formset_factory(picking_filterset.form.__class__)

        return Pickable(model, form.instance, picking_filterset, factory)

    def preview_picked_objects(self, request, *args, **kwargs):
        model, picker, picking_filterset, factory = self.get_pickable(request)

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
        # first we handle any static defers - performance optimisation
        if hasattr(picking_filterset, 'static_defer'):
            defer = picking_filterset.static_defer()
            qs = qs.defer(*defer)

        # second we handle any static select_related fields - performance optimisation
        if hasattr(picking_filterset, 'static_select_related'):
            select_related = picking_filterset.static_select_related()
            qs = qs.select_related(*select_related)

        # third we handle any static prefetch_related fields - performance optimisation
        if hasattr(picking_filterset, 'static_prefetch_related'):
            prefetch_related = picking_filterset.static_prefetch_related()
            qs = qs.prefetch_related(*prefetch_related)

        # fourth we apply our inclusion filters
        for f in coerce_filters(inclusion_fs):
            qs = qs.filter(**f)

        # fifth we apply our exclusion filters
        for f in coerce_filters(exclusion_fs):
            qs = qs.exclude(**f)

        # before we limit the qs we let the picking filter set apply any last minute operations
        if hasattr(picking_filterset, 'static_chain') and callable(picking_filterset.static_chain):
            qs = picking_filterset.static_chain(qs)

        if not picker.max_count or picker.max_count > 10:
            limit = 10
        else:
            limit = picker.max_count

        ids = list(qs.values_list('id', flat=True)[:limit])

        picked = model.objects.filter(id__in=ids)
        # picked = model.objects.order_by('pk').in_bulk(ids)

        for_json = []
        for item in picked:
            for_json.append((item.pk, escape(repr(item))))

        response = HttpResponse(json.dumps(for_json), content_type="application/json")

        return response

    def picking_filters_fields(self, request, *args, **kwargs):
        model, picker, picking_filterset, factory = self.get_pickable(request)

        clean_produced = factory()
        clean_form = clean_produced[0]

        returns = {
            'existing': {},
            'filters': [(f.name, f.label, f.as_widget()) for f in clean_form],
        }
        base_fields = [f.name for f in clean_form]

        field_matcher = re.compile("^(%s)?" % "|".join(base_fields))
        incl = picker.include_filters
        excl = picker.exclude_filters

        def build_picking_fields(haystack):
            picking_fields = []
            for i, items in enumerate(haystack):
                picking_fields.append({})
                for key, val in items.iteritems():
                    match = field_matcher.match(key)
                    if match is not None:
                        picking_fields[i].update({match.group(): uncoerce_pickled_value(val)})
            return picking_fields

        incl_picking_fields = build_picking_fields(incl or [])
        excl_picking_fields = build_picking_fields(excl or [])

        def serialize_picking_fields(haystack):
            produced = factory(initial=haystack)
            serialized = []
            for i in range(len(produced) - 1):
                form = produced[i]
                serialized.append([])
                for field in form:
                    if field.name in haystack[i]:
                        serialized[i].append((field.name, field.label, field.__unicode__()))
            return serialized

        saved_inclusion = serialize_picking_fields(incl_picking_fields)
        saved_exclusion = serialize_picking_fields(excl_picking_fields)

        returns['existing'] = {'incl': saved_inclusion, 'excl': saved_exclusion}

        response = HttpResponse(json.dumps(returns), content_type="application/json")

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
