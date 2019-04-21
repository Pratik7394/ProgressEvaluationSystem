from registration.forms import userInfoForm, userInfoForm2, studentProfileForm  # loginForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from registration.models import professorWhiteList, userInfo, studentProfile, announcement, studentName, professorName
from questionnaire.models import submissionTrack, questionnaire
# , studentWhiteList,
from django.contrib import messages

import socket

socket.getaddrinfo('127.0.0.1', 8080)


# Create your views here.


@login_required()
def special(request):
    del request.session['your key']
    return HttpResponse("You are loged in, Nice!")


@login_required()
def userLogout(request):
    del request.session['fullNameSession']
    del request.session['userNameSession']
    del request.session['idSession']
    logout(request)
    return HttpResponseRedirect(reverse('registration:index'))


def index(request):
    announcement_list = announcement.objects.all()
    return render(request, 'registration/index.html',
                  {'announcement_list': announcement_list})
    # return render(request, 'registration/index.html', {})


def register(request):
    registered = False
    if request.method == "POST":

        userInfo_form = userInfoForm(data=request.POST)
        userInfo_form2 = userInfoForm2(data=request.POST)

        if userInfo_form.is_valid() and userInfo_form2.is_valid():
            email = userInfo_form.cleaned_data['email']
            # firstName = userInfo_form.cleaned_data['first_name']
            # lastName = userInfo_form.cleaned_data['last_name']
            user = userInfo_form.save()
            user.is_active = False
            user.username = email
            user.set_password(user.password)
            user.save()
            studentprofessor = userInfo_form2.save(commit=False)
            studentprofessor.user = user

            ####white list logic saved for future ####
            # if studentWhiteList.objects.filter(email=email).exists():
            #     StudentOrProfessor = "student"

            if professorWhiteList.objects.filter(email=email).exists():
                StudentOrProfessor = "professor"
            else:
                StudentOrProfessor = "student"

            studentprofessor.studentOrProfessor = StudentOrProfessor  # change field
            studentprofessor.save()
            registered = True

            ####STUDENT PROFILE####
            # userProfile = studentProfile.objects.create(username=email)
            # userProfile.save()

            # Email Verification
            current_site = get_current_site(request)
            mail_subject = 'ACTIVATE YOUR PhD Evaluation ACCOUNT'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = userInfo_form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.warning(request,
                             "Please confirm your email address to complete the registration")
            return redirect('registration:userLogin')
        else:
            print(userInfo_form.errors, userInfo_form2.errors)

    else:
        userInfo_form = userInfoForm()
        userInfo_form2 = userInfoForm2()

    return render(request, 'registration/register.html', {'userInfo_form': userInfo_form,
                                                          'userInfo_form2': userInfo_form2,
                                                          'registered': registered})


#############ACTIVATE EMAIL##############
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        user_name = user.username
        email = user.email
        first_name = user.first_name
        last_name = user.last_name
        first_name = str(first_name)
        last_name = str(last_name)
        full_name = first_name + " " + last_name
        # print("email -- > " + email)
        uid = force_text(urlsafe_base64_decode(uidb64))
        studentProfessor = userInfo.objects.get(user_id=uid).studentOrProfessor
        if studentProfessor == "student":
            user = User.objects.get(id=uid)
            # studentName.user = user
            studentProfile.objects.create(email=email, first_name=first_name, last_name=last_name)
            studentName.objects.create(username=user, name=full_name)
            questionnaire_for = questionnaire.objects.get(status='Active').id

            print("questionnaire_for")
            print(questionnaire_for)

            if questionnaire_for is not None:
                questionnaireFor = questionnaire.objects.get(id=questionnaire_for)
                submissionTrack.objects.create(username=user, questionnaire_for=questionnaireFor,
                                               status="Not Started", fullname=full_name)

        else:
            user = User.objects.get(id=uid)
            professorName.objects.create(username=user, name=full_name)

        message = messages.warning(request,
                                   "Email verification done. You can login into your account now")
        return HttpResponseRedirect('http://127.0.0.1:8000/registration/login/')
        # return render(request, 'registration/login.html', {'message': message})
        # return userLogin
    else:
        return HttpResponse('Activation link is invalid!, Contact Administrator')


