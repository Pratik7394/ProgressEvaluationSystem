from django.urls import path
from questionnaire import views
app_name = 'questionnaire'
urlpatterns = [
    path('student/', views.studentHome, name='studentHome'),
    path('submissions/', views.viewSubmissions, name='viewSubmissions'),
    path('step1/', views.handleCourses, name='form-courses'),
    path('step2/', views.handleQExams, name='form-qexams'),
    path('step3/', views.handleTA, name='form-ta'),
    path('step4/', views.handleResearch, name='form-research'),
    path('step5/', views.handlePapers, name='form-papers'),
    # path('submissions/(?P<item_id>[0-9]+)', views.viewSubmissions, name='submissions'),
]
