from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from registration.models import studentProfile
from registration.models import studentName as Student
from django.contrib import messages
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from registration.decorators import user_type_student

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

static_data = {
    'display': {
        'QExams': 'Qualifying Exams',
        'Research': 'Academics and Research',
        'Papers': 'Research Papers',
        'Teaching': 'Teaching Assist',
        'Courses': 'Courses'
    }
}


# Create your views here.

def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


@login_required
@user_type_student
def studentHome(request):
    if request.method == 'POST':
        var = request.POST['var']
        request.session["questionnaireForIdSession"] = var
        return redirect('questionnaire:viewSubmissions')

    else:
        sessionFullName = request.session['fullNameSession']
        sessionUserName = request.session['userNameSession']
        sessionid = request.session['idSession']
        submissionList = Submission.objects.filter(username_id=sessionid).order_by("-questionnaire_for")
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
        except Submission.DoesNotExist:
            profile2 = []

        return render(request, 'registration/homeStudent.html',
                      {'profile2': profile2, 'sessionFullName': sessionFullName, 'submissionList': submissionList,
                       'profile': profile, 'blankspace': blankspace, })


"""
@load_data: Previous Questionnaire Data loader
@param Request: Request object for message propagation.
@param userTableID: User ID to get data.
@param questionnaire_id: Questionnaire ID to get data from previous Questionnaire and copy to the current one.
"""


def load_data(request, userTableID, questionnaire_id):
    print('Data loader started')
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
        research = None

        try:
            current_research = Research.objects.get(username_id=userTableID, questionnaire_for_id=questionnaire_id)
        except Research.DoesNotExist:
            current_research = None
            try:
                research = Research.objects.get(username_id=userTableID, questionnaire_for_id=previousReport.id)
            except Research.DoesNotExist:
                research = None
        if current_research and research:
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
        current_courses = Course.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
        courses = Course.objects.filter(username_id=userTableID, questionnaire_for_id=previousReport.id)
        if courses.exists() and not current_courses.exists():
            print('Course data exists and Loaded for this term')
            data = [Course(
                username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                Subject_Name=c.Subject_Name, Subject_Code=c.Subject_Code,
                Subject_Year=c.Subject_Year, Subject_Term=c.Subject_Term, Grade=c.Grade
            ) for c in courses]
            try:
                with transaction.atomic():
                    Course.objects.bulk_create(data)
                    messages.success(request, 'Your Courses are preloaded.')
            except IntegrityError:
                # If the transaction failed
                messages.error(request, "Your Courses couldn't be preloaded.")

        # Load Qualifying Exam Attempts
        current_qexams = QExam.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
        qexams = QExam.objects.filter(username_id=userTableID, questionnaire_for_id=previousReport.id)
        if qexams.exists() and not current_qexams.exists():
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
        current_ta = TA.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
        teaching_assists = TA.objects.filter(username_id=userTableID,questionnaire_for_id=previousReport.id)
        if teaching_assists.exists() and not current_ta.exists():
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
                    messages.success(request, 'Your TA details are preloaded.')
            except IntegrityError:
                # If the transaction failed
                messages.error(request, "Your TA details couldn't be preloaded.")

        # Load Research Papers
        studentAuthor_id = Student.objects.get(username_id=userTableID)
        current_papers = Paper.objects.filter(Author_id=studentAuthor_id, questionnaire_for_id=questionnaire_id)
        papers = Paper.objects.filter(Author_id=studentAuthor_id, questionnaire_for_id=previousReport.id)
        if papers.exists() and  not current_papers.exists():
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
    return

