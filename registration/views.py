from registration.forms import userInfoForm, userInfoForm2, studentProfileForm, professorProfileForm  # loginForm
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
from django.contrib.auth.decorators import login_required
from registration.models import professorWhiteList, userInfo, studentProfile, announcement, studentName
from questionnaire.models import submissionTrack, questionnaire
from django.contrib import messages
import datetime
from datetime import datetime

# import socket
# socket.getaddrinfo('127.0.0.1', 8080)


# Create your views here.

@login_required()
def userLogout(request):
    print("hi2")
    del request.session['fullNameSession']
    del request.session['userNameSession']
    del request.session['idSession']
    del request.session['studentProfessor']
    del request.session['login']
    logout(request)
    announcement_list = announcement.objects.all()
    return render(request, 'registration/index.html',
                  {'announcement_list': announcement_list})

def index(request):
    announcement_list = announcement.objects.all()
    return render(request, 'registration/index.html',
                  {'announcement_list': announcement_list})

def register(request):
    registered = False

    if request.method == "POST":

        userInfo_form = userInfoForm(data=request.POST)
        userInfo_form2 = userInfoForm2(data=request.POST)

        if userInfo_form.is_valid() and userInfo_form2.is_valid():
            email = userInfo_form.cleaned_data['email']
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

            # Email Verification
            current_site = get_current_site(request)
            mail_subject = 'ACTIVATE YOUR PhD EVALUATION ACCOUNT'
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
            messages.info(request,
                             "Please confirm your email address to complete the registration")
            return redirect('registration:userLogin')
        else:
            print(userInfo_form.errors, userInfo_form2.errors)

    else:
        userInfo_form = userInfoForm()
        userInfo_form2 = userInfoForm2()

        if 'login' in request.session:
            del request.session['fullNameSession']
            del request.session['userNameSession']
            del request.session['idSession']
            del request.session['studentProfessor']
            del request.session['login']
            logout(request)
            announcement_list = announcement.objects.all()
            message = messages.warning(request,
                                       "You have been logged out")
            return render(request, 'registration/index.html',
                          {'announcement_list': announcement_list})


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
        emailID = user.email
        # print(emailID)
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
            studentProfile.objects.create(email=emailID, first_name=first_name, last_name=last_name)
            studentName.objects.create(username=user, name=full_name)
            questionnaire_for = None

            try:
                questionnaire_for = questionnaire.objects.get(status='Active').id
            except:
                pass

            if questionnaire_for is not None:
                questionnaireFor = questionnaire.objects.get(id=questionnaire_for)
                submissionTrack.objects.create(username=user, questionnaire_for=questionnaireFor,
                                               status="Not Started", Email=emailID, fullname=full_name)

        # else:
            # user = User.objects.get(id=uid)
            # professorName.objects.create(username=user, name=full_name)

        message = messages.success(request,
                                   "Email verification done. You can login into your account now")
        return redirect("registration:userLogin")
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
                    request.session['login'] = 'login'
                    # id = User.objects.get(username=username).id
                    studentProfessor = userInfo.objects.get(user_id=id).studentOrProfessor
                    request.session['studentProfessor'] = studentProfessor
                    if studentProfessor == "student":
                        return redirect('questionnaire:studentHome')

                    elif studentProfessor == "professor":
                        return redirect('professor:professorHome')

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
            messages.warning(request,
                             "Something is wrong on our side. Inform administrator, Then we will resolve it")
            return redirect('registration:userLogin')
    else:
        if 'login' in request.session:
            del request.session['fullNameSession']
            del request.session['userNameSession']
            del request.session['idSession']
            del request.session['studentProfessor']
            del request.session['login']
            logout(request)
            announcement_list = announcement.objects.all()
            message = messages.warning(request,
                                       "You have been logged out")
            return render(request, 'registration/index.html',
                          {'announcement_list': announcement_list})
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

    sessionUserName = request.session['userNameSession']
    id = request.session['idSession']
    profile = studentProfile.objects.get(email=sessionUserName)
    studentProfessor = userInfo.objects.get(user_id=id).studentOrProfessor
    studentProfile_Form = studentProfileForm(instance=profile)

    if request.method == "POST":

        studentProfile_Form = studentProfileForm(data=request.POST)

        if studentProfile_Form.is_valid():
            sessionUserName = request.session['userNameSession']
            first_name = studentProfile_Form.cleaned_data['first_name']
            last_name = studentProfile_Form.cleaned_data['last_name']
            SUNY_ID = studentProfile_Form.cleaned_data['SUNY_ID']
            native_country = studentProfile_Form.cleaned_data['native_country']
            full_name = first_name + " " + last_name
            program_joining_date = studentProfile_Form.cleaned_data['program_joining_date']
            # print(program_joining_date)
            now = datetime.now()
            now = now.date()
            # print(now)
            diff = now - program_joining_date
            diff = diff.days
            # print(diff)
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

            # print(year)
            studentProfile.objects.filter(email=sessionUserName).update(first_name=first_name, last_name=last_name,
                                                                        SUNY_ID=SUNY_ID,
                                                                        native_country=native_country,
                                                                        program_joining_date=program_joining_date)
            uid = User.objects.get(username=sessionUserName).id
            submissionTrack.objects.filter(status=('Not Started' or 'Saved'), username_id=uid).update(
                Current_Program_Year=year)
            User.objects.filter(username=sessionUserName).update(first_name=first_name, last_name=last_name)

            submissionTrack.objects.filter(username_id=uid).update(fullname=full_name)
            sessionid = request.session['idSession']
            studentName.objects.filter(username_id=sessionid).update(name=full_name)
            sessionUserName = request.session['userNameSession']
            first_name = User.objects.get(username=sessionUserName).first_name
            last_name = User.objects.get(username=sessionUserName).last_name
            full_name = first_name + " " + last_name
            request.session['firstNameSession'] = first_name
            request.session['lastNameSession'] = last_name
            request.session['fullNameSession'] = full_name
            return redirect('questionnaire:studentHome')

        else:
            print(studentProfile_Form.errors)

    return render(request, 'registration/profile_edit.html',
                      {'studentProfile_Form': studentProfile_Form, 'studentProfessor': studentProfessor})


