from django.contrib import admin
from registration.models import professorWhiteList, userInfo, announcement, studentProfile, professorName, studentName#, studentWhiteList,
# from django.contrib.admin import AdminSite
# from django.utils.translation import ugettext_lazy


# Register your models here.
admin.site.register(userInfo)
admin.site.register(studentProfile)
admin.site.register(professorWhiteList)
admin.site.register(announcement)
admin.site.register(professorName)
admin.site.register(studentName)
# admin.site.registration(studentWhiteList)

admin.site.site_header = "PhD Evaluation Administrator"
admin.site.site_title = 'PhD Evaluation'
