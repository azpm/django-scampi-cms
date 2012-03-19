from django import forms
from django.contrib.auth.models import User
from libscampi.core.fields import UserModelChoiceField, UserModelMultipleChoiceField
from libscampi.contrib.multilingual.models import Language
from .models import ArticleTranslation, Story, Publish

class ArticleTranslationForm(forms.ModelForm):
    headline = forms.CharField(widget = forms.TextInput(attrs={'size': 80}))
    sub_headline = forms.CharField(widget = forms.TextInput(attrs={'size': 80}))
    body = forms.CharField(widget = forms.Textarea(attrs={'cols': 120, 'rows': 30}))
    language = forms.ModelChoiceField(queryset=Language.objects.all(), initial = Language.objects.get(code = "en"))
    
    class Meta:
        model = ArticleTranslation
        fields = ('language', 'headline', 'sub_headline', 'body')
        

class StoryForm(forms.ModelForm):
    author = UserModelChoiceField(User.objects.all().order_by('first_name', 'last_name', 'username'))
    
    class Meta:
        model = Story
        
class PublishForm(forms.ModelForm):
    approved_by = UserModelChoiceField(User.objects.all().order_by('first_name', 'last_name', 'username'))
    
    class Meta:
        model = Publish 