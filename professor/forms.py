from django import forms
from questionnaire.models import submissionTrack


class feedbackform(forms.ModelForm):

    class Meta:
        model = submissionTrack
        fields = ('Feedback',)
        widgets = {
            'Feedback': forms.Textarea(attrs={'cols': 165, 'rows': 8}),
        }
