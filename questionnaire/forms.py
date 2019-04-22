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
            'Responsibilities': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'Lecture_or_Presentation_Given': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'Area_of_Improvement': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }
        # fields = ['Subject_Name', 'Subject_Code', 'In_Which_Semester', 'Instructor_Name',
        #  'Responsibilities', 'Lecture_or_Presentation_Given', 'Area_of_Improvement']

class ResearchForm(ModelForm):
    class Meta:
        model = Research
        exclude = ['username', 'questionnaire_for']
        # fields = ['Topic', 'Proposal', 'Defense', 'Current_Academic_Advisor', 'Current_Research_Advisor']

class PaperForm(ModelForm):
    class Meta:
        model = Paper
        exclude = ['username', 'questionnaire_for']
        # fields = ['Title', 'Venue', 'Status_of_Paper', 'Coauthor']