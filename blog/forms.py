from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    title = forms.CharField(
        label='عنوان',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان مقاله'})
    )
    content = forms.CharField(
        label='محتوا',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10})
    )
    image = forms.ImageField(
        label='تصویر',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    published = forms.BooleanField(
        label='منتشر شده',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'published']
