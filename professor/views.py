from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from questionnaire.models import course, submissionTrack, examAttempt, techingAssistant, paper, research
from django.contrib import messages
from professor.filter import UserFilter
from django.contrib.auth.decorators import login_required
from professor.forms import feedbackform
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage
from registration.tokens import account_activation_token
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from registration.models import studentName
from django.http import HttpResponseRedirect


# Create your views here.

@login_required
def professorHome(request):
    if request.method == 'POST':
        if 'clear' in request.POST:
            return redirect('professor:professorHome')
        if 'export' in request.POST:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        sessionFullName = request.session['fullNameSession']
        blankspace = ""
        details = submissionTrack.objects.all()
        filter = UserFilter(request.GET, queryset=details)
        user_dict = {'details': details, 'filter': filter, 'sessionFullName': sessionFullName, 'blankspace': blankspace}
        return render(request, 'registration/homeProfessor.html', context=user_dict)


@login_required
def filterName(request, item_id):
    if request.method == 'POST':
        if 'clear' in request.POST:
            return redirect('professor:professorHome')

        if 'export' in request.POST:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        print(item_id)
        details = submissionTrack.objects.filter(username_id=item_id)
        print(details)
        fullname = ''

        for detail in details:
            fullname = detail.fullname
            break
        sessionFullName = request.session['fullNameSession']
        blankspace = ""
        filter = UserFilter(request.GET, queryset=details)
        user_dict = {'details': details, 'filter': filter, 'fullname': fullname, 'sessionFullName': sessionFullName,
                     'blankspace': blankspace}
        return render(request, 'registration/homeProfessor.html', context=user_dict)


@login_required
def submissionView(request, item_id):
    if request.method == 'POST':
        if 'save' in request.POST:
            feedback = ''
            feedback_form = feedbackform(data=request.POST)

            if feedback_form.is_valid():
                feedback = feedback_form.cleaned_data['Feedback']

            var = request.session['varSession']
            submissionTrack.objects.filter(id=var).update(Feedback=feedback)
            submissionTrack.objects.filter(id=var).update(status="Review In Progress")
            messages.warning(request,
                             "Feedback successfully saved")
            return redirect('professor:professorHome')

        if 'submit' in request.POST:
            feedback = ''
            feedback_form = feedbackform(data=request.POST)
            var = request.session['varSession']
            track = submissionTrack.objects.get(id=var)
            submissionTrack.objects.filter(id=var).update(status="Review Submitted")
            user = User.objects.get(username=track.username)
            emailID = user.username
            questionnaireFor = track.questionnaire_for

            if feedback_form.is_valid():
                feedback = feedback_form.cleaned_data['Feedback']

            submissionTrack.objects.filter(id=var).update(Feedback=feedback)

            current_site = get_current_site(request)
