from django import forms
from django.forms import ModelForm, HiddenInput

from network.models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['user', 'content']
        widgets = {
            'user': HiddenInput(),
            'content': forms.Textarea(
                attrs={'rows': 1, 'cols': 30})
        }
