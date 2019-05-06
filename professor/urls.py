from django.conf.urls import url
from professor import views
from django.urls import path

app_name = 'professor'

urlpatterns = [
    path('professorHome/',views.professorHome,name='professorHome'),
    url(r'^submission/(?P<item_id>[0-9]+)', views.submissionView, name= 'submissionView'),
    url(r'^filterName/(?P<item_id>[0-9]+)', views.filterName, name='filterName'),
]
