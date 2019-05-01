from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from registration.models import studentProfile
from registration.models import studentName as Student, professorName as Professor
from django.contrib import messages
from django.db.models import Q
import socket

socket.getaddrinfo('127.0.0.1', 8080)
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from questionnaire.models import (
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


# Create your views here.
@login_required()
def studentHome(request):
    if request.method == 'POST':
        print("view")
        # sessionid = request.session['idSession']
        # submissionList = Submission.objects.filter(username_id=sessionid)
        # print(submissionList)
        var = None
        var = request.POST['var']
        if "review" in var:
            print("mission success")
            print(var)
        request.session["questionnaireForIdSession"] = var
        return redirect('questionnaire:viewSubmissions')

    else:
        sessionFullName = request.session['fullNameSession']
        sessionUserName = request.session['userNameSession']
        sessionid = request.session['idSession']
        submissionList = Submission.objects.filter(username_id=sessionid).order_by("-questionnaire_for")
        submit = "submit"
        print(submissionList)
        blankspace = ""
        profile = studentProfile.objects.get(email=sessionUserName)
        try:
            Submission.objects.filter(
                Q(status='Review Submitted') | Q(status='Submitted For Review') | Q(status='Review In Progress'),
                username_id=sessionid)
            profile2 = \
                Submission.objects.filter(
                    Q(status='Review Submitted') | Q(status='Submitted For Review') | Q(status='Review In Progress'),
                    username_id=sessionid).order_by(
                    "-questionnaire_for_id").first()
            print("profile2")
            print(profile2)
        except Submission.DoesNotExist:
            profile2 = []

        return render(request, 'registration/homeStudent.html',
                      {'profile2': profile2, 'sessionFullName': sessionFullName, 'submissionList': submissionList,
                       'profile': profile, 'blankspace': blankspace, 'submit': submit})

@login_required()
def viewSubmissions(request):
    if request.method == 'POST':
        return redirect('questionnaire:studentHome')

    else:
        submissionTrack_id = request.session["questionnaireForIdSession"]

        if "review" in submissionTrack_id:
            print("yes")
            submissionTrack_id = submissionTrack_id[:-6]
            request.session["questionnaireForIdSession"] = submissionTrack_id
            return redirect('questionnaire:review')

        else:
            submissionTrack_id = request.session["questionnaireForIdSession"]
            questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
            questionnaire_id = Submission.objects.get(id=submissionTrack_id).questionnaire_for_id
            questionnaire_submit_username = request.session['userNameSession']
            questionnaire_submit_fullname = request.session['fullNameSession']
            print((questionnaireStatus))
            userTableID = User.objects.get(username=questionnaire_submit_username).id

            if questionnaireStatus in ["Submitted For Review", "Review In Progress", "Review Submitted"]:
                course_dict = Course.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
                examAttempt_dict = QExam.objects.filter(username_id=userTableID,
                                                        questionnaire_for_id=questionnaire_id)
                techingAssistant_dict = TA.objects.filter(username_id=userTableID,
                                                          questionnaire_for_id=questionnaire_id)
                paper_dict = Paper.objects.filter(Author_id=Student.objects.get(username_id=userTableID).id,
                                                  questionnaire_for_id=questionnaire_id)
                research_dict = Research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)

                return render(request, 'questionnaire/submissionView.html',
                              {'questionnaire_submit_fullname': questionnaire_submit_fullname,
                               'course_dict': course_dict, 'examAttempt_dict': examAttempt_dict,
                               'techingAssistant_dict': techingAssistant_dict, 'paper_dict': paper_dict,
                               'research_dict': research_dict})

            ##################saved
            elif questionnaireStatus == "Saved":
                return redirect(reverse('questionnaire:form-research'))

            ##################not started
            else:
                currentReport = Questionnaire.objects.get(id=questionnaire_id)
                try:
                    previousReport = Questionnaire.objects.get(id=currentReport.previous_term_id)
                except Questionnaire.DoesNotExist:
                    previousReport = None

                if previousReport:
                    print('Previous report exists')
                    print('Current Questionnaire:' + str(currentReport))
                    print('Previous Questionnaire:' + str(previousReport))

                    # Load Research data
                    try:
                        research = Research.objects.get(username_id=userTableID, questionnaire_for_id=previousReport.id)
                    except Research.DoesNotExist:
                        research = None
                    if research:
                        print('Research Data exists and Loaded for this term')
                        data = [Research(
                            username_id=research.username_id, questionnaire_for_id=questionnaire_id,
                            Topic=research.Topic,
                            Proposal=research.Proposal, Defense=research.Defense,
                            Proposal_Status=research.Proposal_Status, Defense_Status=research.Defense_Status,
                            Thesis_Committee=research.Thesis_Committee,
                            Current_GPA=research.Current_GPA,
                            Current_Research_Advisor=research.Current_Research_Advisor,
                            Current_Academic_Advisor=research.Current_Academic_Advisor
                        )]
                        try:
                            with transaction.atomic():
                                Research.objects.bulk_create(data)
                                messages.success(request, 'Your Research details are preloaded.')
                        except IntegrityError:
                            # If the transaction failed
                            messages.error(request, "Your Research details couldn't be preloaded.")


                    # Load Courses
                    courses = Course.objects.filter(username_id=userTableID, questionnaire_for_id=previousReport.id)
                    if courses.exists():
                        print('Course data exists and Loaded for this term')
                        data = [Course(
                            username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                            Subject_Name=c.Subject_Name, Subject_Code=c.Subject_Code,
                            Subject_Year=c.Subject_Year, Subject_Term=c.Subject_Term, Grade=c.Grade
                        ) for c in courses]
                        try:
                            with transaction.atomic():
                                Course.objects.bulk_create(data)
                                messages.success(request, 'Your courses are preloaded.')
                        except IntegrityError:
                            # If the transaction failed
                            messages.error(request, "Your courses couldn't be preloaded.")


                    # Load Qualifying Exam Attempts
                    qexams = QExam.objects.filter(username_id=userTableID, questionnaire_for_id=previousReport.id)
                    if qexams.exists():
                        print('QExam data exists and Loaded for this term')
                        data = [QExam(
                            username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                            Exam_Name_id=c.Exam_Name_id, Attempt_Number=c.Attempt_Number, Grade=c.Grade
                        ) for c in qexams]
                        try:
                            with transaction.atomic():
                                QExam.objects.bulk_create(data)
                                messages.success(request, 'Your Qualifying exam attempts are preloaded.')
                        except IntegrityError:
                            # If the transaction failed
                            messages.error(request, "Your Qualifying exam attempts couldn't be preloaded.")

                    # Load Teaching Assistantships
                    teaching_assists = TA.objects.filter(username_id=userTableID,
                                                         questionnaire_for_id=previousReport.id)
                    if teaching_assists.exists():
                        print('TA Data exists and Loaded for this term')
                        data = [TA(
                            username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                            Subject_Name=c.Subject_Name, Subject_Code=c.Subject_Code,
                            Responsibilities=c.Responsibilities,
                            Subject_Year=c.Subject_Year, Subject_Term=c.Subject_Term, Instructor_Name=c.Instructor_Name,
                            Lecture_or_Presentation_Given=c.Lecture_or_Presentation_Given,
                            Area_of_Improvement=c.Area_of_Improvement
                        ) for c in teaching_assists]
                        try:
                            with transaction.atomic():
                                TA.objects.bulk_create(data)
                                messages.success(request, 'Your TA experiences are preloaded.')
                        except IntegrityError:
                            # If the transaction failed
                            messages.error(request, "Your TA details couldn't be preloaded.")

                    # Load Research Papers
                    studentAuthor_id = Student.objects.get(username_id=userTableID)
                    papers = Paper.objects.filter(Author_id=studentAuthor_id, questionnaire_for_id=previousReport.id)
                    if papers.exists():
                        print('Papers present and noted')
                        data = [Paper(
                            Author_id=c.Author_id, questionnaire_for_id=questionnaire_id, Title=c.Title,
                            Venue=c.Venue, List_of_Authors=c.List_of_Authors, Status_of_Paper=c.Status_of_Paper,
                            Publish_Year=c.Publish_Year, Publish_Term=c.Publish_Term
                        ) for c in papers]
                        try:
                            with transaction.atomic():
                                Paper.objects.bulk_create(data)
                                messages.success(request, 'Your Research papers are preloaded.')
                        except IntegrityError:
                            # If the transaction failed
                            messages.error(request, "Your Research papers couldn't be preloaded.")

                return redirect(reverse('questionnaire:form-research'))


