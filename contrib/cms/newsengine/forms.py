from django import forms
from django.contrib.auth.models import User
from libscampi.core.fields import UserModelChoiceField, UserModelMultipleChoiceField
from libscampi.contrib.multilingual.models import Language
from .models import ArticleTranslation, Story, Publish

class ArticleTranslationForm(forms.ModelForm):
    #body = forms.CharField(widget = forms.Textarea(attrs={'cols': 120, 'rows': 30}))
    
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