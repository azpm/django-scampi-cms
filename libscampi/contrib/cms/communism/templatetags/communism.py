from classytags.arguments import Argument
from classytags.core import Tag, Options
from classytags.helpers import InclusionTag
from django import template
from django.contrib.sites.models import Site

from libscampi.contrib.cms.communism import models

register = template.Library()


class ThemeScripts(InclusionTag):
    name = "render_theme_scripts"
    template = "communism/scripts.html"

    options = Options(
        Argument('theme', required=False, resolve=False)
    )

    def get_context(self, context, **kwargs):
        keyname = kwargs.pop('theme', None)

        if not keyname:
            cms_page = context.get('cms_page', None)

            try:
                theme = cms_page['theme']
            except (KeyError, AttributeError, ValueError):
                # swallows errors and returns empty context
                return {}
        else:
            try:
                theme = models.Theme.objects.get_by_natural_key(keyname)
            except models.Theme.DoesNotExist:
                # invalid theme argument, empty context
                return {}

        scripts = theme.Javascript.base_active.for_theme(theme)

        return {'scripts': scripts}


class ThemeStyles(InclusionTag):
    name = "render_theme_styles"
    template = "communism/styles.html"

    options = Options(
        Argument('theme', required=False, resolve=False)
    )

    def get_context(self, context, **kwargs):
        keyname = kwargs.pop('theme', None)
        if not keyname:
            cms_page = context.get('cms_page', None)
            try:
                theme = cms_page['theme']
            except (KeyError, AttributeError, ValueError):
                # swallows errors and returns empty context
                return {}
        else:
            try:
                theme = models.Theme.objects.get_by_natural_key(keyname)
            except models.Theme.DoesNotExist:
                # invalid theme argument, empty context
                return {}

        styles = models.StyleSheet.base_active.for_theme(theme)

        return {'styles': styles}


class ThemePage(Tag):
    name = "get_themed_page"

    options = Options(
        Argument('theme', required=True, resolve=False),
    )

    def render_tag(self, context, **kwargs):
        cms_page = context.get('cms_page', None)
        keyname = kwargs.pop('theme', None)

        if cms_page is not None:
            return ''

        cms_page = {'theme': models.Theme.objects.none()}

        try:
            theme = models.Theme.objects.get_by_natural_key(keyname)
        except models.Theme.DoesNotExist:
            # invalid theme argument, empty context
            pass
        else:
            cms_page['theme'] = theme

        context['cms_page'] = cms_page

        return u''


class LocalRealm(Tag):
    name = "get_current_realm"

    def render_tag(self, context, **kwargs):
        cms_realm = context.get('cms_realm', None)

        if cms_realm is not None:
            return ''

        site = Site.objects.get_current()

        try:
            context['cms_realm'] = site.realm
        finally:
            return ''


register.tag(LocalRealm)
register.tag(ThemePage)
register.tag(ThemeScripts)
register.tag(ThemeStyles)
