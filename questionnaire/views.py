from registration.forms import userInfoForm, userInfoForm2  # loginForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from registration.models import professorWhiteList, userInfo, announcement  # , studentWhiteList,
from registration.models import studentProfile
from django.contrib import messages
import socket

socket.getaddrinfo('127.0.0.1', 8080)


# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import (
    submissionTrack as Submission,
    course as Course,
    paper as Paper,
    techingAssistant as TA,
    research as Research,
    examAttempt as QExam,
    questionnaire as Questionnaire,
    qualifyingExam as Exams
)
from .forms import (
    CourseForm,
    QExamForm,
    TeachingForm,
    ResearchForm,
    PaperForm
)

@login_required()
def studentHome(request):
    if request.method == 'POST':
        sessionid = request.session['idSession']
        submissionList = Submission.objects.filter(username_id=sessionid)
        var = None
        for submission in submissionList:
            # print(submission.questionnaire_for_id)
            var = submission.id
            var = str(var)
            if var in request.POST:
                break

        request.session["questionnaireForIdSession"] = var
        return redirect('questionnaire:viewSubmissions')

    # if 'editProfile' in request.POST:
    #     return redirect('registration:editProfileStudent')

    else:
        sessionFullName = request.session['fullNameSession']
        sessionUserName = request.session['userNameSession']
        sessionid = request.session['idSession']
        submissionList = Submission.objects.filter(username_id=sessionid).order_by("-questionnaire_for")
        print(submissionList)
        blankspace = ""
        profile = studentProfile.objects.get(email=sessionUserName)
        try:
            Submission.objects.get(status='Submitted For Review')
            profile2 = \
            Submission.objects.filter(status="Submitted For Review", username_id=sessionid).order_by("-status")[0]
            print("profile2")
            print(profile2)
        except Submission.DoesNotExist:
            profile2 = []

    return render(request, 'registration/homeStudent.html',
                  {'profile2': profile2, 'sessionFullName': sessionFullName, 'submissionList': submissionList,
                   'profile': profile, 'blankspace': blankspace})


@login_required()
def viewSubmissions(request):
    if request.method == 'POST':
        # sessionFullName = request.session['fullNameSession']
        # sessionUserName = request.session['userNameSession']
        # sessionid = request.session['idSession']
        # submissionList = submissionTrack.objects.filter(username_id=sessionid).order_by("-questionnaire_for")
        # blankspace = ""
        # profile = studentProfile.objects.get(email=sessionUserName)
        # return render(request, 'registration/homeStudent.html',
        #               {'sessionFullName': sessionFullName, 'submissionList': submissionList,
        #                'profile': profile, 'blankspace': blankspace})
        return redirect('questionnaire:studentHome')

    else:
        submissionTrack_id = request.session["questionnaireForIdSession"]
        questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
        questionnaire_id = Submission.objects.get(id=submissionTrack_id).questionnaire_for_id
        questionnaire_submit_username = request.session['userNameSession']
        questionnaire_submit_fullname = request.session['fullNameSession']
        # print((questionnaireStatus))

        if questionnaireStatus == "Submitted For Review":

            userTableID = User.objects.get(username=questionnaire_submit_username).id
            course_dict = Course.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
            examAttempt_dict = QExam.objects.filter(username_id=userTableID,
                                                          questionnaire_for_id=questionnaire_id)
            techingAssistant_dict = TA.objects.filter(username_id=userTableID,
                                                                    questionnaire_for_id=questionnaire_id)
            paper_dict = Paper.objects.filter(Author_id=userTableID, questionnaire_for_id=questionnaire_id)
            research_dict = Research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
            # feedback_dict = submissionTrack.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)

            # print(feedback)
            print(course_dict)
            print(examAttempt_dict)
            print(techingAssistant_dict)
            print(paper_dict)
            print(research_dict)

            return render(request, 'questionnaire/submissionView.html',
                          {'questionnaire_submit_fullname': questionnaire_submit_fullname,
                           'course_dict': course_dict, 'examAttempt_dict': examAttempt_dict,
                           'techingAssistant_dict': techingAssistant_dict, 'paper_dict': paper_dict,
                           'research_dict': research_dict})
            # 'feedback_dict': feedback_dict})

        ##################saved
        elif questionnaireStatus == "Saved":
            return HttpResponse("work in in progress")


        ##################not started
        else:
            return redirect(reverse('questionnaire:form-courses'))

