from django.urls import path
from django.conf.urls import url
from registration import views
from django.views.generic import TemplateView

app_name = 'registration'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.userLogin, name='userLogin'),
    path('logout/', views.userLogout, name='userLogout'),
    path('editProfileStudent/', views.editProfileStudent, name='editProfileStudent'),
    path('editProfileProfessor/', views.editProfileProfessor, name='editProfileProfessor'),
    # path('login/home', TemplateView.as_view(template_name="registration/homeStudent.html"), name='homeStudent'),
    path('home/', views.navigate, name='navigate'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]

