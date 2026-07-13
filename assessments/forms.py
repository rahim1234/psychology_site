from django import forms


class PHQ9TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .scoring import PHQ9_QUESTIONS, PHQ9_ANSWERS
        for i, question in enumerate(PHQ9_QUESTIONS, 1):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=question,
                choices=PHQ9_ANSWERS,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
            )


class GAD7TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .scoring import GAD7_QUESTIONS, GAD7_ANSWERS
        for i, question in enumerate(GAD7_QUESTIONS, 1):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=question,
                choices=GAD7_ANSWERS,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
            )