@login_required()
def saveCourses(request):
    CourseFormSet = formset_factory(CourseForm,can_order=True, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    courses = Course.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).order_by('-Subject_Term_and_Year', 'Grade', 'Subject_Name')
    course_data=[{}]
    if courses.exists():
        course_data = [{
            'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
            'Subject_Name': c.Subject_Name, 'Subject_Code': c.Subject_Code,
            'Subject_Term_and_Year': c.Subject_Term_and_Year, 'Grade': c.Grade
        } for c in courses]
    if request.method == 'POST':
        print('Course POST')
        course_formset = CourseFormSet(request.POST,initial=course_data)
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-qexams'))
        if 'save' in request.POST:
            if course_formset.is_valid():
                print('Course valid')
                new_courses = []
                for course_form in course_formset:
                    Subject_Name = course_form.cleaned_data.get('Subject_Name')
                    Subject_Code = course_form.cleaned_data.get('Subject_Code')
                    Subject_Term_and_Year = course_form.cleaned_data.get('Subject_Term_and_Year')
                    Grade = course_form.cleaned_data.get('Grade')

                    new_courses.append(Course(
                        username_id=userTableID, questionnaire_for_id=questionnaire_id, Subject_Name=Subject_Name,
                        Subject_Code=Subject_Code, Subject_Term_and_Year=Subject_Term_and_Year, Grade=Grade
                    ))
                try:
                    with transaction.atomic():
                        # Replace the old with the new
                        Course.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).delete()
                        Course.objects.bulk_create(new_courses)

                        # notify our users that Courses are saved
                        messages.success(request, 'Your courses are saved.')
                        return redirect(reverse('questionnaire:form-courses'))

                except IntegrityError:  # If the transaction failed
                    print('Course failed')
                    messages.error(request, 'There was an error saving your courses.')
                    return redirect(reverse('questionnaire:form-courses'),{'course_formset': course_formset})
            else:
                print('Course invalid')
                print(course_formset.errors())
                messages.error(request, 'There seems to be something wrong with your courses. Please make sure every entry below is valid.')
                return redirect(reverse('questionnaire:form-courses'),{'course_formset': course_formset})

    elif courses.exists():
        print('Course existing')
        course_formset = CourseFormSet(initial=course_data)
    else:
        print('Course GET')
        course_formset = CourseFormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': ''
        })
    context = {
        'course_formset': course_formset
    }
    return render(request, 'questionnaire/step1.html', context)

@login_required()
def saveQExams(request):
    QExamFormSet = formset_factory(QExamForm,can_order=True, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    qexams = QExam.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).order_by('Exam_Name','Attempt_Number')
    qexam_data = [{}]
    if qexams.exists():
        qexam_data = [{
            'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
            'Exam_Name': c.Exam_Name_id, 'Attempt_Number': c.Attempt_Number, 'Grade': c.Grade
        } for c in qexams]
    if request.method == 'POST':
        print('QExam POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-ta'))
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-courses'))
        qexam_formset = QExamFormSet(request.POST, initial=qexam_data)
        if qexam_formset.is_valid():
            print('QExam valid')
            new_qexams = []
            for qexam_form in qexam_formset:
                Exam_Name_id = Exams.objects.get(exam_Name=qexam_form.cleaned_data.get('Exam_Name')).id
                Attempt_Number = qexam_form.cleaned_data.get('Attempt_Number')
                Grade = qexam_form.cleaned_data.get('Grade')
                new_qexams.append(QExam(
                    username_id=userTableID, questionnaire_for_id=questionnaire_id, Exam_Name_id=Exam_Name_id,
                    Attempt_Number=Attempt_Number, Grade=Grade
                ))
            try:
                with transaction.atomic():
                    # Replace the old with the new
                    QExam.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).delete()
                    QExam.objects.bulk_create(new_qexams)

                    # notify our users that Qualifying Exam Attempts are saved
                    messages.success(request, 'Your qualification exam attempts are saved.')
                    return redirect(reverse('questionnaire:form-qexams'))

            except IntegrityError:  # If the transaction failed
                print('QExam failed')
                messages.error(request, 'There was an error saving your qualification exams.')
                return redirect(reverse('questionnaire:form-qexams'))
        else:
            print('QExam invalid')
            messages.error(request, 'There seems to be something wrong with your qualification exams data. Please make sure all entries below are valid.')
            return redirect(reverse('questionnaire:form-qexams'))
    elif qexams.exists():
        print('QExam existing')
        qexam_formset = QExamFormSet(initial=qexam_data)
    else:
        print('QExam GET')
        qexam_formset = QExamFormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': ''
        })

    context = {
        'qexam_formset': qexam_formset
    }
    return render(request, 'questionnaire/step2.html', context)

