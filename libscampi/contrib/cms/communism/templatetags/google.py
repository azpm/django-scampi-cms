from django import template
from django.utils.encoding import force_text
from classytags.core import Tag, Options
from classytags.arguments import Argument

register = template.Library()


class Urchin(Tag):
    name = "urchin"

    options = Options(
        Argument('google_id', required=True, resolve=True)
    )

    def render_tag(self, context, **kwargs):
        google_id = kwargs.get('google_id')
        string = """
        <script type="text/javascript">
            var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
            document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
        </script>
        """
        string2 = """
            <script type="text/javascript">
                var pageTracker = _gat._getTracker("%s");
                pageTracker._initData();
                pageTracker._trackPageview();
            </script>""" % (google_id,)
        return force_text(string + string2)


register.tag(Urchin)
