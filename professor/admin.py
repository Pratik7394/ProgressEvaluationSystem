from django.contrib import admin
from questionnaire.models import course, questionnaire, submissionTrack, qualifyingExam, techingAssistant, paper, \
    research, examAttempt  # thesis, advisor,
# from django import forms
from registration.models import userInfo, studentProfile
from django.contrib.auth.models import User
from datetime import datetime


class questionnaireAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        questionnaire_for = form.cleaned_data['questionnaire_for']
        # print(questionnaire_for)
        previous_term = form.cleaned_data['previous_term']
        # print(previous_term)
        status = form.cleaned_data['status']
        # print(status)
        start_date = form.cleaned_data['start_date']
        # print(start_date)
        end_date = form.cleaned_data['end_date']
        # print(end_date)

        questionnaire_dict = []
        user_dict = []
        questionnaireid = None
        # obj = questionnaire.objects.get(questionnaire_for=questionnaire_for).exists()

        try:
            questionnaire.objects.get(questionnaire_for=questionnaire_for)
            questionnaire.objects.filter(questionnaire_for=questionnaire_for).update(
                questionnaire_for=questionnaire_for, previous_term=previous_term, status=status, start_date=start_date,
                end_date=end_date)
        except questionnaire.DoesNotExist:
            questionnaire.objects.create(questionnaire_for=questionnaire_for, previous_term=previous_term,
                                         status=status,
                                         start_date=start_date, end_date=end_date)

        user_dict = userInfo.objects.filter(studentOrProfessor="student").values('user_id')
        questionnaire_dict = questionnaire.objects.filter(questionnaire_for=questionnaire_for).values('id')

        if status == "Active":
            print("we are in")
            for questionnaire_dict in questionnaire_dict:
                questionnaireid = questionnaire_dict.get('id')

            for user in user_dict:
                userid = user.get('user_id')
                username = User.objects.get(id=userid)
                program_joining_date = studentProfile.objects.get(email=username).program_joining_date
                print(program_joining_date)
                year = 0
                if program_joining_date is not None:
                    now = datetime.now()
                    now = now.date()
                    print(now)
                    diff = now - program_joining_date
                    diff = diff.days
                    print(diff)
                    days = 365
                    if diff < days:
                        year = 1
                    elif diff >= days or diff < (days * 2):
                        year = 2
                    elif diff >= (days * 2) or diff < (days * 3):
                        year = 3
                    elif diff >= (days * 3) or diff < (days * 4):
                        year = 4
                    elif diff >= (days * 4) or diff < (days * 5):
                        year = 5
                    elif diff >= (days * 5) or diff < (days * 6):
                        year = 6
                    elif diff >= (days * 6) or diff < (days * 7):
                        year = 7
                    else:
                        year = 8
                    print(year)
                print(username)
                query = User.objects.filter(id=userid).values('first_name', 'last_name')
                for query in query:
                    firstname = query.get('first_name')
                    lastname = query.get('last_name')
                    fullname = str(firstname + " " + lastname)
                    print(firstname)
                    print(lastname)
                    questionnaire_for = questionnaire.objects.get(id=questionnaireid)
                    submissionTrack.objects.create(username=username, questionnaire_for=questionnaire_for,
                                                   status="Not Started", fullname=fullname, Current_Program_Year=year, Email=username)

# def createquery(questionary_for):


# Register your models here.
# admin.site.register(year)
# admin.site.register(advisor)
admin.site.register(course)
admin.site.register(submissionTrack)
# admin.site.register(semester)
admin.site.register(questionnaire, questionnaireAdmin)
admin.site.register(research)
admin.site.register(qualifyingExam)
admin.site.register(examAttempt)
admin.site.register(techingAssistant)
admin.site.register(paper)
# admin.site.register(thesis)

admin.site.site_header = "PhD Evaluation Administrator"
admin.site.site_title = 'PhD Evaluation'