@user_type_student
@login_required()
def viewSubmissions(request):
    if request.method == 'POST':
        return redirect('questionnaire:studentHome')

    else:
        submissionTrack_id = request.session["questionnaireForIdSession"]

        if "review" in submissionTrack_id:
            submissionTrack_id = submissionTrack_id[:-6]
            request.session["questionnaireForIdSession"] = submissionTrack_id
            return redirect('questionnaire:review')

        else:
            submissionTrack_id = request.session["questionnaireForIdSession"]
            questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
            questionnaire_id = Submission.objects.get(id=submissionTrack_id).questionnaire_for_id
            questionnaire_submit_username = request.session['userNameSession']
            questionnaire_submit_fullname = request.session['fullNameSession']
            userTableID = User.objects.get(username=questionnaire_submit_username).id

            if questionnaireStatus in ["Submitted For Review", "Review In Progress", "Review Submitted"]:
                course_dict = Course.objects.filter(username_id=userTableID,
                                                    questionnaire_for_id=questionnaire_id).order_by(
                    '-Subject_Year', 'Subject_Term', 'Grade', 'Subject_Name')
                examAttempt_dict = QExam.objects.filter(username_id=userTableID,
                                                        questionnaire_for_id=questionnaire_id).order_by(
                    'Exam_Name', 'Attempt_Number')
                techingAssistant_dict = TA.objects.filter(username_id=userTableID,
                                                          questionnaire_for_id=questionnaire_id).order_by(
                    '-Subject_Year', 'Subject_Term', 'Subject_Name')
                paper_dict = Paper.objects.filter(Author_id=Student.objects.get(username_id=userTableID).id,
                                                  questionnaire_for_id=questionnaire_id).order_by(
                    '-Status_of_Paper', 'Title')
                research_dict = Research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)

                return render(request, 'questionnaire/submissionView.html',
                              {'questionnaire_submit_fullname': questionnaire_submit_fullname,
                               'course_dict': course_dict, 'examAttempt_dict': examAttempt_dict,
                               'techingAssistant_dict': techingAssistant_dict, 'paper_dict': paper_dict,
                               'research_dict': research_dict})
            elif questionnaireStatus == "Saved":
                return redirect(reverse('questionnaire:form-research'))
            else: # status == 'not started'
                load_data(request, userTableID, questionnaire_id)
                return redirect(reverse('questionnaire:form-research'))

'''
    # @requestHandler: Generic method that takes care of rendering data for every object,
    # considering both common and distinct scenarios/attributes.
    # @param Object: The Model object that is being used/modified.
    # @param objectName: CamelCase string representation of the object name that matches with .html equivalent.
'''


