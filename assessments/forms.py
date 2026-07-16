from django import forms

from .scoring import GAD7_ANSWERS, GAD7_QUESTIONS, PHQ9_ANSWERS, PHQ9_QUESTIONS


class PHQ9TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        for i, question in enumerate(GAD7_QUESTIONS, 1):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=question,
                choices=GAD7_ANSWERS,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
            )


class BDITestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i, question in enumerate(BDI_QUESTIONS, 1):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=f'{i}. {question["text"]}',
                choices=question['options'],
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
            )


class BAITestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i, question in enumerate(BAI_QUESTIONS, 1):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=f'{i}. {question}',
                choices=BAI_ANSWERS,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
            )


class MCMI4TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i, question in enumerate(MCMI4_QUESTIONS, 1):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=f'{i}. {question}',
                choices=MCMI4_ANSWERS,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
            )

from .scoring import BDI_QUESTIONS, BAI_QUESTIONS, BAI_ANSWERS, MCMI4_QUESTIONS, MCMI4_ANSWERS


class BDITestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i, question in enumerate(BDI_QUESTIONS, 1):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=f'{i}. {question["text"]}',
                choices=question['options'],
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
            )


class BAITestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i, question in enumerate(BAI_QUESTIONS, 1):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=f'{i}. {question}',
                choices=BAI_ANSWERS,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
            )


class MCMI4TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i, question in enumerate(MCMI4_QUESTIONS, 1):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=f'{i}. {question}',
                choices=MCMI4_ANSWERS,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
            )