from django import forms
from django.db.models import fields
from .models import Post, Comment, Tag


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...'
        })
    )


class PostForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Post.OPTIONS)
    category = forms.ChoiceField(choices=Post.CATEGORY_OPT)
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Post
        fields = (
            'title',
            'content',
            'image',
            'category',
            'status',
            'tags',
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
