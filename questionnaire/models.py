from django.db import models
from django.contrib.auth.models import User
from registration.models import studentName, professorName
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
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
    status = models.CharField(max_length=10, choices=choices, default=Inactive)
    start_date = models.DateField(default=datetime.datetime.now)
    end_date = models.DateField()

    def __str__(self):
        return self.questionnaire_for

    # def save(self, *args, **kwargs):
    #     if self.status == 'Active':
    #         try:
    #             temp = questionnaire.objects.get(status='Active')
    #             if self != temp:
    #                 temp.status = 'Inactive'
    #                 temp.save()
    #         except questionnaire.DoesNotExist:
    #             pass
    #     super(questionnaire, self).save(*args, **kwargs)


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
        (Not_Started, 'Not Started'),
        (Saved, 'Saved'),
        (Submitted_For_Review, 'Submitted For Review'),
        (Review_In_Progress, 'Review In Progress'),
        (Review_Submitted, 'Review Submitted'),
    )
    status = models.CharField(max_length=25, choices=choices)

    ##Displaying Fields
    fullname = models.CharField(max_length=500)
    current_GPA = models.FloatField(blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    Current_Research_Advisor = models.CharField(max_length=500, blank=True, null=True)
    Current_Academic_Advisor = models.CharField(max_length=500, blank=True, null=True)
    Current_Program_Year = models.IntegerField(blank=True, null=True)

    #############feedback############
    Feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('username', 'questionnaire_for')

    def __str__(self):
        return str(self.username) + " " + self.fullname + " " + str(
            self.questionnaire_for) + " " + str(self.status)


class course(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)

    FALL = 'Fall'
    SPRING = 'Spring'
    SUMMER = 'Summer'
    term_choices = (
        (FALL, FALL),
        (SPRING, SPRING),
        (SUMMER, SUMMER),
    )
    year_choices = []
    for y in range((datetime.datetime.now().year - 6), (datetime.datetime.now().year + 1)):
        year_choices.append((y, y))

    Subject_Year = models.IntegerField(choices=year_choices, blank=True, null=True)
    Subject_Term = models.CharField(max_length=6, choices=term_choices, blank=True)

    Subject_Name = models.CharField(max_length=200)
    Subject_Code = models.CharField(max_length=50)

    Grade = models.CharField(max_length=20)

    class Meta:
        unique_together = ('username', 'questionnaire_for', 'Subject_Name', 'Subject_Year', 'Subject_Term')

    def __str__(self):
        return str(self.username) + " " + str(self.questionnaire_for) + " " + \
               self.Subject_Name + " " + str(self.Subject_Year) + " " + self.Subject_Term

    def clean(self):
        if self.Subject_Name:
            if self.Subject_Year or self.Subject_Term:
                if not (self.Subject_Year and self.Subject_Term):
                    raise ValidationError("Both Subject Year and Term should be selected.")
            else:
                raise ValidationError("Please select Subject Year and Term.")


class examAttempt(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)
    Exam_Name = models.ForeignKey(qualifyingExam, db_column="exam_Name", on_delete=models.PROTECT)
    Attempt_Number = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)])
    Grade = models.CharField(max_length=10)

    class Meta:
        unique_together = ('username', 'questionnaire_for', 'Exam_Name', 'Attempt_Number',)

    def __str__(self):
        return str(self.username) + str(self.questionnaire_for) + " " + str(self.Exam_Name) + " " + str(
            self.Attempt_Number)


