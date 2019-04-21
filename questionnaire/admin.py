from django.contrib import admin
from questionnaire.models import course, questionnaire, submissionTrack, qualifyingExam, techingAssistant, paper, \
    research, examAttempt  # thesis, advisor,
# from django import forms
from registration.models import userInfo
from django.contrib.auth.models import User


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
                print(username)
                query = User.objects.filter(id=userid).values('first_name', 'last_name')
                for query in query:
                    firstname = query.get('first_name')
                    lastname = query.get('last_name')
                    fullname = str(firstname + " " + lastname)
                    print(firstname)
                    print(lastname)
                    questionnaire_for = questionnaire.objects.get(id=questionnaireid)
                    submissionTrack.objects.create(username=username, questionnaire_for=questionnaire_for, status="Not Started",fullname=fullname)
            # print ("looping again")
            # user_list.append(username)
            # print(user_list)
            # A = "Hello \n \n" + "Hi"
            # print(A)

        # for user in user_list:
        #     user_name = user.username
        #     # username = str(username)

        # return super(questionnaireAdmin, self)
        # .save_model(request, obj, form, change)

# def createquery(questionary_for):


# Register your models here.

admin.site.register(course)
admin.site.register(submissionTrack)
admin.site.register(questionnaire, questionnaireAdmin)
admin.site.register(research)
admin.site.register(qualifyingExam)
admin.site.register(examAttempt)
admin.site.register(techingAssistant)
admin.site.register(paper)


admin.site.site_header = "PhD Evaluation Administrator"
admin.site.site_title = 'PhD Evaluation'
