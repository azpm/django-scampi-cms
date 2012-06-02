from django.template import Library
from classytags.core import Tag, Options
from classytags.arguments import Argument, Flag
from classytags.helpers import InclusionTag, AsTag

from libscampi.contrib.cms.communism.models import Theme, Javascript, StyleSheet, Realm, NamedBox

register = Library()

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
            except (KeyError, AttributeError, ValueError) as e:
                # swallows errors and returns empty context
                return {}

        else:

            try:
                theme = Theme.objects.get_by_natural_key(keyname)
            except Theme.DoesNotExist:
                # invalid theme argument, empty context
                return {}

        scripts = Javascript.base_active.for_theme(theme)

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
            except (KeyError, AttributeError, ValueError) as e:
                # swallows errors and returns empty context
                return {}

        else:

            try:
                theme = Theme.objects.get_by_natural_key(keyname)
            except Theme.DoesNotExist:
                # invalid theme argument, empty context
                return {}

        styles = StyleSheet.base_active.for_theme(theme)

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

        cms_page = {'theme': Theme.objects.none()}

        try:
            theme = Theme.objects.get_by_natural_key(keyname)
        except Theme.DoesNotExist:
            # invalid theme argument, empty context
            pass
        else:
            cms_page['theme'] = theme

        context['cms_page'] = cms_page

        return u''



register.tag(ThemePage)
register.tag(ThemeScripts)
register.tag(ThemeStyles)