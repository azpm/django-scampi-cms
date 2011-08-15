from django import template
from django.utils.encoding import force_unicode
register = template.Library()

def urchin(uacct):
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
        </script>""" % (uacct,)
    return force_unicode(string+string2)

register.simple_tag(urchin)