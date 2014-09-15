import akismet
import unicodedata
import urllib2
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.comments.moderation import CommentModerator


class StoryModerator(CommentModerator):
    auto_close_field = 'start'
    close_after = 30

    def allow(self, comment, content_object, request):
        check = content_object.publish_set.filter(published=True).latest('start')
        # the check is the latest published version of the story
        if check:
            return check.comments_enabled and check.published
        else:
            return False

    def moderate(self, comment, content_object, request):
        if request.user.is_authenticated() and request.user.is_staff:
            return False
        api = akismet.Akismet(
            key=settings.AKISMET_API_KEY or None,
            blog_url=Site.objects.get_current().realm.get_base_url(),
            agent="Scampi NewsEngine Python/Django"
        )

        for k in comment.userinfo:
            comment.userinfo[k] = unicodedata.normalize('NFKD', comment.userinfo[k]).encode('ascii', 'ignore')

        data = {
            'user_ip': comment.ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'comment_author': comment.userinfo['name'],
            'comment_author_url': comment.userinfo['url']
        }

        try:
            return api.comment_check(unicodedata.normalize('NFKD', comment.comment).encode('ascii', 'ignore'), data)
        except (urllib2.HTTPError, urllib2.URLError):
            return True
