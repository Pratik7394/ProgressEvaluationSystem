from django.urls import path
from django.conf.urls import url
from questionnaire import views

app_name = 'questionnaire'

urlpatterns = [
    # path('submissions/(?P<item_id>[0-9]+)', views.viewSubmissions, name='submissions'),
    path('submissions/', views.viewSubmissions, name='viewSubmissions'),
    path('student/', views.studentHome, name='studentHome'),
    path('step1/', views.handleResearch, name='form-research'),
    path('step2/', views.handleQExams, name='form-qexams'),
    path('step3/', views.handleTA, name='form-ta'),
    path('step4/', views.handleCourses, name='form-courses'),
    path('step5/', views.handlePapers, name='form-papers'),
    path('step6/', views.handleReview, name='review'),
]
