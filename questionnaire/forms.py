from django.forms import ModelForm
from django import forms
from .models import (
    course as Course,
    examAttempt as QExam,
    techingAssistant as TA,
    research as Research,
    paper as Paper
    )


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
            'Subject_Name': forms.TextInput(attrs={'size':15}),
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