@user_type_student
@login_required
def requestHandler(request, Object, objectName):
    sessionid = request.session['idSession']
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))
    questionnaire = Submission.objects.get(id=request.session["questionnaireForIdSession"])
    questionnaire_id = questionnaire.questionnaire_for_id
    questionnairefor = questionnaire.questionnaire_for
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    formMap = {
        'Courses': CourseForm,
        'QExams': QExamForm,
        'Teaching': TeachingForm,
        'Research': ResearchForm,
        'Papers': PaperForm
    }
    if objectName == 'Research':
        FormSet = formset_factory(formMap[objectName], can_delete=True, extra=1, max_num=1)
    else:
        FormSet = formset_factory(formMap[objectName], can_delete=True, extra=1)
    if objectName == 'Papers':
        try:
            userTableID = Student.objects.get(
                username_id=User.objects.get(username=request.session['userNameSession']).id).id
        except Student.DoesNotExist:
            userTableID = User.objects.get(username=request.session['userNameSession']).id
        current_data = Object.objects.filter(Author_id=userTableID, questionnaire_for_id=questionnaire_id)
    else:
        current_data = Object.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
    data = [{}]
    if current_data.exists():
        print(objectName + ' data exists and noted')
        if objectName == 'QExams':
            data = [{
                'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
                'Exam_Name': c.Exam_Name_id, 'Attempt_Number': c.Attempt_Number, 'Grade': c.Grade
            } for c in current_data]
        elif objectName == 'Courses':
            data = [{
                'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
                'Subject_Name': c.Subject_Name, 'Subject_Code': c.Subject_Code,
                'Subject_Year': c.Subject_Year, 'Subject_Term': c.Subject_Term, 'Grade': c.Grade
            } for c in current_data]
        elif objectName == 'Teaching':
            data = [{
                'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
                'Subject_Name': c.Subject_Name, 'Subject_Code': c.Subject_Code, 'Responsibilities': c.Responsibilities,
                'Subject_Year': c.Subject_Year, 'Subject_Term': c.Subject_Term, 'Instructor_Name': c.Instructor_Name,
                'Lecture_or_Presentation_Given': c.Lecture_or_Presentation_Given,
                'Area_of_Improvement': c.Area_of_Improvement
            } for c in current_data]
        elif objectName == 'Papers':
            data = [{
                'Author_id': c.Author_id, 'questionnaire_for_id': c.questionnaire_for_id, 'Title': c.Title,
                'Venue': c.Venue, 'List_of_Authors': c.List_of_Authors, 'Status_of_Paper': c.Status_of_Paper,
                'Publish_Year': c.Publish_Year, 'Publish_Term': c.Publish_Term
            } for c in current_data]
        elif objectName == 'Research':
            data = [{
                'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
                'Topic': c.Topic, 'Proposal': c.Proposal, 'Defense': c.Defense,
                'Proposal_Status': c.Proposal_Status, 'Defense_Status': c.Defense_Status,
                'Current_Academic_Advisor': c.Current_Academic_Advisor, 'Current_GPA': c.Current_GPA,
                'Current_Research_Advisor': c.Current_Research_Advisor,
                'Thesis_Committee': c.Thesis_Committee
            } for c in current_data]

    if request.method == 'POST':
        print(objectName + ' POST')
        formset = FormSet(request.POST, initial=data)
        if formset.is_valid():
            print(objectName + ' valid')
            new_data = []
            if formset.has_changed():
                print('Data modified')
                for form in formset:
                    # Skip forms that are selected for deletion
                    if form in formset.deleted_forms:
                        continue
                    if objectName == 'QExams':
                        try:
                            unique_or_required_field = Exams.objects.get(
                                exam_Name=form.cleaned_data.get('Exam_Name')).id
                        except Exams.DoesNotExist:
                            continue
                    elif objectName in ['Courses', 'Teaching']:
                        unique_or_required_field = form.cleaned_data.get('Subject_Name')
                    elif objectName == 'Papers':
                        unique_or_required_field = form.cleaned_data.get('Title')
                    elif objectName == 'Research':
                        unique_or_required_field = form.cleaned_data.get('Topic')

                    # If we don't have unique field, this would be an empty form.
                    # Hence we skip this form
                    if not unique_or_required_field:
                        continue
                    thisForm = form.save(commit=False)
                    if objectName == 'Papers':
                        thisForm.Author_id = userTableID
                    else:
                        thisForm.username_id = userTableID

                    thisForm.questionnaire_for_id = questionnaire_id
                    new_data.append(thisForm)

                try:
                    with transaction.atomic():
                        # Replace the old with the new
                        if objectName == 'Papers':
                            Object.objects.filter(Author_id=userTableID, questionnaire_for_id=questionnaire_id).delete()
                        else:
                            Object.objects.filter(username_id=userTableID,
                                                  questionnaire_for_id=questionnaire_id).delete()
                        for eachInstance in new_data:
                            eachInstance.save()

                        # notify our users that Qualifying Exam Attempts are saved
                        messages.success(request, 'Your ' + static_data['display'][objectName] + ' data is saved.')

                        if questionnaireStatus == "Not Started":
                            Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

                        if objectName == 'QExams':
                            if 'next' in request.POST:
                                return redirect(reverse('questionnaire:form-ta'))
                            if 'prev' in request.POST:
                                return redirect(reverse('questionnaire:form-research'))
                            return redirect(reverse('questionnaire:form-qexams'))
                        elif objectName == 'Courses':
                            if 'next' in request.POST:
                                return redirect(reverse('questionnaire:form-papers'))
                            if 'prev' in request.POST:
                                return redirect(reverse('questionnaire:form-ta'))
                            return redirect(reverse('questionnaire:form-courses'))
                        elif objectName == 'Teaching':
                            if 'next' in request.POST:
                                return redirect(reverse('questionnaire:form-courses'))
                            if 'prev' in request.POST:
                                return redirect(reverse('questionnaire:form-qexams'))
                            return redirect(reverse('questionnaire:form-ta'))
                        elif objectName == 'Papers':
                            if 'next' in request.POST:
                                return redirect(reverse('questionnaire:review'))
                            if 'prev' in request.POST:
                                return redirect(reverse('questionnaire:form-courses'))
                            return redirect(reverse('questionnaire:form-papers'))
                        elif objectName == 'Research':
                            if 'next' in request.POST:
                                return redirect(reverse('questionnaire:form-qexams'))
                            if 'prev' in request.POST:
                                return redirect(reverse('questionnaire:studentHome'))
                            return redirect(reverse('questionnaire:form-research'))

                except IntegrityError:  # If the transaction failed
                    print(objectName + ' failed')
                    messages.error(request, 'There was an error while saving your ' +
                                   static_data['display'][objectName] + ' data. Please avoid duplicate/invalid entries')
            else:
                if not ('save' in request.POST):
                    if objectName == 'QExams':
                        if 'next' in request.POST:
                            return redirect(reverse('questionnaire:form-ta'))
                        if 'prev' in request.POST:
                            return redirect(reverse('questionnaire:form-research'))
                    elif objectName == 'Courses':
                        if 'next' in request.POST:
                            return redirect(reverse('questionnaire:form-papers'))
                        if 'prev' in request.POST:
                            return redirect(reverse('questionnaire:form-ta'))
                    elif objectName == 'Teaching':
                        if 'next' in request.POST:
                            return redirect(reverse('questionnaire:form-courses'))
                        if 'prev' in request.POST:
                            return redirect(reverse('questionnaire:form-qexams'))
                    elif objectName == 'Papers':
                        if 'next' in request.POST:
                            return redirect(reverse('questionnaire:review'))
                        if 'prev' in request.POST:
                            return redirect(reverse('questionnaire:form-courses'))
                    elif objectName == 'Research':
                        if 'next' in request.POST:
                            return redirect(reverse('questionnaire:form-qexams'))
                        if 'prev' in request.POST:
                            return redirect(reverse('questionnaire:studentHome'))
                messages.error(request, 'No changes detected in ' + static_data['display'][objectName] + ' data!')
        else:
            print(objectName + ' invalid')
            messages.error(request,
                           'There seems to be something wrong with your ' + static_data['display'][objectName] +
                           ' data. Please make sure all entries below are valid.')
    elif current_data.exists():
        print(objectName + ' existing')
        formset = FormSet(initial=data)
    else:
        print(objectName + ' GET')
        formset = FormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': ''
        }, initial=data)

    context = {
        'formset': formset,
        'QuestionnaireFor': questionnairefor, 'questionnaireStatus': questionnaireStatus
    }
    return render(request, 'questionnaire/' + objectName.lower() + '.html', context)


