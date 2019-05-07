from questionnaire.models import submissionTrack
import django_filters


class UserFilter(django_filters.FilterSet):
    choices_select = (
        ('0', 'Saved'),
        ('1', 'Submitted For Review'),
        ('3', 'Review In Progress'),
        ('4', 'Review Submitted'),
        ('5', 'Not_Started'),
    )

    fullname = django_filters.CharFilter(lookup_expr='icontains')
    current_GPA = django_filters.CharFilter(lookup_expr='icontains')
    current_GPA_gt = django_filters.NumberFilter(field_name='current_GPA', lookup_expr='gte')
    current_GPA_lt = django_filters.NumberFilter(field_name='current_GPA', lookup_expr='lte')
    SUNY_ID = django_filters.CharFilter(lookup_expr='icontains')
    Email = django_filters.CharFilter(lookup_expr='icontains')
    Current_Program_Year = django_filters.CharFilter(lookup_expr='icontains')
    Current_Academic_Advisor = django_filters.CharFilter(lookup_expr='icontains')
    Current_Research_Advisor = django_filters.CharFilter(lookup_expr='icontains')
    questionnaire = django_filters.CharFilter(lookup_expr='icontains')
    status_1 = django_filters.ChoiceFilter(choices=choices_select, lookup_expr='icontains')

    class Meta:
        model = submissionTrack
        fields = ['fullname', 'current_GPA', 'SUNY_ID', 'Email', 'Current_Program_Year',
                  'Current_Academic_Advisor', 'Current_Research_Advisor', 'questionnaire_for', 'status']