@login_required()
def handleResearch(request):
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    try:
        research = Research.objects.get(username_id=userTableID, questionnaire_for_id=questionnaire_id)
    except Research.DoesNotExist:
        research = None
    data = {}
    if research:
        print('Research Data exists and Noted')
        data = {
            'username_id': research.username_id, 'questionnaire_for_id': research.questionnaire_for_id,
            'Topic': research.Topic, 'Proposal': research.Proposal, 'Defense': research.Defense,
            'Proposal_Status': research.Proposal_Status, 'Defense_Status': research.Defense_Status,
            'Current_Academic_Advisor': research.Current_Academic_Advisor, 'Current_GPA': research.Current_GPA,
            'Current_Research_Advisor': research.Current_Research_Advisor, 'Thesis_Committee': research.Thesis_Committee
        }
    if request.method == 'POST':
        print('Research POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-qexams'))
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:studentHome'))
        sub = Submission.objects.get(id=submissionTrack_id)
        if sub.status == "Not Started":
            Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

        form = ResearchForm(request.POST)
        if form.is_valid():
            print('Research data is valid')
            if form.has_changed():
                Topic = form.cleaned_data.get('Topic')
                Proposal = form.cleaned_data.get('Proposal')
                Defense = form.cleaned_data.get('Defense')
                Thesis_Committee = form.cleaned_data.get('Thesis_Committee')
                Defense_Status = form.cleaned_data.get('Defense_Status')
                Proposal_Status = form.cleaned_data.get('Proposal_Status')

                Current_Academic_Advisor = form.cleaned_data.get('Current_Academic_Advisor')
                try:
                    Current_Academic_Advisor_id = Professor.objects.get(name=Current_Academic_Advisor).id
                except Professor.DoesNotExist:
                    Current_Academic_Advisor_id = None

                Current_Research_Advisor = form.cleaned_data.get('Current_Research_Advisor')
                try:
                    Current_Research_Advisor_id = Professor.objects.get(name=Current_Research_Advisor).id
                except Professor.DoesNotExist:
                    Current_Research_Advisor_id = None
                Current_GPA = form.cleaned_data.get('Current_GPA')
                newresearch = [Research(
                    username_id=userTableID, questionnaire_for_id=questionnaire_id, Topic=Topic, Proposal=Proposal,
                    Defense=Defense, Current_Research_Advisor_id=Current_Research_Advisor_id, Current_GPA=Current_GPA,
                    Current_Academic_Advisor_id=Current_Academic_Advisor_id, Proposal_Status=Proposal_Status,
                    Defense_Status = Defense_Status, Thesis_Committee=Thesis_Committee
                )]
                try:
                    with transaction.atomic():
                        # Replace the old with the new
                        Research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).delete()
                        Research.objects.bulk_create(newresearch)

                        # notify our users that research details are saved
                        messages.success(request, 'Your research details are saved.')
                        return redirect(reverse('questionnaire:form-research'))

                except IntegrityError:  # If the transaction failed
                    print('Research data failed to save')
                    messages.error(request, 'There was an error saving your research details.')
                    # return redirect(reverse('questionnaire:form-research'))
            else:
                messages.error(request, 'Please modify data in order to Save!')
        else:
            print('Research data is invalid')
            messages.error(request,
                           'There seems to be something wrong with your research details. Please make sure every entry below is valid.')
            # return redirect('questionnaire:form-research')
    elif research:
        print('Research Get with existing data')
        form = ResearchForm(initial=data)
    else:
        print('Research GET')
        form = ResearchForm()
    context = {
        'form': form
    }
    return render(request, 'questionnaire/research.html', context)