def userLogin(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            # print("inlogin")
            username = request.POST.get('username')
            username = username.lower()
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            # full_name = request.user.get_full_name()
            # print("name --> " + first_name)
            # print("username --> " + username)
            # username = request.session['username']

            if user is not None:

                if user.is_active:
                    login(request, user)
                    id = User.objects.get(username=username).id
                    first_name = User.objects.get(username=username).first_name
                    last_name = User.objects.get(username=username).last_name
                    full_name = first_name + " " + last_name
                    request.session['userNameSession'] = username
                    request.session['firstNameSession'] = first_name
                    request.session['lastNameSession'] = last_name
                    request.session['fullNameSession'] = full_name
                    request.session['idSession'] = id
                    # id = User.objects.get(username=username).id
                    studentProfessor = userInfo.objects.get(user_id=id).studentOrProfessor

                    if studentProfessor == "student":
                        return redirect('questionnaire:studentHome')
                        # sessionFullName = request.session['fullNameSession']
                        # sessionUserName = request.session['userNameSession']
                        # # print("student --> " + sessionFullName)
                        # sessionid = request.session['idSession']
                        # submissionList = submissionTrack.objects.filter(username_id=sessionid).order_by("-questionnaire_for")
                        # blankspace = ""
                        # profile = studentProfile.objects.get(email=sessionUserName)
                        # return render(request, 'registration/homeStudent.html',
                        #               {'sessionFullName': sessionFullName, 'submissionList': submissionList,
                        #                'profile': profile, 'blankspace': blankspace})


                    elif studentProfessor == "professor":
                        return redirect('professor:professorHome')
                        ###################need to be implemented
                        # print("professor")
                        # return render(request, 'registration/homeProfessor.html', {})
                    else:
                        messages.warning(request,
                                         "Something is wrong on our side. Inform administrator, Then we will resolve it")
                        return redirect('registration:userLogin')
                else:
                    messages.warning(request, "User not active yet")
                    return redirect('registration:userLogin')

            else:
                messages.warning(request, "Invalid login details!")
                return redirect('registration:userLogin')
        else:
            # sessionid = request.session['idSession']
            # submissionList = submissionTrack.objects.filter(username_id=sessionid)
            # var = None
            # for submission in submissionList:
            #     # print(submission.Questionnaire_For_id)
            #     var = submission.questionnaire_for_id
            #     var = str(var)
            #     if var in request.POST:
            #         break
            # request.session["questionnaireForIdSession"] = var
            # return redirect('questionnaire:submissions')
            messages.warning(request,
                             "Something is wrong on our side. Inform administrator, Then we will resolve it")
            return redirect('registration:userLogin')
    else:
        return render(request, 'registration/login.html', {})


###################Dont remove it#############
# def userLoginCheck(request):
#     if request.session.has_key('username'):
#         username = request.session['username']
#         return render(request, 'registration/homeStudent.html', {"username": username})
#     else:
#         return redirect('registerAndLogin:userLogin')


def forgotPassword(request):
    return render(request, 'registration/password_reset_form.html', {})


@login_required()
def editProfileStudent(request):
    if request.method == "POST":
        print("post")
        studentProfile_Form = studentProfileForm(data=request.POST)
        if studentProfile_Form.is_valid():
            print("valid")
            sessionUserName = request.session['userNameSession']
            first_name = studentProfile_Form.cleaned_data['first_name']
            last_name = studentProfile_Form.cleaned_data['last_name']
            SUNY_ID = studentProfile_Form.cleaned_data['SUNY_ID']
            native_country = studentProfile_Form.cleaned_data['native_country']
            full_name = first_name + " " + last_name
            # current_GPA = studentProfile_Form.cleaned_data['current_GPA']
            # number_of_semester_completed = studentProfile_Form.cleaned_data['number_of_semester_completed']
            # current_research_advisor = studentProfile_Form.cleaned_data['current_research_advisor']
            # current_academic_advisor = studentProfile_Form.cleaned_data['current_academic_advisor']
            # number_of_paper_PUBLISHED = studentProfile_Form.cleaned_data['number_of_paper_PUBLISHED']
            # print("start update")
            studentProfile.objects.filter(email=sessionUserName).update(first_name=first_name, last_name=last_name,
                                                                        SUNY_ID=SUNY_ID,
                                                                        native_country=native_country)

            # current_GPA=current_GPA,
            # number_of_semester_completed=number_of_semester_completed,
            # current_research_advisor=current_research_advisor,
            # current_academic_advisor=current_academic_advisor,
            # number_of_paper_PUBLISHED=number_of_paper_PUBLISHED)
            # print("update 2")
            User.objects.filter(username=sessionUserName).update(first_name=first_name, last_name=last_name)
            # print("update 3")

            # print("update 1")
            # username = str(sessionUserName)
            sessionid = request.session['idSession']

            studentName.objects.filter(username_id=sessionid).update(name=full_name)

            sessionUserName = request.session['userNameSession']
            first_name = User.objects.get(username=sessionUserName).first_name
            last_name = User.objects.get(username=sessionUserName).last_name
            full_name = first_name + " " + last_name
            request.session['fullNameSession'] = full_name
            # sessionFullName = request.session['fullNameSession']
            # sessionUserName = request.session['userNameSession']
            # sessionid = request.session['idSession']
            # submissionList = submissionTrack.objects.filter(username_id=sessionid)
            # profile = studentProfile.objects.get(email=sessionUserName)
            # return render(request, 'registration/homeStudent.html',
            #               {'sessionFullName': sessionFullName, 'submissionList': submissionList,
            #                'profile': profile})
            return redirect('questionnaire:studentHome')


    else:
        sessionUserName = request.session['userNameSession']
        profile = studentProfile.objects.get(email=sessionUserName)
        studentProfile_Form = studentProfileForm(instance=profile)
        # print("hey all")
        return render(request, 'registration/student_profile_edit.html', {'studentProfile_Form': studentProfile_Form, })


@login_required()
def homepageStudent(request):
    sessionFullName = request.session['fullNameSession']
    sessionUserName = request.session['userNameSession']
    sessionid = request.session['idSession']
    submissionList = submissionTrack.objects.filter(username_id=sessionid).order_by("-questionnaire_for")
    blankspace = ""
    profile = studentProfile.objects.get(email=sessionUserName)
    return render(request, 'registration/homeStudent.html',
                  {'sessionFullName': sessionFullName, 'submissionList': submissionList,
                   'profile': profile, 'blankspace': blankspace})
