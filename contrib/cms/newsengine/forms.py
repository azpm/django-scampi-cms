from django import forms
from .models import Article

class ArticleTranslationForm(forms.ModelForm):
    headline = forms.CharField(widget = forms.TextInput(attrs={'size': 80}))
    sub_headline = forms.CharField(widget = forms.TextInput(attrs={'size': 80}))
    body = forms.CharField(widget = forms.Textarea(attrs={'cols': 120, 'rows': 30}))
    
    class Meta:
        model = Article
        fields = ('language', 'headline', 'sub_headline', 'body')