@login_required()
def handleQExams(request):
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    FormSet = formset_factory(QExamForm, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    qexams = QExam.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).order_by(
        'Exam_Name', 'Attempt_Number')
    data = [{}]
    if qexams.exists():
        print('QExam data exists and noted')
        data = [{
            'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
            'Exam_Name': c.Exam_Name_id, 'Attempt_Number': c.Attempt_Number, 'Grade': c.Grade
        } for c in qexams]
    if request.method == 'POST':
        print('QExam POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-ta'))
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-research'))
        if 'save' in request.POST:
            sub = Submission.objects.get(id=submissionTrack_id)
            if sub.status == "Not Started":
                Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

            formset = FormSet(request.POST, initial=data)
            if formset.is_valid():
                print('QExam valid')
                new_qexams = []
                if formset.has_changed():
                    print('Data modified')
                    for form in formset:
                        if form in formset.deleted_forms:
                            continue
                        Exam_Name_id = ''
                        try:
                            Exam_Name_id = Exams.objects.get(exam_Name=form.cleaned_data.get('Exam_Name')).id
                        except Exams.DoesNotExist:
                            continue
                        if not Exam_Name_id:
                            continue
                        Attempt_Number = form.cleaned_data.get('Attempt_Number')
                        Grade = form.cleaned_data.get('Grade')
                        new_qexams.append(QExam(
                            username_id=userTableID, questionnaire_for_id=questionnaire_id,
                            Exam_Name_id=Exam_Name_id,
                            Attempt_Number=Attempt_Number, Grade=Grade
                        ))
                    try:
                        with transaction.atomic():
                            # Replace the old with the new
                            QExam.objects.filter(username_id=userTableID,
                                                 questionnaire_for_id=questionnaire_id).delete()
                            QExam.objects.bulk_create(new_qexams)

                            # notify our users that Qualifying Exam Attempts are saved
                            messages.success(request, 'Your qualification exam attempts are saved.')
                            return redirect(reverse('questionnaire:form-qexams'))

                    except IntegrityError:  # If the transaction failed
                        print('QExam failed')
                        messages.error(request, 'There was an error saving your qualification exams.')
                else:
                    messages.error(request, 'Please modify data in order to Save!')
            else:
                print('QExam invalid')
                messages.error(request, 'There seems to be something wrong with your qualification exams data. ' +
                               'Please make sure all entries below are valid.')
        else:
            return redirect(reverse('questionnaire:form-qexams'))
    elif qexams.exists():
        print('QExam existing')
        formset = FormSet(initial=data)
    else:
        print('QExam GET')
        formset = FormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': ''
        })

    context = {
        'formset': formset
    }
    return render(request, 'questionnaire/qexams.html', context)


