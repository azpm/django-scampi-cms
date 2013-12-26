import logging
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from libscampi.contrib.cms.conduit import models as conduit

logger = logging.getLogger('libscampi.contrib.cms.conduit.views')


class PickerMixin(object):
    picker = None
    base_categories = None

    def get(self, request, *args, **kwargs):
        """
        provides the picker to the view for base QuerySet limits
        """
        from libscampi.contrib.cms.newsengine import models as newsengine

        if 'picker' in kwargs:
            picker_key = kwargs.pop('picker')
            self.picker = get_object_or_404(conduit.DynamicPicker.objects.select_related('commune'), keyname=picker_key,
                                            active=True, commune__isnull=False)
        else:
            raise Http404

        if self.picker.content != ContentType.objects.get_by_natural_key('newsengine', 'publish'):
            raise Http404("Picker Archives only work for Published Stories")

        if self.picker.commune.realm.site_id != Site.objects.get_current().pk:
            redirect_url = "{0:>s}p/{1:>s}".format(self.picker.commune.realm.get_base_url(), self.picker.keyname)
            if 'year' in kwargs:
                redirect_url = "{0:>s}/{1:>s}".format(redirect_url, kwargs.pop('year'))
                if 'month' in kwargs:
                    redirect_url = "{0:>s}/{1:>s}".format(redirect_url, kwargs.pop('month'))
                    if 'day' in kwargs:
                        redirect_url = "{0:>s}/{1:>s}".format(redirect_url, kwargs.pop('day'))
                        if 'slug' in kwargs:
                            redirect_url = "{0:>s}/{1:>s}/".format(redirect_url, kwargs.pop('slug'))

            return redirect(redirect_url)

        categories = set()  # no result queryset evals to none, reset it to a blank set
        keep_these = ('story__categories__id__in', 'story__categories__id__exact')
        if isinstance(self.picker.include_filters, list):
            for f in self.picker.include_filters:
                for k in f.keys():
                    if k in keep_these:
                        categories |= set(f[k]) # build a set of our base categories
        else:
            logger.critical(
                "invalid picker: cannot build archives from picker {0:>s} [id: {1:d}]".format(self.picker.name,
                                                                                              self.picker.id))

        categories = newsengine.StoryCategory.objects.filter(pk__in=list(categories), browsable=True)

        self.base_categories = categories

        # add section to the graph by way of the picker
        kwargs.update({'keyname': self.picker.commune.keyname})

        return super(PickerMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        logger.debug("PickerMixin.get_context_data started")
        #get the existing context
        context = super(PickerMixin, self).get_context_data(*args, **kwargs)

        #give the template the current picker
        context.update({'picker': self.picker, 'base_categories': self.base_categories})
        logger.debug("PickerMixin.get_context_data ended")

        return context
