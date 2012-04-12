from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from libscampi.core.fields import UserModelChoiceField
from .models import ArticleTranslation, Story, Publish

class ArticleTranslationForm(forms.ModelForm):
    headline = forms.CharField(label = _('Headline'), widget = forms.TextInput(attrs={'size': 100}))
    sub_headline = forms.CharField(label = _('Tagline'), widget = forms.TextInput(attrs={'size': 100}))
    synopsis = forms.CharField(
        widget = forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        help_text = _("Article Synopsis, markup(down) allowed: see <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown Syntax</a> for help")
    )
    body = forms.CharField(
        widget = forms.Textarea(attrs={'cols': 80, 'rows': 30}),
    help_text = _("Article body, markup(down) allowed: see <a href='http://daringfireball.net/projects/markdown/syntax'>Markdown Syntax</a> for help")
    )
    
    class Meta:
        model = ArticleTranslation
        fields = ('language', 'headline', 'sub_headline', 'synopsis', 'body')
        

class StoryForm(forms.ModelForm):
    author = UserModelChoiceField(User.objects.all().order_by('first_name', 'last_name', 'username'))
    
    class Meta:
        model = Story
        
class PublishForm(forms.ModelForm):
    approved_by = UserModelChoiceField(User.objects.all().order_by('first_name', 'last_name', 'username'))
    
    class Meta:
        model = Publish 