@login_required()
def handleTA(request):
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    FormSet = formset_factory(TeachingForm, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    teaching_assists = TA.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
    data = [{}]
    if teaching_assists.exists():
        print('TA Data exists and Noted')
        data = [{
            'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
            'Subject_Name': c.Subject_Name, 'Subject_Code': c.Subject_Code, 'Responsibilities': c.Responsibilities,
            'Subject_Year': c.Subject_Year,  'Subject_Term': c.Subject_Term,'Instructor_Name': c.Instructor_Name,
            'Lecture_or_Presentation_Given': c.Lecture_or_Presentation_Given,
            'Area_of_Improvement': c.Area_of_Improvement
        } for c in teaching_assists]
    if request.method == 'POST':
        print('TA POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-courses'))
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-qexams'))

        sub = Submission.objects.get(id=submissionTrack_id)
        if sub.status == "Not Started":
            Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

        formset = FormSet(request.POST, initial=data)
        if formset.is_valid():
            print('TA valid')
            new_teaching_assists = []
            if formset.has_changed():
                print('Data modified')
                for form in formset:
                    if form in formset.deleted_forms:
                        continue
                    Subject_Name = form.cleaned_data.get('Subject_Name')
                    if not Subject_Name:
                        continue
                    Subject_Code = form.cleaned_data.get('Subject_Code')
                    Subject_Year = form.cleaned_data.get('Subject_Year')
                    Subject_Term = form.cleaned_data.get('Subject_Term')
                    Instructor_Name = form.cleaned_data.get('Instructor_Name')
                    Responsibilities = form.cleaned_data.get('Responsibilities')
                    Lecture_or_Presentation_Given = form.cleaned_data.get('Lecture_or_Presentation_Given')
                    Area_of_Improvement = form.cleaned_data.get('Area_of_Improvement')

                    new_teaching_assists.append(TA(
                        username_id=userTableID, questionnaire_for_id=questionnaire_id, Subject_Name=Subject_Name,
                        Subject_Code=Subject_Code, Responsibilities=Responsibilities,
                        Subject_Year=Subject_Year, Subject_Term=Subject_Term, Instructor_Name=Instructor_Name,
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
                        return redirect(reverse('questionnaire:form-ta'))
                except IntegrityError:  # If the transaction failed
                    print('TA failed')
                    messages.error(request, 'There was an error saving your teaching assist experiences .')
            else:
                messages.error(request, 'Please modify data in order to Save!')
        else:
            print('TA invalid')
            messages.error(request, 'There seems something wrong with your TA details.' +
                           ' Please make sure all entries below are valid.')
    elif teaching_assists.exists():
        print('TA existing data')
        formset = FormSet(initial=data)
    else:
        print('TA GET')
        formset = FormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': ''
        })

    context = {
        'formset': formset
    }
    return render(request, 'questionnaire/teaching.html', context)


