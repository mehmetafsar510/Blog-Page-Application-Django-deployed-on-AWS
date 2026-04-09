from django import forms
from django.db.models import fields
from .models import Post, Comment, Tag, NewsletterSubscriber


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
    status = forms.ChoiceField(
        choices=Post.OPTIONS,
        initial='p',  # Default to Published
        widget=forms.RadioSelect
    )
    category = forms.ChoiceField(choices=Post.CATEGORY_OPT)
    published_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text='Optional publish date for scheduling'
    )
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
            'published_date',
            'tags',
            'meta_title',
            'meta_description',
            'keywords',
        )
        widgets = {
            'meta_description': forms.Textarea(attrs={'rows': 3, 'maxlength': 160}),
            'keywords': forms.TextInput(attrs={'placeholder': 'keyword1, keyword2, keyword3'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)


class NewsletterSubscriptionForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'autocomplete': 'email',
            'type': 'email'
        })
    )
    
    class Meta:
        model = NewsletterSubscriber
        fields = ('email',)
        labels = {
            'email': ''
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
        return email
