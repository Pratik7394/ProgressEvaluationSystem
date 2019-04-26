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
from registration.models import studentProfile
from registration.models import studentName as Student
from django.contrib import messages

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

def studentHome(request):
    if request.method == 'POST':
        print("view")
        sessionid = request.session['idSession']
        submissionList = Submission.objects.filter(username_id=sessionid)
        print(submissionList)
        var = None
        var = request.POST['var']
        if "submit" in var:
            print("mission success")
        # a = a.get('var')
        # print("a")
        print("var")
        print(var)




        # for submission in submissionList:
        #     print("1st for")
        #     var = submission.id
        #     var = str(var)
        #     if var in request.POST:
        #         break
        #     else:
        #         var = None
        # print(var)
        #
        # if var is None:
        #     for submission in submissionList:
        #         print("2nd for")
        #         var = str(submission.id)+"submit"
        #         var = str(var)
        #         if var in request.POST:
        #             break
        #
        #
        #     var = var[:-6]
        #     var = int(var)
        #     submission = Submission.objects.get(id=var)
        #     print(submission)
        #     Submission.objects.filter(id=var).update(status="Submitted For Review")
        #     return redirect('questionnaire:studentHome')


        request.session["questionnaireForIdSession"] = var
        return redirect('questionnaire:viewSubmissions')

    # if 'editProfile' in request.POST:
    #     return redirect('registration:editProfileStudent')

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
            Submission.objects.filter(status='Review Submitted', username_id=sessionid)
            profile2 = \
                Submission.objects.filter(status="Review Submitted", username_id=sessionid).order_by(
                    "-questionnaire_for_id").first()
            print("profile2")
            print(profile2)
        except submissionTrack.DoesNotExist:
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

        if "submit" in submissionTrack_id:
            submissionTrack_id = submissionTrack_id[:-6]
            # print(submissionTrack_id)
            # id = submissionTrack_id.split()[0]
            # print(id)
            id = int(submissionTrack_id)
            print(submissionTrack_id)
            Submission.objects.filter(id=submissionTrack_id).update(status="Submitted For Review")
            return redirect('questionnaire:studentHome')

        else:
            submissionTrack_id = request.session["questionnaireForIdSession"]
            questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
            questionnaire_id = Submission.objects.get(id=submissionTrack_id).questionnaire_for_id
            questionnaire_submit_username = request.session['userNameSession']
            questionnaire_submit_fullname = request.session['fullNameSession']
            print((questionnaireStatus))
            userTableID = User.objects.get(username=questionnaire_submit_username).id

            if questionnaireStatus in ["Submitted For Review", "Review In Progress", "Review Submitted"]:
                # userTableID = User.objects.get(username=questionnaire_submit_username).id
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
                return redirect(reverse('questionnaire:form-courses'))

            ##################not started
            else:
                # currentReport = Questionnaire.objects.get(id=questionnaire_id)
                # try:
                #     previousReport = Questionnaire.objects.get(id=currentReport.previous_term_id)
                # except Questionnaire.DoesNotExist:
                #     previousReport = None
                #
                # if previousReport:
                #     print('Previous report exists')
                #
                #     # Load Research data
                #     try:
                #         research = Research.objects.get(username_id=userTableID, questionnaire_for_id=previousReport.id)
                #     except Research.DoesNotExist:
                #         research = None
                #     if research:
                #         print('Research Data exists and Loaded for this term')
                #         research_data = [Research(
                #             username_id=research.username_id, questionnaire_for_id=questionnaire_id,
                #             Topic=research.Topic,
                #             Proposal=research.Proposal, Defense=research.Defense,
                #             Current_Program_Year=research.Current_Program_Year,
                #             Current_Academic_Advisor=research.Current_Academic_Advisor,
                #             Current_GPA=research.Current_GPA,
                #             Current_Research_Advisor=research.Current_Research_Advisor
                #         )]
                #         # Research.objects.bulk_create(research_data)
                #
                #     # Load Courses
                #     courses = Course.objects.filter(username_id=userTableID, questionnaire_for_id=previousReport.id)
                #     if courses.exists():
                #         print('Course data exists and Loaded for this term')
                #         course_data = [Course(
                #             username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                #             Subject_Name=c.Subject_Name, Subject_Code=c.Subject_Code,
                #             Subject_Term_and_Year=c.Subject_Term_and_Year, Grade=c.Grade
                #         ) for c in courses]
                #         Course.objects.bulk_create(course_data)
                #
                #     # Load Qualifying Exam Attempts
                #     qexams = QExam.objects.filter(username_id=userTableID, questionnaire_for_id=previousReport.id)
                #     if qexams.exists():
                #         print('QExam data exists and Loaded for this term')
                #         qexam_data = [QExam(
                #             username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                #             Exam_Name=c.Exam_Name_id, Attempt_Number=c.Attempt_Number, Grade=c.Grade
                #         ) for c in qexams]
                #         QExam.objects.bulk_create(qexam_data)
                #
                #     # Load Teaching Assistantships
                #     teaching_assists = TA.objects.filter(username_id=userTableID,
                #                                          questionnaire_for_id=previousReport.id)
                #     if teaching_assists.exists():
                #         print('TA Data exists and Loaded for this term')
                #         ta_data = [TA(
                #             username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                #             Subject_Name=c.Subject_Name, Subject_Code=c.Subject_Code,
                #             Responsibilities=c.Responsibilities,
                #             In_Which_Semester=c.In_Which_Semester, Instructor_Name=c.Instructor_Name,
                #             Lecture_or_Presentation_Given=c.Lecture_or_Presentation_Given,
                #             Area_of_Improvement=c.Area_of_Improvement
                #         ) for c in teaching_assists]
                #         TA.objects.bulk_create(ta_data)
                #
                #     # Load Research Papers
                #     studentAuthor_id = Student.objects.get(username_id=userTableID)
                #     papers = Paper.objects.filter(Author_id=studentAuthor_id, questionnaire_for_id=previousReport.id)
                #     if papers.exists():
                #         print('Papers present and noted')
                #         paper_data = [Paper(
                #             Author_id=c.Author_id, questionnaire_for_id=questionnaire_id, Title=c.Title,
                #             Venue=c.Venue, List_of_Authors=c.List_of_Authors, Status_of_Paper=c.Status_of_Paper
                #         ) for c in papers]
                #         Paper.objects.bulk_create(paper_data)

                return redirect(reverse('questionnaire:form-courses'))

            ##################not started
            else:
                # currentReport = Questionnaire.objects.get(id=questionnaire_id)
                # try:
                #     previousReport = Questionnaire.objects.get(id=currentReport.previous_term_id)
                # except Questionnaire.DoesNotExist:
                #     previousReport = None
                #
                # if previousReport:
                #     print('Previous report exists')
                #
                #     # Load Research data
                #     try:
                #         research = Research.objects.get(username_id=userTableID, questionnaire_for_id=previousReport.id)
                #     except Research.DoesNotExist:
                #         research = None
                #     if research:
                #         print('Research Data exists and Loaded for this term')
                #         research_data = [Research(
                #             username_id=research.username_id, questionnaire_for_id=questionnaire_id,
                #             Topic=research.Topic,
                #             Proposal=research.Proposal, Defense=research.Defense,
                #             Current_Program_Year=research.Current_Program_Year,
                #             Current_Academic_Advisor=research.Current_Academic_Advisor,
                #             Current_GPA=research.Current_GPA,
                #             Current_Research_Advisor=research.Current_Research_Advisor
                #         )]
                #         # Research.objects.bulk_create(research_data)
                #
                #     # Load Courses
                #     courses = Course.objects.filter(username_id=userTableID, questionnaire_for_id=previousReport.id)
                #     if courses.exists():
                #         print('Course data exists and Loaded for this term')
                #         course_data = [Course(
                #             username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                #             Subject_Name=c.Subject_Name, Subject_Code=c.Subject_Code,
                #             Subject_Term_and_Year=c.Subject_Term_and_Year, Grade=c.Grade
                #         ) for c in courses]
                #         Course.objects.bulk_create(course_data)
                #
                #     # Load Qualifying Exam Attempts
                #     qexams = QExam.objects.filter(username_id=userTableID, questionnaire_for_id=previousReport.id)
                #     if qexams.exists():
                #         print('QExam data exists and Loaded for this term')
                #         qexam_data = [QExam(
                #             username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                #             Exam_Name=c.Exam_Name_id, Attempt_Number=c.Attempt_Number, Grade=c.Grade
                #         ) for c in qexams]
                #         QExam.objects.bulk_create(qexam_data)
                #
                #     # Load Teaching Assistantships
                #     teaching_assists = TA.objects.filter(username_id=userTableID,
                #                                          questionnaire_for_id=previousReport.id)
                #     if teaching_assists.exists():
                #         print('TA Data exists and Loaded for this term')
                #         ta_data = [TA(
                #             username_id=c.username_id, questionnaire_for_id=questionnaire_id,
                #             Subject_Name=c.Subject_Name, Subject_Code=c.Subject_Code,
                #             Responsibilities=c.Responsibilities,
                #             In_Which_Semester=c.In_Which_Semester, Instructor_Name=c.Instructor_Name,
                #             Lecture_or_Presentation_Given=c.Lecture_or_Presentation_Given,
                #             Area_of_Improvement=c.Area_of_Improvement
                #         ) for c in teaching_assists]
                #         TA.objects.bulk_create(ta_data)
                #
                #     # Load Research Papers
                #     studentAuthor_id = Student.objects.get(username_id=userTableID)
                #     papers = Paper.objects.filter(Author_id=studentAuthor_id, questionnaire_for_id=previousReport.id)
                #     if papers.exists():
                #         print('Papers present and noted')
                #         paper_data = [Paper(
                #             Author_id=c.Author_id, questionnaire_for_id=questionnaire_id, Title=c.Title,
                #             Venue=c.Venue, Coauthor=c.Coauthor, Status_of_Paper=c.Status_of_Paper
                #         ) for c in papers]
                #         Paper.objects.bulk_create(paper_data)

                    return redirect(reverse('questionnaire:form-courses'))

