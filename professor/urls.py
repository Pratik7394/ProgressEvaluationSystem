from django.conf.urls import url
from professor import views
from django.urls import path

app_name='professor'

urlpatterns = [
    path('professorHome/',views.professorHome,name='professorHome'),
    # path(r'^info/',views.index,name='index'),
    # path(r'^users/',views.users,name='users'),
    # path(r'^search2/',views.search2,name='search2'),
    # # url(r'^search/$', views.search, name='search'),
    # url(r'^details/(?P<item_id>[0-9]+)',views.item,name='item'),
    url(r'^profile/(?P<item_id>[0-9]+)',views.profile,name='profile'),
    url(r'^submission/(?P<item_id>[0-9]+)', views.submissionView, name= 'submissionView'),
    # url(r'^exportcsv/(?P<item_id>[0-9]+)',views.export_csv,name='export_csv'),
    # path(r'^submission/$',views.submission,name='submission'),
    # path(r'^download-csv/',views.contact_download,name='contact_download'),
    path('return_result/',views.return_result,name='return_result'),

]