@user_type_student
@login_required()
def handleResearch(request):
    # return requestHandler(request, Research, 'Research')
    sessionid = request.session['idSession']
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    questionnaire = Submission.objects.get(id=request.session["questionnaireForIdSession"])
    questionnaire_id = questionnaire.questionnaire_for_id
    questionnairefor = questionnaire.questionnaire_for
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
        form = ResearchForm(request.POST, initial=data)
        if form.is_valid():
            print('Research data is valid')
            if form.has_changed():
                print('Research data is changed')
                Topic = form.cleaned_data.get('Topic')
                if Topic:
                    thisForm = form.save(commit=False)
                    thisForm.username_id = userTableID

                    thisForm.questionnaire_for_id = questionnaire_id
                    try:
                        with transaction.atomic():
                            # Replace the old with the new
                            Research.objects.filter(username_id=userTableID,
                                                    questionnaire_for_id=questionnaire_id).delete()
                            thisForm.save()

                            # notify our users that research details are saved
                            messages.success(request, 'Your research details are saved.')

                            if questionnaireStatus == "Not Started":
                                Submission.objects.filter(id=submissionTrack_id).update(status="Saved")
                            if 'next' in request.POST:
                                return redirect(reverse('questionnaire:form-qexams'))
                            if 'prev' in request.POST:
                                return redirect(reverse('questionnaire:studentHome'))
                            return redirect(reverse('questionnaire:form-research'))
                    except IntegrityError:  # If the transaction failed
                        print('Research data failed to save')
                        messages.error(request, 'There was an error while saving your research details.')
                else:
                    messages.error(request, 'There is some data missing. Couldn\'t save your data')
            else:
                if 'next' in request.POST:
                    return redirect(reverse('questionnaire:form-qexams'))
                if 'prev' in request.POST:
                    return redirect(reverse('questionnaire:studentHome'))
                messages.error(request, 'No changes detected!')
        else:
            print('Research data is invalid')
            messages.error(request,
                           'There seems to be something wrong with your research details. Please make sure every entry below is valid.')
    elif research:
        print('Research Get with existing data')
        form = ResearchForm(initial=data)
    else:
        print('Research GET')
        form = ResearchForm()
    context = {
        'form': form,
        'QuestionnaireFor': questionnairefor, 'questionnaireStatus': questionnaireStatus
    }
    return render(request, 'questionnaire/research.html', context)


