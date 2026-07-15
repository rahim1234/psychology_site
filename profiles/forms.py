from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        label='نام کامل',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کامل خود را وارد کنید'})
    )
    age = forms.IntegerField(
        label='سن',
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'سن خود را وارد کنید', 'min': 1, 'max': 120,
        })
    )
    gender = forms.ChoiceField(
        label='جنسیت',
        choices=Profile.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    problem_description = forms.CharField(
        label='توضیح مشکل',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'مشکل خود را توضیح دهید (اختیاری)'})
    )

    class Meta:
        model = Profile
        fields = ['full_name', 'age', 'gender', 'problem_description']