@login_required()
def handleCourses(request):
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    FormSet = formset_factory(CourseForm, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    courses = Course.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).order_by(
        '-Subject_Year','Subject_Term', 'Grade', 'Subject_Name')
    data = [{}]
    if courses.exists():
        print('Course data exists and noted')
        data = [{
            'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
            'Subject_Name': c.Subject_Name, 'Subject_Code': c.Subject_Code,
            'Subject_Year': c.Subject_Year, 'Subject_Term': c.Subject_Term, 'Grade': c.Grade
        } for c in courses]
    if request.method == 'POST':
        print('Course POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-papers'))
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-ta'))
        sub = Submission.objects.get(id=submissionTrack_id)
        if sub.status == "Not Started":
            Submission.objects.filter(id=submissionTrack_id).update(status="Saved")
        formset = FormSet(request.POST, initial=data)
        if formset.is_valid():
            print('Course valid')
            new_courses = []
            if formset.has_changed():
                print('Data modified')
                for form in formset:
                    if form in formset.deleted_forms:
                        continue
                    Subject_Name = form.cleaned_data.get('Subject_Name')
                    if not Subject_Name:
                        continue
                    Subject_Code = form.cleaned_data.get('Subject_Code')
                    Subject_Year = form.cleaned_data.get('Subject_Year')
                    Subject_Term = form.cleaned_data.get('Subject_Term')
                    Grade = form.cleaned_data.get('Grade')

                    new_courses.append(Course(
                        username_id=userTableID, questionnaire_for_id=questionnaire_id,
                        Subject_Name=Subject_Name,
                        Subject_Code=Subject_Code, Subject_Year=Subject_Year, Subject_Term=Subject_Term, Grade=Grade
                    ))
                try:
                    with transaction.atomic():
                        # Replace the old with the new
                        Course.objects.filter(username_id=userTableID,
                                              questionnaire_for_id=questionnaire_id).delete()
                        Course.objects.bulk_create(new_courses)

                        # notify our users that Courses are saved
                        messages.success(request, 'Your courses are saved.')
                        return redirect(reverse('questionnaire:form-courses'))

                except IntegrityError:  # If the transaction failed
                    print('Course failed')
                    messages.error(request, 'There was an error saving your courses.')
            else:
                messages.error(request, 'Please modify data in order to Save!')

        else:
            print('Course invalid')
            messages.error(request,
                           'There seems to be something wrong with your courses. Please make sure every entry below is valid.')

    elif courses.exists():
        print('Course with existing data')
        formset = FormSet(initial=data)
    else:
        print('Course GET')
        formset = FormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': ''
        })
    context = {
        'formset': formset
    }
    return render(request, 'questionnaire/courses.html', context)


@login_required()
def handlePapers(request):
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    FormSet = formset_factory(PaperForm, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = Student.objects.get(username_id=User.objects.get(username=request.session['userNameSession']).id)
    papers = Paper.objects.filter(Author_id=userTableID.id, questionnaire_for_id=questionnaire_id).order_by(
        '-Status_of_Paper', 'Title')
    data = [{}]
    if papers.exists():
        print('Papers present and noted')
        data = [{
            'Author_id': c.Author_id, 'questionnaire_for_id': c.questionnaire_for_id, 'Title': c.Title,
            'Venue': c.Venue, 'List_of_Authors': c.List_of_Authors, 'Status_of_Paper': c.Status_of_Paper,
            'Publish_Year': c.Publish_Year, 'Publish_Term': c.Publish_Term
        } for c in papers]
    if request.method == 'POST':
        print('Paper POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:review'))
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-courses'))

        sub = Submission.objects.get(id=submissionTrack_id)
        if sub.status == "Not Started":
            Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

        formset = FormSet(request.POST, initial=data)
        if formset.is_valid():
            print('Paper valid')
            new_papers = []
            if formset.has_changed():
                print('Data modified')
                for form in formset:
                    if form in formset.deleted_forms:
                        print('Deleted form skipped')
                        continue
                        # form.save()

                    print('Individual form is valid')
                    Title = form.cleaned_data.get('Title')
                    # Venue = form.cleaned_data.get('Venue')
                    # List_of_Authors = form.cleaned_data.get('List_of_Authors')
                    # Status_of_Paper = form.cleaned_data.get('Status_of_Paper')
                    # Publish_Term = form.cleaned_data.get('Publish_Term')
                    # Publish_Year = form.cleaned_data.get('Publish_Year')
                    #
                    # new_papers.append(Paper(
                    #     Author_id=userTableID.id, questionnaire_for_id=questionnaire_id, Title=Title,
                    #     Venue=Venue, List_of_Authors=List_of_Authors, Status_of_Paper=Status_of_Paper,
                    #     Publish_Term=Publish_Term, Publish_Year=Publish_Year
                    # ))
                    if not Title:
                        continue
                    p = form.save(commit=False)
                    p.Author_id=userTableID.id
                    p.questionnaire_for_id=questionnaire_id
                    new_papers.append(p)
                try:
                    with transaction.atomic():
                        # Replace the old with the new
                        Paper.objects.filter(Author_id=userTableID, questionnaire_for_id=questionnaire_id).delete()
                        # Paper.objects.bulk_create(new_papers)
                        for newpaper in new_papers:
                            newpaper.save()
                        messages.success(request, 'Your papers are saved.')
                        return redirect(reverse('questionnaire:form-papers'), {'formset': formset})

                except IntegrityError:  # If the transaction failed
                    print('Paper failed')
                    messages.error(request, 'There was an error saving your papers.')
            else:
                messages.error(request, 'Please modify data in order to Save!')
        else:
            print('Paper invalid')
            messages.error(request,
                           'There seems to be something wrong with your research paper details. Please make sure every entry below is valid.')
    elif papers.exists():
        print('Paper with existing data')
        formset = FormSet(initial=data)
    else:
        print('Paper GET')
        formset = FormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': ''
        })
    context = {
        'formset': formset
    }
    return render(request, 'questionnaire/papers.html', context)