@login_required()
def handleQExams(request):
    return requestHandler(request, QExam, 'QExams')


@login_required()
def handleTA(request):
    return requestHandler(request, TA, 'Teaching')


@login_required()
def handleCourses(request):
    return requestHandler(request, Course, 'Courses')


@login_required()
def handlePapers(request):
    return requestHandler(request, Paper, 'Papers')


@user_type_student
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
                Submission.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).update(
                    current_GPA=current_data.Current_GPA, status="Submitted For Review",
                    Current_Research_Advisor=str(current_data.Current_Research_Advisor),
                    Current_Academic_Advisor=str(current_data.Current_Academic_Advisor),
                )
            except Submission.DoesNotExist:
                messages.error('Error while submitting record, Inform Admin')
            return redirect('questionnaire:studentHome')

        else:  # Back button
            return redirect('questionnaire:form-research')

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

            course_dict = Course.objects.filter(username_id=userTableID,
                                                questionnaire_for_id=questionnaire_id).order_by(
                '-Subject_Year', 'Subject_Term', 'Grade', 'Subject_Name')
            examAttempt_dict = QExam.objects.filter(username_id=userTableID,
                                                    questionnaire_for_id=questionnaire_id).order_by(
                'Exam_Name', 'Attempt_Number')
            techingAssistant_dict = TA.objects.filter(username_id=userTableID,
                                                      questionnaire_for_id=questionnaire_id).order_by(
                '-Subject_Year', 'Subject_Term', 'Subject_Name')
            paper_dict = Paper.objects.filter(Author_id=Student.objects.get(username_id=userTableID).id,
                                              questionnaire_for_id=questionnaire_id).order_by(
                '-Status_of_Paper', 'Title')
            research_dict = Research.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)

            return render(request, 'questionnaire/review.html',
                          {'questionnaire_submit_fullname': request.session['fullNameSession'],
                           'course_dict': course_dict, 'examAttempt_dict': examAttempt_dict,
                           'techingAssistant_dict': techingAssistant_dict, 'paper_dict': paper_dict,
                           'research_dict': research_dict, 'profile2': profile2, 'sessionFullName': sessionFullName,
                           'submissionList': submissionList, 'profile': profile, })
