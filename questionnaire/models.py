from django.db import models
from django.contrib.auth.models import User
from registration.models import studentName, professorName
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime


class questionnaire(models.Model):
    questionnaire_for = models.CharField(max_length=100, unique=True)
    previous_term = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    Active = 'Active'
    Inactive = 'Inactive'
    choices = (
        (Active, 'Active'),
        (Inactive, 'Inactive'),
    )
    status = models.CharField(max_length=10, choices=choices)
    start_date = models.DateField(default=datetime.datetime.now)
    end_date = models.DateField()

    def __str__(self):
        return self.questionnaire_for


class qualifyingExam(models.Model):
    exam_Name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.exam_Name


class submissionTrack(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, on_delete=models.PROTECT)

    Not_Started = 'Not Started'
    Saved = 'Saved'
    Submitted_For_Review = 'Submitted For Review'
    Review_In_Progress = 'Review In Progress'
    Review_Submitted = 'Review Submitted'

    choices = (
        (Not_Started, Not_Started),
        (Saved, Saved),
        (Submitted_For_Review, Submitted_For_Review),
        (Review_In_Progress, Review_In_Progress),
        (Review_Submitted, Review_Submitted),
    )
    status = models.CharField(max_length=25, choices=choices)

    ##Displaying Fields
    fullname = models.CharField(max_length=500)
    current_GPA = models.FloatField(blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    Current_Research_Advisor = models.CharField(max_length=500, blank=True)
    Current_Academic_Advisor = models.CharField(max_length=500, blank=True)
    Current_Program_Year = models.IntegerField(blank=True, null=True)

    #############feedback############
    Feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('username', 'questionnaire_for', 'status',)

    def __str__(self):
        return str(self.username) + " " + self.fullname + " " + str(
            self.questionnaire_for) + " " + str(self.status)


class course(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)
    Subject_Name = models.CharField(max_length=200)
    Subject_Code = models.CharField(max_length=50)
    Subject_Term_and_Year = models.CharField(max_length=50)
    Grade = models.CharField(max_length=20)

    class Meta:
        unique_together = ('username', 'questionnaire_for', 'Subject_Name', 'Subject_Code',)

    def __str__(self):
        return str(self.username) + " " + str(
            self.questionnaire_for) + " " + self.Subject_Name + " " + self.Subject_Term_and_Year


class examAttempt(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)
    Exam_Name = models.ForeignKey(qualifyingExam, db_column="exam_Name", on_delete=models.PROTECT)
    Attempt_Number = models.IntegerField(default="1", validators=[MaxValueValidator(4), MinValueValidator(1)])
    Grade = models.CharField(max_length=10)

    class Meta:
        unique_together = ('username', 'questionnaire_for', 'Exam_Name', 'Attempt_Number',)

    def __str__(self):
        return str(self.username) + str(self.questionnaire_for) + " " + str(self.Exam_Name) + " " + str(
            self.Attempt_Number)


class techingAssistant(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)
    Subject_Name = models.CharField(max_length=200)
    Subject_Code = models.CharField(max_length=50)
    In_Which_Semester = models.CharField(max_length=50)
    Instructor_Name = models.CharField(max_length=200)
    Responsibilities = models.TextField(max_length=5000)
    Lecture_or_Presentation_Given = models.TextField(max_length=5000)
    Area_of_Improvement = models.TextField(max_length=5000)

    class Meta:
        unique_together = ('username', 'questionnaire_for', 'Subject_Name', 'In_Which_Semester')

    def __str__(self):
        return str(self.username) + " " + str(
            self.questionnaire_for) + " " + self.Subject_Code + " " + self.In_Which_Semester

class paper(models.Model):
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)
    Title = models.CharField(max_length=5000)
    Venue = models.CharField(max_length=1000)

    IP = 'In Progress'
    UR = 'Under Revision'
    PU = 'Published'
    status_choices = (
        (IP, IP),
        (UR, UR),
        (PU, PU),
    )
    Status_of_Paper = models.CharField(max_length=15, choices=status_choices)

    Author = models.ForeignKey(studentName, db_column="name", on_delete=models.PROTECT, blank=True)
    Coauthor = models.CharField(max_length=1000, blank=True)

    class Meta:
        unique_together = ('Author', 'questionnaire_for', 'Title')

    def __str__(self):
        return str(self.Author) + " " + str(self.questionnaire_for) + " " + self.Title


class research(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)
    Topic = models.CharField(max_length=5000, blank=True)
    Proposal = models.CharField(max_length=5000, blank=True)
    Defense = models.CharField(max_length=5000, blank=True)
    Current_GPA = models.FloatField(validators=[MaxValueValidator(4.0)], blank=True, null=True)
    Current_Academic_Advisor = models.ForeignKey(professorName, related_name='academic_advisor',
                                                 on_delete=models.PROTECT, blank=True, null=True)
    Current_Research_Advisor = models.ForeignKey(professorName, related_name='research_advisor',
                                                 on_delete=models.PROTECT, blank=True, null=True)
    Current_Program_Year = models.IntegerField(default="1", validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('username', 'questionnaire_for')

    def __str__(self):
        return str(self.username) + " " + str(self.questionnaire_for) + " " + self.Topic