@login_required()
def editProfileProfessor(request):
    if request.method == "POST":
        professorProfile_Form = professorProfileForm(data=request.POST)
        if professorProfile_Form.is_valid():
            sessionUserName = request.session['userNameSession']
            name = request.session['fullNameSession']
            first_name = professorProfile_Form.cleaned_data['first_name']
            last_name = professorProfile_Form.cleaned_data['last_name']
            full_name = first_name + " " + last_name
            uid = User.objects.get(username=sessionUserName).id
            User.objects.filter(username=sessionUserName).update(first_name=first_name, last_name=last_name)
            # professorWhiteList.objects.filter(email=sessionUserName).update(name = full_name)
            # submissionTrack.objects.filter(Current_Research_Advisor=name).update(Current_Research_Advisor=full_name)
            # submissionTrack.objects.filter(Current_Academic_Advisor=name).update(Current_Academic_Advisor=full_name)
            first_name = User.objects.get(username=sessionUserName).first_name
            last_name = User.objects.get(username=sessionUserName).last_name
            request.session['firstNameSession'] = first_name
            request.session['lastNameSession'] = last_name
            request.session['fullNameSession'] = full_name

            return redirect('professor:professorHome')

    else:
        sessionUserName = request.session['userNameSession']
        profile = User.objects.get(username=sessionUserName)
        id = request.session['idSession']
        studentProfessor = userInfo.objects.get(user_id=id).studentOrProfessor
        # print("userinfo --> " + str(studentProfessor))
        professorProfile_Form = professorProfileForm(instance=profile)
        return render(request, 'registration/profile_edit.html',
                      {'professorProfile_Form': professorProfile_Form, 'studentProfessor': studentProfessor})