#             mail_subject = 'Feedback for your questionnaire' + " " + str(questionnaireFor)
            mail_subject = 'Thanks For Helping Us To Test Our Site, Testing Feedback Functionality'
            message = render_to_string('professor/feedback_email.html', {
                'feedback': feedback,
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = emailID
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.warning(request,
                             "Feedback successfully emailed")
            return redirect('professor:professorHome')

        elif 'back' in request.POST:
            return redirect('professor:professorHome')

        else:
            HttpResponse("Something is wrong on our side. Inform administrator, Then we will resolve it")

    else:
        # print(item_id)
        # sid = submissionTrack.objects.get(status="Submitted For Review").id
        # print("sid --> " + str(sid))
        questionnaire_id = submissionTrack.objects.get(id=item_id).questionnaire_for_id
        questionnaireStatus = submissionTrack.objects.get(id=item_id).status
        questionnaire_submit_username = submissionTrack.objects.get(id=item_id).username

        var = item_id
        request.session['varSession'] = var
        print(questionnaireStatus)
        context = {}
        if (questionnaireStatus == "Submitted For Review") or (questionnaireStatus == "Review In Progress") or (
                questionnaireStatus == "Review Submitted"):
            userTableID = User.objects.get(username=questionnaire_submit_username).id
            course_dict = course.objects.filter(username_id=userTableID,
                                                questionnaire_for_id=questionnaire_id).order_by(
                '-Subject_Year', 'Subject_Term', 'Grade', 'Subject_Name')
            examAttempt_dict = examAttempt.objects.filter(username_id=userTableID,
                                                          questionnaire_for_id=questionnaire_id).order_by(
                'Exam_Name', 'Attempt_Number')
            techingAssistant_dict = techingAssistant.objects.filter(username_id=userTableID,
                                                                    questionnaire_for_id=questionnaire_id).order_by(
                '-Subject_Year', 'Subject_Term', 'Subject_Name')
            paper_dict = paper.objects.filter(Author_id=studentName.objects.get(username_id=userTableID).id,
                                              questionnaire_for_id=questionnaire_id).order_by(
                '-Status_of_Paper', 'Title')
            research_dict = research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)

            fullname = submissionTrack.objects.get(id=item_id).fullname
            instance = submissionTrack.objects.get(id=item_id)
            feedback = submissionTrack.objects.get(id=item_id).Feedback
            feedback_form = feedbackform(instance=instance)
            blankspace = ""

            context = {'fullname': fullname, 'course_dict': course_dict, 'examAttempt_dict': examAttempt_dict,
                       'techingAssistant_dict': techingAssistant_dict, 'questionnaireStatus': questionnaireStatus,
                       'paper_dict': paper_dict, 'research_dict': research_dict, 'feedback_form': feedback_form,
                       'blankspace': blankspace, 'feedback': feedback, }

        else:
            HttpResponse("Something is wrong on our side. Inform administrator, Then we will resolve it")

        return render(request, 'professor/submission.html', context)

############################################CSV filter student list #############################
# def search_query(request):
#     user_list = submissionTrack.objects.all()
#     user_filter = UserFilter(request.GET, queryset=user_list)
#     return user_filter
#
#
# def return_result(request):
#     print("export2")
#     data = search_query(request)
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="students_record.csv"'
#     writer = csv.writer(response, delimiter=',')
#     writer.writerow(
#         ['fullname', 'current_GPA', 'Current_Program_Year','Email', 'questionnaire_for', 'Current_Academic_Advisor',
#          'Current_Research_Advisor', 'status'])
#     for obj in data.qs:
#         writer.writerow([obj.fullname, obj.current_GPA, obj.Current_Program_Year, obj.Email, obj.questionnaire_for,
#                          obj.Current_Academic_Advisor, obj.Current_Research_Advisor, obj.status])
#
#     return response


############################################CSV filter student list#############################


###################profile of student###################

# @login_required
# def profile(request, item_id):
#     if request.method == 'POST':
#         # back = "back"
#         if 'feedback' in request.POST:
#             print("feedback")
#             feedback = ''
#             feedback_form = feedbackform(data=request.POST)
#             if feedback_form.is_valid():
#                 var = request.session['varSession']
#                 earlier_feedback = submissionTrack.objects.filter(id=var)
#                 earlierfeedback = ""
#                 for feedbacks in earlier_feedback:
#                     earlierfeedback = feedbacks.Feedback
#                 # print("valid")
#                 feedback = feedback_form.cleaned_data['Feedback']
#                 feedback = str(earlierfeedback) + " \n" + "--------------------------" + "\n" + "-" + feedback
#             var = request.session['varSession']
#             submissionTrack.objects.filter(id=var).update(Feedback=feedback)
#             sessionFullName = request.session['fullNameSession']
#             # sessionUserName = request.session['userNameSession']
#             # print("student --> " + sessionFullName)
#             # sessionid = request.session['idSession']
#             blankspace = ""
#             details = submissionTrack.objects.all()
#             filter = UserFilter(request.GET, queryset=details)
#             user_dict = {'details': details, 'filter': filter, 'sessionFullName': sessionFullName,
#                          'blankspace': blankspace}
#             return render(request, 'registration/homeProfessor.html', context=user_dict)
#
#         elif 'back' in request.POST:
#             sessionFullName = request.session['fullNameSession']
#             blankspace = ""
#             details = submissionTrack.objects.all()
#             filter = UserFilter(request.GET, queryset=details)
#             user_dict = {'details': details, 'filter': filter, 'sessionFullName': sessionFullName,
#                          'blankspace': blankspace}
#             return render(request, 'registration/homeProfessor.html', context=user_dict)
#
#         elif 'export' in request.POST:
#             print("export1")
#             print("back")
#             sessionFullName = request.session['fullNameSession']
#             # sessionUserName = request.session['userNameSession']
#             # print("student --> " + sessionFullName)
#             # sessionid = request.session['idSession']
#             blankspace = ""
#             details = submissionTrack.objects.all()
#             filter = UserFilter(request.GET, queryset=details)
#             user_dict = {'details': details, 'filter': filter, 'sessionFullName': sessionFullName,
#                          'blankspace': blankspace}
#             return render(request, 'registration/homeProfessor.html', context=user_dict)
#
#         else:
#             var = ""
#             submission_list = submissionTrack.objects.all()
#             for submission in submission_list:
#                 var = submission.id
#                 var = str(var)
#                 if var in request.POST:
#                     break
#
#             print(var)
#             request.session['varSession'] = var
#             # questionnaire_id = request.session["questionnaireForIdSession"]
#             # questionnaireValue = submissionTrack.objects.get(id=var)
#             # print("row --> ")
#             # print(questionnaireValue)
#
#             questionnaire_id = submissionTrack.objects.get(id=var).questionnaire_for_id
#             questionnaireStatus = submissionTrack.objects.get(id=var).status
#             questionnaire_submit_username = submissionTrack.objects.get(id=var).username
#             # questionnaire_submit_fullname = request.session['fullNameSession']
#             print((questionnaireStatus))
#             context = {}
#             if questionnaireStatus == "Submitted":
#                 userTableID = User.objects.get(username=questionnaire_submit_username).id
#                 course_dict = course.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
#                 examAttempt_dict = examAttempt.objects.filter(username_id=userTableID,
#                                                               questionnaire_for_id=questionnaire_id)
#                 techingAssistant_dict = techingAssistant.objects.filter(username_id=userTableID,
#                                                                         questionnaire_for_id=questionnaire_id)
#                 paper_dict = paper.objects.filter(Author_id=userTableID, questionnaire_for_id=questionnaire_id)
#                 research_dict = research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
#
#                 print(course_dict)
#                 print(examAttempt_dict)
#                 print(techingAssistant_dict)
#                 print(paper_dict)
#                 print(research_dict)
#                 obj = User.objects.get(id=userTableID)
#                 firstname = obj.first_name
#                 print(firstname)
#                 lastname = obj.last_name
#                 fullname = firstname + " " + lastname
#                 print(fullname)
#                 feedback_form = feedbackform()
#                 blankspace = ""
#                 context = {'fullname': fullname, 'course_dict': course_dict, 'examAttempt_dict': examAttempt_dict,
#                            'techingAssistant_dict': techingAssistant_dict,
#                            'paper_dict': paper_dict, 'research_dict': research_dict, 'feedback_form': feedback_form,
#                            'blankspace': blankspace}
#             return render(request, 'professor/submission.html', context)
#
#
#     else:
#         submissionTrack_obj = \
#             submissionTrack.objects.filter(username_id=item_id, status="Submitted").order_by("-status")[0]
#         print(submissionTrack_obj)
#         submissionList = submissionTrack.objects.filter(status="Submitted", username_id=item_id)
#
#         context = {
#             "submissionTrack_obj": submissionTrack_obj, 'submissionList': submissionList
#         }
#         return render(request, 'professor/studentProfile.html', context)

# obj = User.objects.get(id=item_id)
# # questionnaire = query.questionnaire_for
# coursesTaken_obj = course.objects.filter(username_id=item_id)
# examAttempts_obj = examAttempt.objects.filter(username_id=item_id)
# techingAssistant_obj = techingAssistant.objects.filter(username_id=item_id)
# paper_obj = paper.objects.filter(Author_id=item_id)
# research_obj = research.objects.filter(username_id=item_id)
# submissionTrack_obj = submissionTrack.objects.filter(username_id=item_id)
# details = submissionTrack.objects.filter(username_id=item_id)
#
# print(coursesTaken_obj)
#
# submissionList = submissionTrack.objects.filter(username_id=item_id)
# final_list = chain(obj, coursesTaken_obj, examAttempts_obj, techingAssistant_obj, paper_obj, research_obj,
#                    submissionTrack_obj, details, submissionList)
# print("final list")
# print(final_list)
#
# # print(obj.name)
# # template = loader.get_template("fac_app/Button.html")
# # print (item_id)
#
# context = {
#     "item": obj, "coursesTaken_obj": coursesTaken_obj, "examAttempts_obj": examAttempts_obj,
#     "techingAssistant_obj": techingAssistant_obj,
#     "paper_obj": paper_obj, "research_obj": research_obj, "submissionTrack_obj": submissionTrack_obj
# }
#
# return render(request, 'professor/profile.html', context)
###################profile of student###################


# def index(request):
#
#     userTableID = User.objects.get(username='arai2@albany.edu').id
#     TermID = term.objects.get(semester='Fall',year='2018').id
#     # print(TermID)
#     # print(userTableID)
#     research_object = research.objects.filter(username_id=userTableID, term_id=TermID)
#     taken_courses = coursesTaken.objects.filter(username_id=userTableID,term_id=TermID)
#     exam_qualify = examAttempts.objects.filter(username_id=userTableID,term_id=TermID)
#     assistant  = techingAssistant.objects.filter(username_id=userTableID,term_id=TermID)
#     research_paper = paper.objects.filter(Author_id=userTableID,term_id=TermID)
#
#     track = research.objects.select_related('username').all()
#
#     print(track)
#
#     # print(research_paper)
#     # print(research_object)
#     # print(taken_courses)
#     # print(exam_qualify)
#     # print(assistant)
#     # print(research_paper)
#
#     user_details=[]
#     track = submissionTrack.objects.filter(saveSubmit__startswith="SUBMIT")
#
#     user_details= User.objects.get(username='arai2@albany.edu')
#
#     # for track2 in track:
#     #    user_details.append[coursesTaken.objects.filter(username=track2.username)]
#     #     print (track2.username)
#
#
#     user_dict = {'details':user_details,'research_obj_view':research_object,'taken_courses_view':taken_courses,'exam_qualify_view':exam_qualify,
#     'assistant_view':assistant,'research_paper_view':research_paper}
#     return render(request,'professor/users.html',context=user_dict)
#
# # def index(request):
# #
# #     user_details=[]
# #     track = submissionTrack.objects.filter(saveSubmit__startswith="SUBMIT")
# #     for track2 in track:
# #         user_details.append[coursesTaken.objects.filter(username=track2.username)]
# #         print (track2.username)
# #
# #     print(user_details)
# #     user_dict = {'details':user_details}
# #     return render(request,'professor/users.html',context=user_dict)
#      # for track3 in track:
#      #     print (track3.first_name)
#      # user_details = User.objects.select_related(username=track.username)
#
#
#     # print(track)
#     #
#     # for track2 in track:
#     #     user_details = User.objects.get(username=track2.username)
#     #     print (track2.username)
#
#
#
#
#     # user_details = User.objects.filter(track.username)
#     # for track2 in track:
#     #     user_details = User.objects.filter(username=track2.username)
#     #     print (track2.username)
#
#
#     # for track3 in user_details:
#     #     print(user_details.first_name)
#         # for m1 in student_details:
#         #     print(student_details.first_name)
#     # for track2 in track:
#     #     print (user_details.first_name)
#     # user_list = advisor.objects.all()
#     # list1 = User.objects.all()
#     # 'users': user_list,'list': list1,
#
#
#
# def users(request):
#     user_list = User.objects.all()
#     user_dict = {'users': user_list}
#     return render(request,'fac_app/users.html',context=user_dict)
#
# def search2(request):
#     if request.method=='POST':
#         srch=request.POST['srh']
#
#         if srch:
#             match = User.objects.filter(Q(name__icontains=srch)| Q(gpa__icontains=srch)| Q(papers_published__icontains=srch)| Q(email__icontains=srch)
#                     | Q(year__icontains=srch)| Q(advisor__icontains=srch)                )
#
#             if match:
#                 return render(request,'fac_app/search.html',{'sr':match})
#             else:
#                 messages.error(request,'no results found')
#         else:
#                 return HttpResponseRedirect('/search')
#     return render(request,'fac_app/search.html')
#
# def search(request):
#     print("in search")
#     user_list = User.objects.all()
#     user_list2 = research.objects.all()
#     user_filter = UserFilter(request.GET, queryset=user_list)
#     return render(request, 'fac_app/user_list.html', {'filter': user_filter})
#
# def button(request):
#     return render(request, 'fac_app/Button.html')
#
#
# def submission(request):
#     user_list = Question.objects.all()
#     context = {
#
#     }
#     user_dict = {'users': user_list}
#     return render(request,'fac_app/submission.html',context=user_dict)
#
# @login_required
# def contact_download(request):
#     items = User.objects.all()
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="contact.csv"'
#     writer = csv.writer(response,delimiter=',')
#     writer.writerow(['name','gpa','papers_published','email','year','advisor','academic_year'])
#
#     for obj in items:
#         writer.writerow([obj.name, obj.gpa, obj.papers_published, obj.email, obj.year, obj.advisor, obj.academic_year])
#
#     return response
# #
#
# def model_info(request,item_id):
#     obj = User.objects.get(id=item_id)
#     coursesTaken_obj = course.objects.filter(username_id=item_id)
#     examAttempts_obj = examAttempt.objects.filter(username_id=item_id)
#     techingAssistant_obj = techingAssistant.objects.filter(username_id=item_id)
#     paper_obj = paper.objects.filter(Author_id=item_id)
#     research_obj = research.objects.filter(username_id=item_id)
#     submissionTrack_obj = submissionTrack.objects.filter(username_id=item_id)
#     details = submissionTrack.objects.filter(username_id=item_id)
#     submissionList = submissionTrack.objects.filter(username_id=item_id)
#
#     final_list  = chain(obj, coursesTaken_obj,examAttempts_obj,techingAssistant_obj,paper_obj,research_obj,submissionTrack_obj,details,submissionList)
#
#     print(final_list)
#     # print(obj.name)
#     # template = loader.get_template("fac_app/Button.html")
#     # print (item_id)
#
#     return final_list
#
# def export_csv(request,item_id):
#     data = search_query(request,item_id)
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="students_record.csv"'
#     writer = csv.writer(response,delimiter=',')
#     writer.writerow(['first_name','last_name','current_GPA','SUNY_ID','Email','questionnaire_for','Current_Academic_Advisor','Current_Research_Advisor','status'])
#     for obj in data.qs:
#          writer.writerow([obj.first_name, obj.last_name, obj.current_GPA,obj.SUNY_ID, obj.Email,obj.questionnaire_for, obj.Current_Academic_Advisor,obj.Current_Research_Advisor,obj.status])
#
#     return response
#


# @login_required
# def item(request, item_id):
#     print("item id")
#     questionnaireFor = submissionTrack.objects.filter(id=item_id).values('questionnaire_for_id')
#     userName = submissionTrack.objects.filter(id=item_id).values('username_id')
#     print(userName)
#
#     # userTableID = User.objects.get(username=questionnaire_submit_username).id
#     obj = User.objects.get(id=item_id)
#     firstname = obj.first_name
#     print(firstname)
#     lastname = obj.last_name
#     fullname = firstname + " " + lastname
#
#     course_dict = course.objects.filter(username_id=userName, questionnaire_for_id=questionnaireFor)
#     examAttempt_dict = examAttempt.objects.filter(username_id=userName, questionnaire_for_id=questionnaireFor)
#     techingAssistant_dict = techingAssistant.objects.filter(username_id=userName, questionnaire_for_id=questionnaireFor)
#     paper_dict = paper.objects.filter(Author_id=userName, questionnaire_for_id=questionnaireFor)
#     research_dict = research.objects.filter(username_id=userName, questionnaire_for_id=questionnaireFor)
#     # submissionTrack_obj = submissionTrack.objects.filter(username_id=item_id)
#
#     context = {
#         "item": obj, 'course_dict': course_dict, 'examAttempt_dict': examAttempt_dict,
#         'techingAssistant_dict': techingAssistant_dict,
#         'paper_dict': paper_dict, 'research_dict': research_dict, 'fullname': fullname}
#
#     return render(request, 'professor/submission.html', context)
#     # return HttpResponse(template.render(context,request))
#
#     # item = User.objects.get(item_id)
