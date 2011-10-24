from django.views.generic.dates import *

from libscampi.contrib.cms.views.base import Page, PageNoView
from libscampi.contrib.cms.conduit.views.mixins import PickerMixin

from .mixins import PublishStoryMixin

class NewsEngineArchivePage(PublishStoryMixin, PageNoView, PickerMixin):
    """
    Base page for newsengine archives
    
    provides the picker-pruned initial queryset
    """
    def get_queryset(self):
        qs = self.model.objects.select_related().all()
        
        """
        this is a hardcoded "hack"
        
        the newsengine publish stories are displayed, by way of the CMS through
        dynamic pickers. Without having time to write a robust "archive" feature
        for dynamic pickers, we conclude that because contrib.CMS is not editable
        the Picking Filterset for Publish (published stories) is immutable and
        'start', 'end', 'end__isnull' are known keys of things we DON'T want to
        filter by for the archives.
        
        We do this because the archives themselves will exclude things that
        haven't been published yet, and will always show expired stories.
        """
        
        exclude_these = ('start', 'end', 'end__isnull')
        
        #loop over the inclusion filters and update the qs
        if self.picker.include_filters:
            if isinstance(self.picker.include_filters, list):
                for f in self.picker.include_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) #this strips anything we dont want
                    qs = qs.filter(**f)
            else:
                qs = qs.filter(**f)
        
        if self.picker.exclude_filters:
            if isinstance(self.picker.include_filters, list):
                for f in self.picker.exclude_filters:
                    for k in f.keys():
                        if k in exclude_these:
                            f.pop(k) #strips unneeded filters
                    qs = qs.exclude(**f)
            else:
                qs = qs.exclude(**f)
        
        
        return qs
        
    def get_context_data(self, *args, **kwargs):
        #get the existing context
        context = super(NewsEngineArchivePage, self).get_context_data(*args, **kwargs)
        
        #give the templat the current picker
        context.update({'picker': self.picker})
            
        return context


class PickedStoryIndex(NewsEngineArchivePage, ArchiveIndexView):
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/index.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/index.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/index.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/index.html" % self.commune.theme.keyname,
        )
        
        return tpl_list
    

class PickedStoryYearArchive(NewsEngineArchivePage, YearArchiveView):
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/year.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/year.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/year.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/year.html" % self.commune.theme.keyname,
        )
        
        return tpl_list

class PickedStoryMonthArchive(NewsEngineArchivePage, MonthArchiveView):
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/month.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/month.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/month.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/month.html" % self.commune.theme.keyname,
        )
        
        return tpl_list

class PickedStoryDayArchive(NewsEngineArchivePage, DayArchiveView):
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/day.html" % self.commune.theme.keyname,
        )
        
        return tpl_list
    
class PickerStoryTodayArchive(NewsEngineArchivePage, TodayArchiveView):  
    
    def get_template_names(self):
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/today.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/today.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/today.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/%s/day.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/today.html" % self.commune.theme.keyname,
            "%s/newsengine/archive/day.html" % self.commune.theme.keyname,
        )
        
        return tpl_list
    
class PickedStoryDetailArchive(NewsEngineArchivePage, DateDetailView):
    
    def get_template_names(self):
    
        tpl_list = (
            "%s/newsengine/archive/%s/%s/%s/%s.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname, self.object.slug),
            "%s/newsengine/archive/%s/%s/%s/detail.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname, self.picker.keyname),
            "%s/newsengine/archive/%s/%s/detail.html" % (self.commune.theme.keyname, self.realm.keyname, self.commune.keyname),
            "%s/newsengine/archive/%s/detail.html" % (self.commune.theme.keyname, self.realm.keyname),
            "%s/newsengine/archive/detail.html" % self.commune.theme.keyname,
        )
        
        return tpl_list