@login_required()
def saveTA(request):
    TAFormSet = formset_factory(TeachingForm,can_order=True, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    teaching_assists = TA.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
    ta_data=[{}]
    if teaching_assists.exists():
        ta_data = [{
            'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
            'Subject_Name': c.Subject_Name, 'Subject_Code': c.Subject_Code, 'Responsibilities': c.Responsibilities,
            'In_Which_Semester': c.In_Which_Semester, 'Instructor_Name': c.Instructor_Name,
            'Lecture_or_Presentation_Given': c.Lecture_or_Presentation_Given,
            'Area_of_Improvement': c.Area_of_Improvement
        } for c in teaching_assists]
    if request.method == 'POST':
        print('TA POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-research'))
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-qexams'))
        ta_formset = TAFormSet(request.POST, initial=ta_data)
        if ta_formset.is_valid():
            print('TA valid')
            new_teaching_assists = []
            for ta_form in ta_formset:
                Subject_Name = ta_form.cleaned_data.get('Subject_Name')
                Subject_Code = ta_form.cleaned_data.get('Subject_Code')
                In_Which_Semester = ta_form.cleaned_data.get('In_Which_Semester')
                Instructor_Name = ta_form.cleaned_data.get('Instructor_Name')
                Responsibilities = ta_form.cleaned_data.get('Responsibilities')
                Lecture_or_Presentation_Given = ta_form.cleaned_data.get('Lecture_or_Presentation_Given')
                Area_of_Improvement = ta_form.cleaned_data.get('Area_of_Improvement')

                new_teaching_assists.append(TA(
                    username_id=userTableID, questionnaire_for_id=questionnaire_id, Subject_Name=Subject_Name,
                    Subject_Code=Subject_Code, Responsibilities=Responsibilities,
                    In_Which_Semester=In_Which_Semester, Instructor_Name=Instructor_Name,
                    Lecture_or_Presentation_Given=Lecture_or_Presentation_Given,
                    Area_of_Improvement=Area_of_Improvement
                ))
            try:
                with transaction.atomic():
                    # Replace the old with the new
                    TA.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).delete()
                    TA.objects.bulk_create(new_teaching_assists)

                    # notify our users that TAs are saved
                    messages.success(request, 'Your teaching assist experiences are saved.')
                    return redirect('questionnaire:form-ta')

            except IntegrityError:  # If the transaction failed
                print('TA failed')
                messages.error(request, 'There was an error saving your teaching assist experiences .')
                return redirect(reverse('questionnaire:form-teaching'))
        else:
            print('TA invalid')
            messages.error(request, 'There is something in your teaching assist experiences. Please make sure all entries below are valid. ')
            return redirect('questionnaire:form-ta')
    elif teaching_assists.exists():
        print('TA existing data')
        ta_formset = TAFormSet(initial=ta_data)
    else:
        print('TA GET')
        ta_formset = TAFormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': ''
        })

    context = {
        'ta_formset': ta_formset
    }
    return render(request, 'questionnaire/step3.html', context)

@login_required()
def saveResearch(request):
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    research = Research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
    research_data = [{}]
    if research.exists():
        research_data = [{
            'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id, 'Topic': c.Topic,
            'Proposal': c.Proposal, 'Defense': c.Defense, 'Current_Program_Year':c.Current_Program_Year,
            'Current_Academic_Advisor': c.Current_Academic_Advisor, 'Current_GPA':c.Current_GPA,
            'Current_Research_Advisor': c.Current_Research_Advisor
        }for c in research]
    if request.method == 'POST':
        print('Research POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-papers'))
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-ta'))
        research_form = ResearchForm(request.POST)
        if research_form.is_valid():
            print('Research data is valid')
            Topic = research_form.cleaned_data.get('Topic')
            Proposal = research_form.cleaned_data.get('Proposal')
            Defense = research_form.cleaned_data.get('Defense')
            Current_GPA = research_form.cleaned_data.get('Current_GPA')
            Current_Academic_Advisor_id = research_form.cleaned_data.get('Current_Academic_Advisor_id')
            Current_Research_Advisor_id = research_form.cleaned_data.get('Current_Research_Advisor_id ')
            Current_Program_Year = research_form.cleaned_data.get('Current_Program_Year')
            print(str(Current_GPA) + ' ' + Current_Program_Year)
            newresearch = [Research(
                username_id=userTableID, questionnaire_for_id=questionnaire_id, Topic=Topic, Proposal=Proposal,
                Defense=Defense, Current_Research_Advisor_id=Current_Research_Advisor_id, Current_GPA=Current_GPA,
                Current_Academic_Advisor_id=Current_Academic_Advisor_id, Current_Program_Year=Current_Program_Year
            )]
            try:
                with transaction.atomic():
                    # Replace the old with the new
                    Research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).delete()
                    Research.objects.bulk_create(newresearch)

                    # notify our users that research details are saved
                    messages.success(request, 'Your research details are saved.')
                    return redirect('questionnaire:form-research')

            except IntegrityError:  # If the transaction failed
                print('Research data failed to save')
                messages.error(request, 'There was an error saving your research details.')
                return redirect(reverse('questionnaire:form-research'))
        else:
            print('Research data is invalid')
            messages.error(request,
                           'There seems to be something wrong with your research details. Please make sure every entry below is valid.')
            return redirect('questionnaire:form-research')
    elif research.exists():
        print('Research Get with existing data')
        c = research[0]
        research_data = {
            'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id, 'Topic': c.Topic,
            'Proposal': c.Proposal, 'Defense': c.Defense,
            'Current_Academic_Advisor': c.Current_Academic_Advisor,
            'Current_Research_Advisor': c.Current_Research_Advisor
        }
        research_form = ResearchForm(initial=research_data)
    else:
        print('Research GET')
        research_form = ResearchForm()
    context = {
        'research_form': research_form
    }
    return render(request, 'questionnaire/step4.html', context)