class techingAssistant(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)

    FALL = 'Fall'
    SPRING = 'Spring'
    SUMMER = 'Summer'
    term_choices = (
        (FALL, FALL),
        (SPRING, SPRING),
        (SUMMER, SUMMER),
    )
    year_choices = []
    for y in range((datetime.datetime.now().year - 6), (datetime.datetime.now().year + 1)):
        year_choices.append((y, y))

    Subject_Year = models.IntegerField(choices=year_choices, blank=True, null=True)
    Subject_Term = models.CharField(max_length=6, choices=term_choices, blank=True)
    Subject_Name = models.CharField(max_length=200)
    Subject_Code = models.CharField(max_length=50)
    Instructor_Name = models.CharField(max_length=200)
    Responsibilities = models.TextField(max_length=5000)
    Lecture_or_Presentation_Given = models.TextField(max_length=5000)
    Area_of_Improvement = models.TextField(max_length=5000)

    class Meta:
        unique_together = ('username', 'questionnaire_for', 'Subject_Name', 'Subject_Year', 'Subject_Term')

    def __str__(self):
        return str(self.username) + " " + str(self.questionnaire_for) + " " + self.Subject_Name + " " + \
               str(self.Subject_Year) + " " + self.Subject_Term

    def clean(self):
        if self.Subject_Name:
            if self.Subject_Year or self.Subject_Term:
                if not (self.Subject_Year and self.Subject_Term):
                    raise ValidationError("Both Subject Year and Term should be selected.")
            else:
                raise ValidationError("Please select Subject Year and Term.")


class paper(models.Model):
    IP = 'In Progress'
    UR = 'Under Revision'
    PU = 'Published'
    status_choices = (
        (IP, IP),
        (UR, UR),
        (PU, PU),
    )
    FALL = 'Fall'
    SPRING = 'Spring'
    SUMMER = 'Summer'
    term_choices = (
        (FALL, FALL),
        (SPRING, SPRING),
        (SUMMER, SUMMER),
    )
    year_choices = []
    for y in range((datetime.datetime.now().year - 6), (datetime.datetime.now().year + 1)):
        year_choices.append((y, y))

    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)
    Title = models.CharField(max_length=5000)
    Venue = models.CharField(max_length=5000)
    Status_of_Paper = models.CharField(max_length=15, choices=status_choices)
    Publish_Year = models.IntegerField(choices=year_choices, blank=True, null=True)
    Publish_Term = models.CharField(max_length=6, choices=term_choices, blank=True)

    Author = models.ForeignKey(studentName, db_column="name", on_delete=models.PROTECT, blank=True)
    List_of_Authors = models.CharField(max_length=5000)

    class Meta:
        unique_together = ('Author', 'questionnaire_for', 'Title',)

    def clean(self):
        if self.Status_of_Paper == 'Published':
            if self.Publish_Year or self.Publish_Term:
                if not (self.Publish_Year and self.Publish_Term):
                    raise ValidationError("Both Publish Year and Term should be selected for a 'Published' Paper.")
            else:
                raise ValidationError("Please select Publish Year and Term.")

    def __str__(self):
        return str(self.Author) + " " + str(self.questionnaire_for) + " " + self.Title


class research(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)
    exp = 'Expected'
    p = 'Passed'
    np = 'Not Passed'
    status_choices = (
        (exp, exp),
        (p, p),
        (np, np),
    )

    #   Research
    Topic = models.CharField(max_length=5000)
    Current_Research_Advisor = models.ForeignKey(professorName, related_name='research_advisor',
                                                 on_delete=models.PROTECT, blank=True, null=True)
    Proposal = models.DateField()
    Proposal_Status = models.CharField(max_length=10, choices=status_choices, default=exp)
    Defense = models.DateField()
    Defense_Status = models.CharField(max_length=10, choices=status_choices, default=exp)
    Thesis_Committee = models.TextField(max_length=5000,blank=True)

    #   Academics
    Current_Academic_Advisor = models.ForeignKey(professorName, related_name='academic_advisor',
                                                 on_delete=models.PROTECT, blank=True, null=True)

    Current_GPA = models.FloatField(validators=[MaxValueValidator(4),MinValueValidator(0)], null=True)

    class Meta:
        unique_together = ('username', 'questionnaire_for',)

    def __str__(self):
        return str(self.username) + " " + str(self.questionnaire_for) + " " + self.Topic