@login_required()
def handleCourses(request):
    course_formset = None
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    CourseFormSet = formset_factory(CourseForm, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    courses = Course.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).order_by(
        '-Subject_Term_and_Year', 'Grade', 'Subject_Name')
    course_data = [{}]
    if courses.exists():
        print('Course data exists and noted')
        course_data = [{
            'username_id': c.username_id, 'questionnaire_for_id': c.questionnaire_for_id,
            'Subject_Name': c.Subject_Name, 'Subject_Code': c.Subject_Code,
            'Subject_Term_and_Year': c.Subject_Term_and_Year, 'Grade': c.Grade
        } for c in courses]
    if request.method == 'POST':
        print('Course POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-qexams'))
        if 'save' in request.POST:
            sub = Submission.objects.get(id=submissionTrack_id)
            if sub.status == "Not Started":
                Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

            course_formset = CourseFormSet(request.POST, initial=course_data)
            if course_formset.is_valid():
                print('Course valid')
                new_courses = []
                if course_formset.has_changed():
                    print('Data modified')
                    for course_form in course_formset:
                        if course_form in course_formset.deleted_forms:
                            continue
                        Subject_Name = course_form.cleaned_data.get('Subject_Name')
                        Subject_Code = course_form.cleaned_data.get('Subject_Code')
                        Subject_Term_and_Year = course_form.cleaned_data.get('Subject_Term_and_Year')
                        Grade = course_form.cleaned_data.get('Grade')

                        new_courses.append(Course(
                            username_id=userTableID, questionnaire_for_id=questionnaire_id,
                            Subject_Name=Subject_Name,
                            Subject_Code=Subject_Code, Subject_Term_and_Year=Subject_Term_and_Year, Grade=Grade
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
def handleQExams(request):
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    QExamFormSet = formset_factory(QExamForm, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    qexams = QExam.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id).order_by(
        'Exam_Name', 'Attempt_Number')
    qexam_data = [{}]
    if qexams.exists():
        print('QExam data exists and noted')
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
        if 'save' in request.POST:
            sub = Submission.objects.get(id=submissionTrack_id)
            if sub.status == "Not Started":
                Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

            qexam_formset = QExamFormSet(request.POST, initial=qexam_data)
            if qexam_formset.is_valid():
                print('QExam valid')
                new_qexams = []
                if qexam_formset.has_changed():
                    print('Data modified')
                    for qexam_form in qexam_formset:
                        if qexam_form in qexam_formset.deleted_forms:
                            continue
                        Exam_Name_id = Exams.objects.get(exam_Name=qexam_form.cleaned_data.get('Exam_Name')).id
                        Attempt_Number = qexam_form.cleaned_data.get('Attempt_Number')
                        Grade = qexam_form.cleaned_data.get('Grade')
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
def handleTA(request):
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    TAFormSet = formset_factory(TeachingForm, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = User.objects.get(username=request.session['userNameSession']).id
    teaching_assists = TA.objects.filter(username_id=userTableID, questionnaire_for_id=questionnaire_id)
    ta_data = [{}]
    if teaching_assists.exists():
        print('TA Data exists and Noted')
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

        sub = Submission.objects.get(id=submissionTrack_id)
        if sub.status == "Not Started":
            Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

        ta_formset = TAFormSet(request.POST, initial=ta_data)
        if ta_formset.is_valid():
            print('TA valid')
            new_teaching_assists = []
            if ta_formset.has_changed():
                print('Data modified')
                for ta_form in ta_formset:
                    if ta_form in ta_formset.deleted_forms:
                        continue
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
    research_data = {}
    if research:
        print('Research Data exists and Noted')
        research_data = {
            'username_id': research.username_id, 'questionnaire_for_id': research.questionnaire_for_id,
            'Topic': research.Topic, 'Proposal': research.Proposal, 'Defense': research.Defense,
            'Proposal_Status': research.Proposal_Status, 'Defence_Status': research.Defence_Status,
            'Current_Academic_Advisor': research.Current_Academic_Advisor, 'Current_GPA': research.Current_GPA,
            'Current_Research_Advisor': research.Current_Research_Advisor, 'Thesis_Committee': research.Thesis_Committee
        }
    if request.method == 'POST':
        print('Research POST')
        if 'next' in request.POST:
            return redirect(reverse('questionnaire:form-papers'))
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-ta'))

        sub = Submission.objects.get(id=submissionTrack_id)
        if sub.status == "Not Started":
            Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

        research_form = ResearchForm(request.POST)
        if research_form.is_valid():
            print('Research data is valid')
            Topic = research_form.cleaned_data.get('Topic')
            Proposal = research_form.cleaned_data.get('Proposal')
            Defense = research_form.cleaned_data.get('Defense')
            Current_GPA = research_form.cleaned_data.get('Current_GPA')
            Current_Academic_Advisor_id = research_form.cleaned_data.get('Current_Academic_Advisor_id')
            Current_Research_Advisor_id = research_form.cleaned_data.get('Current_Research_Advisor_id')
            Thesis_Committee = research_form.cleaned_data.get('Thesis_Committee')
            Defence_Status = research_form.cleaned_data.get('Defence_Status')
            Proposal_Status = research_form.cleaned_data.get('Proposal_Status')
            newresearch = [Research(
                username_id=userTableID, questionnaire_for_id=questionnaire_id, Topic=Topic, Proposal=Proposal,
                Defense=Defense, Current_Research_Advisor_id=Current_Research_Advisor_id, Current_GPA=Current_GPA,
                Current_Academic_Advisor_id=Current_Academic_Advisor_id, Proposal_Status=Proposal_Status,
                Defence_Status = Defence_Status, Thesis_Committee=Thesis_Committee
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
            print('Research data is invalid')
            messages.error(request,
                           'There seems to be something wrong with your research details. Please make sure every entry below is valid.')
            # return redirect('questionnaire:form-research')
    elif research:
        print('Research Get with existing data')
        research_form = ResearchForm(initial=research_data)
    else:
        print('Research GET')
        research_form = ResearchForm()
    context = {
        'research_form': research_form
    }
    return render(request, 'questionnaire/step4.html', context)

@login_required()
def handlePapers(request):
    submissionTrack_id = request.session["questionnaireForIdSession"]
    questionnaireStatus = Submission.objects.get(id=submissionTrack_id).status
    if not (questionnaireStatus == 'Not Started' or questionnaireStatus == 'Saved'):
        messages.error(request, "You currently don't have permission to access the requested page.")
        return redirect(reverse('questionnaire:studentHome'))

    PaperFormSet = formset_factory(PaperForm, can_delete=True, extra=1)
    questionnaire_id = Submission.objects.get(id=request.session["questionnaireForIdSession"]).questionnaire_for_id
    userTableID = Student.objects.get(username_id=User.objects.get(username=request.session['userNameSession']).id)
    papers = Paper.objects.filter(Author_id=userTableID.id, questionnaire_for_id=questionnaire_id).order_by(
        'Status_of_Paper', 'Title')
    paper_data = [{}]
    if papers.exists():
        print('Papers present and noted')
        paper_data = [{
            'Author_id': c.Author_id, 'questionnaire_for_id': c.questionnaire_for_id, 'Title': c.Title,
            'Venue': c.Venue, 'List_of_Authors': c.List_of_Authors, 'Status_of_Paper': c.Status_of_Paper,
            'Publish_Year':c.Publish_Year, 'Publish_Term':c.Publish_Term
        } for c in papers]
    if request.method == 'POST':
        print('Paper POST')
        if 'prev' in request.POST:
            return redirect(reverse('questionnaire:form-research'))

        sub = Submission.objects.get(id=submissionTrack_id)
        if sub.status == "Not Started":
            Submission.objects.filter(id=submissionTrack_id).update(status="Saved")

        paper_formset = PaperFormSet(request.POST, initial=paper_data)
        if paper_formset.is_valid():
            print('Paper valid')
            new_papers = []
            if paper_formset.has_changed():
                print('Data modified')
                for paper_form in paper_formset:
                    if paper_form in paper_formset.deleted_forms:
                        continue
                    Title = paper_form.cleaned_data.get('Title')
                    Venue = paper_form.cleaned_data.get('Venue')
                    List_of_Authors = paper_form.cleaned_data.get('List_of_Authors')
                    Status_of_Paper = paper_form.cleaned_data.get('Status_of_Paper')
                    Publish_Term = paper_form.cleaned_data.get('Publish_Term')
                    Publish_Year = paper_form.cleaned_data.get('Publish_Year')

                    new_papers.append(Paper(
                        Author_id=userTableID.id, questionnaire_for_id=questionnaire_id, Title=Title,
                        Venue=Venue, List_of_Authors=List_of_Authors, Status_of_Paper=Status_of_Paper,
                        Publish_Term=Publish_Term, Publish_Year=Publish_Year
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
                    # return render(reverse('questionnaire:form-papers'), {'paper_formset': paper_formset})
            else:
                messages.error(request, 'Please modify data in order to Save!')
        else:
            print('Paper invalid')
            messages.error(request,
                           'There seems to be something wrong with your research paper details. Please make sure every entry below is valid.')
            if (paper_formset.errors):
                for er in paper_formset.errors:
                    print(str(er))
            # return redirect(reverse('questionnaire:form-papers'), {'paper_formset': paper_formset})
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