@login_required()
def savePapers(request):
    PaperFormSet = formset_factory(PaperForm,can_order=True, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    papers = Paper.objects.filter(Author_id=userTableID, questionnaire_for_id=questionnaire_id).order_by('Status_of_Paper', 'Title')
    paper_data = [{}]
    if(papers.exists()):
        print('Papers present and noted')
        paper_data = [{
            'Author': c.Author_id, 'questionnaire_for_id': c.questionnaire_for_id, 'Title': c.Title,
            'Venue': c.Venue, 'Coauthor': c.Coauthor, 'Status_of_Paper': c.Status_of_Paper
        } for c in papers]
    else:
        print('Papers absent for ' + str(userTableID) + request.session['userNameSession'] + ' and QID:' + str(questionnaire_id))
    if request.method == 'POST':
        print('Paper POST')
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-research'))
        paper_formset = PaperFormSet(request.POST, initial=paper_data)
        if paper_formset.is_valid():
            print('Paper valid')
            new_papers = []
            for paper_form in paper_formset:
                Title = paper_form.cleaned_data.get('Title')
                Venue = paper_form.cleaned_data.get('Venue')
                Coauthor = paper_form.cleaned_data.get('Coauthor')
                Status_of_Paper = paper_form.cleaned_data.get('Status_of_Paper')

                new_papers.append(Paper(
                    Author_id=userTableID, questionnaire_for_id=questionnaire_id, Title=Title,
                    Venue=Venue, Coauthor=Coauthor, Status_of_Paper=Status_of_Paper
                ))
            try:
                with transaction.atomic():
                    # Replace the old with the new
                    Paper.objects.filter(Author_id=userTableID, questionnaire_for_id=questionnaire_id).delete()
                    Paper.objects.bulk_create(new_papers)

                    # notify our users that papers are saved
                    messages.success(request, 'Your papers are saved.')
                    return redirect(reverse('questionnaire:form-papers'), {'paper_formset': paper_formset})

            except IntegrityError:  # If the transaction failed
                print('Paper failed')
                messages.error(request, 'There was an error saving your papers.')
                return redirect(reverse('questionnaire:form-papers'),{'paper_formset': paper_formset})
        else:
            print('Paper invalid')
            messages.error(request,
                           'There seems to be something wrong with your research paper details. Please make sure every entry below is valid.')
            return redirect(reverse('questionnaire:form-papers'), {'paper_formset': paper_formset})
    elif papers.exists():
        print('Paper with existing data')
        paper_formset = PaperFormSet(initial=paper_data)
    else:
        print('Paper GET')
        paper_formset = PaperFormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': ''
        })
    context = {
        'paper_formset': paper_formset
    }
    return render(request, 'questionnaire/step5.html', context)


class PaperListView(LoginRequiredMixin, ListView):
    model = Paper
    # <app>/<model>_<viewtype>.html
    context_object_name = 'papers'
    ordering = ['title']


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    # <app>/<model>_<viewtype>.html
    context_object_name = 'courses'
    ordering = ['username', 'questionnaire_for', 'Subject_Code']


class PaperDetailView(LoginRequiredMixin, DetailView):
    model = Paper


class PaperCreateView(LoginRequiredMixin, CreateView):
    model = Paper
    fields = ['title', 'venue', 'status', 'author', 'coauthors']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PaperUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Paper
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        paper = self.get_object()
        if self.request.user == paper.author:
            return True
        return False


class PaperDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Paper
    success_url = '/'

    def test_func(self):
        paper = self.get_object()
        if self.request.user == paper.author:
            return True
        return False


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    fields = ['Subject_Name', 'Subject_Code', 'Subject_Term_and_Year', 'Grade']

    def form_valid(self, form):
        form.instance.username = self.request.user
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    success_url = '/'
    fields = ['Subject_Name', 'Subject_Code', 'Subject_Term_and_Year', 'Grade']

    def form_valid(self, form):
        form.instance.username = self.request.user
        return super().form_valid(form)

    def test_func(self):
        course = self.get_object()
        if self.request.user == course.username:
            return True
        return False


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    success_url = '/'

    def test_func(self):
        course = self.get_object()
        if self.request.user == course.username:
            return True
        return False

