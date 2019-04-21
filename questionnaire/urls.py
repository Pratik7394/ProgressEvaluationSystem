from django.urls import path
from questionnaire import views

from questionnaire.views import (
    PaperListView,
    PaperDetailView,
    PaperCreateView,
    PaperUpdateView,
    PaperDeleteView,
    CourseListView,
    CourseDetailView,
    CourseCreateView,
    CourseUpdateView,
    CourseDeleteView
)
app_name = 'questionnaire'
urlpatterns = [
    path('student/', views.studentHome, name='studentHome'),
    path('submissions/', views.viewSubmissions, name='viewSubmissions'),
    path('step1/', views.saveCourses, name='form-courses'),
    path('step2/', views.saveQExams, name='form-qexams'),
    path('step3/', views.saveTA, name='form-ta'),
    path('step4/', views.saveResearch, name='form-research'),
    path('step5/', views.savePapers, name='form-papers'),
    path('paper/', PaperListView.as_view(), name='paper-all'),
    path('paper/<int:pk>/', PaperDetailView.as_view(), name='paper-detail'),
    path('paper/new/', PaperCreateView.as_view(), name='paper-create'),
    path('paper/<int:pk>/update/', PaperUpdateView.as_view(), name='paper-update'),
    path('paper/<int:pk>/delete/', PaperDeleteView.as_view(), name='paper-delete'),
    path('course/all/', CourseListView.as_view(), name='course-all'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('course/new/', CourseCreateView.as_view(), name='course-create'),
    path('course/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('course/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
    # path('submissions/(?P<item_id>[0-9]+)', views.viewSubmissions, name='submissions'),
]
