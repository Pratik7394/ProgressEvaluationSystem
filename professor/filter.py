from questionnaire.models import questionnaire, qualifyingExam, course, submissionTrack, examAttempt, techingAssistant, \
    paper, research
from django.contrib.auth.models import User
import django_filters
from django import forms


class UserFilter(django_filters.FilterSet):
    print("in filter")
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    current_GPA = django_filters.CharFilter(lookup_expr='icontains')
    SUNY_ID = django_filters.CharFilter(lookup_expr='icontains')
    Email = django_filters.CharFilter(lookup_expr='icontains')
    questionnaire_for = django_filters.CharFilter(lookup_expr='icontains')
    Current_Academic_Advisor = django_filters.CharFilter(lookup_expr='icontains')
    Current_Research_Advisor = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='icontains')

    # status2 = django_filters.ModelMultipleChoiceFilter(queryset=submissionTrack.objects.all(),widget=forms.CheckboxSelectMultiple)

    # year__gt = django_filters.NumberFilter(name='year', lookup_expr='year__gt')
    # year__lt = django_filters.NumberFilter(name='year', lookup_expr='year__lt')
    # advisor = django_filters.CharFilter(lookup_expr='icontains')
    # academic_year = django_filters.CharFilter(lookup_expr='icontains')
    # year_joined_gt = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    # year_joined_lt = django_filters.NumberFilter(field_name='year', lookup_expr='lte')

    class Meta:
        model = submissionTrack
        fields = ['first_name', 'last_name', 'current_GPA', 'SUNY_ID', 'Email', 'questionnaire_for',
                  'Current_Academic_Advisor', 'Current_Research_Advisor', 'status']
        # ,'status2']
