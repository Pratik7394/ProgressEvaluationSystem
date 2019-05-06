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
from registration.models import studentName, userInfo
from django.http import HttpResponseRedirect
from registration.decorators import user_type_professor


# Create your views here.

@login_required
@user_type_professor
def professorHome(request):
    if request.method == 'POST':
        if 'clear' in request.POST:
            return redirect('professor:professorHome')
        if 'export' in request.POST:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        sessionid = request.session['idSession']
        sessionFullName = request.session['fullNameSession']
        blankspace = ""
        details = submissionTrack.objects.all()
        filter = UserFilter(request.GET, queryset=details)
        user_dict = {'details': details, 'filter': filter, 'sessionFullName': sessionFullName, 'blankspace': blankspace}
        return render(request, 'registration/homeProfessor.html', context=user_dict)


@login_required
@user_type_professor
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
@user_type_professor
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
            messages.warning(request, "Feedback successfully emailed")
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
