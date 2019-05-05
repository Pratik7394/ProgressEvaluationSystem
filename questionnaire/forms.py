from django.forms import ModelForm
from django import forms
from .models import (
    course as Course,
    examAttempt as QExam,
    techingAssistant as TA,
    research as Research,
    paper as Paper
)
from questionnaire.models import questionnaire, submissionTrack


class CourseForm(ModelForm):
    class Meta:
        model = Course
        exclude = ['username', 'questionnaire_for']
        # fields = ['Subject_Name', 'Subject_Code', 'Subject_Term_and_Year', 'Grade']


class QExamForm(ModelForm):
    class Meta:
        model = QExam
        exclude = ['username', 'questionnaire_for']
        # fields = ['Exam_Name', 'Attempt_Number', 'Grade']


class TeachingForm(ModelForm):
    class Meta:
        model = TA
        exclude = ['username', 'questionnaire_for']
        widgets = {
            'Responsibilities': forms.Textarea(attrs={'rows': 5, 'cols': 13}),
            'Lecture_or_Presentation_Given': forms.Textarea(attrs={'rows': 5, 'cols': 13}),
            'Area_of_Improvement': forms.Textarea(attrs={'rows': 5, 'cols': 13}),
            'Subject_Name': forms.TextInput(attrs={'size': 15}),
            'Subject_Code': forms.TextInput(attrs={'size': 10}),
            'Instructor_Name': forms.TextInput(attrs={'size': 15}),
        }

        # fields = ['Subject_Name', 'Subject_Code', 'Instructor_Name',
        #  'Responsibilities', 'Lecture_or_Presentation_Given', 'Area_of_Improvement']


class DateInput(forms.DateInput):
    input_type = 'date'


class ResearchForm(ModelForm):
    class Meta:
        model = Research
        exclude = ['username', 'questionnaire_for']
        # fields = ['Topic', 'Proposal', 'Defense', 'Current_Academic_Advisor', 'Current_Research_Advisor']

        widgets = {
            'Proposal': DateInput(),
            'Defense': DateInput(),
            'Thesis_Committee': forms.Textarea(attrs={'rows': 7, 'cols': 40}),
            'Topic': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }


class PaperForm(ModelForm):
    class Meta:
        model = Paper
        exclude = ['username', 'questionnaire_for']
        # fields = ['Title', 'Venue', 'Status_of_Paper', 'Coauthor']
        widgets = {
            'Title': forms.Textarea(attrs={'rows': 3, 'cols': 16}),
            'Venue': forms.Textarea(attrs={'rows': 3, 'cols': 16}),
            'List_of_Authors': forms.Textarea(attrs={'rows': 3, 'cols': 16}),
        }


class questionnaireAdminForm(forms.ModelForm):
    class Meta:
        model = questionnaire
        fields = ('questionnaire_for', 'previous_term', 'status', 'start_date', 'end_date',)

    def clean(self):
        cleaned_data = super(questionnaireAdminForm, self).clean()
        questionnaire_for = cleaned_data.get('questionnaire_for')
        status = cleaned_data.get('status')

        id = None

        try:
            questionnaire.objects.get(questionnaire_for=questionnaire_for)
            id = questionnaire.objects.get(questionnaire_for=questionnaire_for).id
        except questionnaire.DoesNotExist:
            pass

        if submissionTrack.objects.filter(questionnaire_for_id=id).exists():
            if status == 'Active':
                raise forms.ValidationError('Questionnaire already present in submission track....INTEGRITY ERROR')

        if status == 'Active':
            if questionnaire.objects.filter(status='Active').exists():
                raise forms.ValidationError(
                    'A questionnaire already exist with active status, Please Inactive every other questionnaire')

