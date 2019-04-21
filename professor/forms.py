from django import forms
from questionnaire.models import submissionTrack


class feedbackform(forms.ModelForm):
    # Feedback = forms.Textarea(attrs={'rows':8 'cols'=125})

    class Meta:
        model = submissionTrack
        fields = ('Feedback',)
        widgets = {
            'Feedback': forms.Textarea(attrs={'cols': 170, 'rows': 8}),
        }