@login_required()
def handleReview(request):
    if request.method == 'POST':
        submissionTrack_id = request.POST['var']
        if "submit" in submissionTrack_id:
            submissionTrack_id = submissionTrack_id[:-6]
            userTableID = User.objects.get(username=request.session['userNameSession']).id
            questionnaire_id = Submission.objects.get(id=submissionTrack_id).questionnaire_for_id
            current_data = Research.objects.get(username_id=userTableID, questionnaire_for_id=questionnaire_id)
            try:
                Submission.objects.filter(username_id=userTableID,questionnaire_for_id=questionnaire_id).update(
                    current_GPA=current_data.Current_GPA, status="Submitted For Review",
                    Current_Research_Advisor=str(current_data.Current_Research_Advisor),
                    Current_Academic_Advisor=str(current_data.Current_Academic_Advisor),
                )
            except Submission.DoesNotExist:
                messages.error('Error while submitting record, Inform Admin')
            return redirect('questionnaire:studentHome')

        else:
            return redirect('questionnaire:form-papers')

    else:
        print("in review page")
        questionnaireStatus = Submission.objects.get(id=request.session["questionnaireForIdSession"]).status
        questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
        userTableID = User.objects.get(username=request.session['userNameSession']).id
        if questionnaireStatus == "Saved":
            sessionFullName = request.session['fullNameSession']
            sessionUserName = request.session['userNameSession']
            sessionid = request.session['idSession']
            submissionList = Submission.objects.filter(username_id=sessionid).order_by("-questionnaire_for")
            profile = studentProfile.objects.get(email=sessionUserName)
            try:
                Submission.objects.filter(status='Review Submitted', username_id=sessionid)
                profile2 = \
                    Submission.objects.filter(status="Review Submitted", username_id=sessionid).order_by(
                        "-questionnaire_for_id").first()
            except Submission.DoesNotExist:
                profile2 = []
            course_dict = Course.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
            examAttempt_dict = QExam.objects.filter(username_id=userTableID,
                                                          questionnaire_for_id=questionnaire_id)
            techingAssistant_dict = TA.objects.filter(username_id=userTableID,
                                                                    questionnaire_for_id=questionnaire_id)
            paper_dict = Paper.objects.filter(Author_id=Student.objects.get(username_id=userTableID).id,
                                              questionnaire_for_id=questionnaire_id)
            research_dict = Research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)

            return render(request, 'questionnaire/review.html',
                          {'questionnaire_submit_fullname': request.session['fullNameSession'],
                           'course_dict': course_dict, 'examAttempt_dict': examAttempt_dict,
                           'techingAssistant_dict': techingAssistant_dict, 'paper_dict': paper_dict,
                           'research_dict': research_dict,'profile2': profile2, 'sessionFullName': sessionFullName,
                           'submissionList': submissionList, 'profile': profile, 'blankspace': '', 'submit': 'submit'})