from django.urls import path
from django.conf.urls import url
from registration import views
# from django.urls import include
# from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

app_name = 'registration'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.userLogin, name='userLogin'),
    path('home/', views.homepageStudent, name='homePageStudent'),
    ########################use this for professor homepage
    # path('Home/', views.homepageProfessor, name='homePageProfessor'),

    # path('login/', views.userLoginCheck, name='userLoginCheck'),
    path('logout/', views.userLogout, name='userLogout'),
    path('editProfileStudent/', views.editProfileStudent, name='editProfileStudent'),
    path('login/home', TemplateView.as_view(template_name="registration/homeStudent.html"), name='homeStudent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]

