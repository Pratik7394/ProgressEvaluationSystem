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
    Current_Research_Advisor = models.CharField(max_length=500, blank=True)
    Current_Academic_Advisor = models.CharField(max_length=500, blank=True)
    Current_Program_Year = models.IntegerField(blank=True, null=True)

    #############feedback############
    Feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('username', 'questionnaire_for',)

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
        unique_together = ('username', 'questionnaire_for', 'Subject_Name', 'In_Which_Semester',)

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

    Author = models.ForeignKey(User, db_column="name", on_delete=models.PROTECT)
    Coauthor = models.CharField(max_length=1000, blank=True)

    class Meta:
        unique_together = ('Author', 'questionnaire_for', 'Title',)

    def __str__(self):
        return str(self.Author) + " " + str(self.questionnaire_for) + " " + self.Title


class research(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    questionnaire_for = models.ForeignKey(questionnaire, db_column="questionnaire_for", on_delete=models.PROTECT)
    Topic = models.CharField(max_length=5000, blank=True)
    Proposal = models.CharField(max_length=5000, blank=True)
    Defense = models.CharField(max_length=5000, blank=True)
    Current_Academic_Advisor = models.ForeignKey(professorName, related_name='academic_advisor',
                                                 on_delete=models.PROTECT, blank=True, null=True)
    Current_Research_Advisor = models.ForeignKey(professorName, related_name='research_advisor',
                                                 on_delete=models.PROTECT,
                                                 blank=True, null=True)
    # Current_Program_Year = models.IntegerField(default="1", validators=[MinValueValidator(1)])
    Current_GPA = models.FloatField(validators=[MaxValueValidator(4)],blank=True, null=True)

    class Meta:
        unique_together = ('username', 'questionnaire_for',)

    def __str__(self):
        return str(self.username) + " " + str(self.questionnaire_for) + " " + self.Topic

# from django.db import models
# from django.contrib.auth.models import User
# from django.core.validators import MinValueValidator, MaxValueValidator
# import datetime

# from django.db import models
# from django.contrib.auth.models import User
# from django.core.validators import MinValueValidator, MaxValueValidator
#
# class questionnaire(models.Model):
#     Questionnaire_For = models.CharField(max_length=20, unique=True)
#
#     def __str__(self):
#         return self.Questionnaire_For
#
#
# class qualifyingExam(models.Model):
#     exam_Name = models.CharField(max_length=200, unique=True)
#
#     def __str__(self):
#         return self.exam_Name
#
#
# class submissionTrack(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     Questionnaire_For = models.ForeignKey(questionnaire, db_column="Questionnaire_For", on_delete=models.PROTECT)
#     SAVE = 'Save'
#     SUBMIT = 'Submit'
#     choices = (
#         (SAVE, 'Save'),
#         (SUBMIT, 'Submit'),
#     )
#     saveSubmit = models.CharField(max_length=6, choices=choices)
#
#     class Meta:
#         unique_together = ('username', 'Questionnaire_For', 'saveSubmit',)
#
#     def ___str___(self):
#         return str(self.username) + " " + str(self.Questionnaire_For) + " " + self.saveSubmit
#
#
# class coursesTaken(models.Model):
#     # print("in coursesTaken")
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     Questionnaire_For = models.ForeignKey(questionnaire, db_column="Questionnaire_For", on_delete=models.PROTECT)
#     Subject_Name = models.CharField(max_length=200)
#     Subject_Code = models.CharField(max_length=50)
#     Subject_Term_and_Year = models.CharField(max_length=50)
#     Grade = models.CharField(max_length=20)
#
#     class Meta:
#         unique_together = ('username', 'Questionnaire_For', 'Subject_Name', 'Subject_Term_and_Year',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(
#             self.Questionnaire_For) + " " + self.Subject_Name + " " + self.Subject_Term_and_Year
#
#
# class examAttempts(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     Questionnaire_For = models.ForeignKey(questionnaire, db_column="Questionnaire_For", on_delete=models.PROTECT)
#     Exam_Name = models.ForeignKey(qualifyingExam, db_column="exam_Name",
#                                   on_delete=models.PROTECT)
#     Attempt_Number = models.IntegerField(default="1", validators=[MaxValueValidator(10), MinValueValidator(1)])
#     Grade = models.CharField(max_length=10)
#
#     class Meta:
#         unique_together = ('username', 'Questionnaire_For', 'Exam_Name', 'Attempt_Number',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.Questionnaire_For) + " " + str(self.Exam_Name) + " " + str(
#             self.Attempt_Number)
#
#
# class techingAssistant(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     Questionnaire_For = models.ForeignKey(questionnaire, db_column="Questionnaire_For", on_delete=models.PROTECT)
#     Subject_Name = models.CharField(max_length=200)
#     Subject_Code = models.CharField(max_length=50)
#     In_Which_Semester = models.CharField(max_length=50)
#     Instructor_Name = models.CharField(max_length=200)
#     Responsibilities = models.TextField(max_length=5000)
#     Lecture_or_Presentation_Given = models.TextField(max_length=5000)
#     Area_of_Improvement = models.TextField(max_length=5000)
#
#     class Meta:
#         unique_together = ('username', 'Questionnaire_For', 'Subject_Name',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.Questionnaire_For) + " " + self.Subject_Name
#
#
# class paper(models.Model):
#     Questionnaire_For = models.ForeignKey(questionnaire, db_column="Questionnaire_For", on_delete=models.PROTECT)
#     Title = models.CharField(max_length=5000)
#     Venue = models.CharField(max_length=1000)
#     IP = 'In Progress'
#     UR = 'Under Revision'
#     PU = 'Published'
#     status_choices = (
#         (IP, IP),
#         (UR, UR),
#         (PU, PU),
#     )
#     Status_of_Paper = models.CharField(max_length=15, choices=status_choices, default=IP)
#     Author = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     Coauthor = models.TextField(max_length=5000)
#
#     class Meta:
#         unique_together = ('Author', 'Questionnaire_For', 'Title',)
#
#     def __str__(self):
#         return str(self.Author) + " " + str(self.Questionnaire_For) + " " + self.Title
#
#
# class research(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     Questionnaire_For = models.ForeignKey(questionnaire, db_column="Questionnaire_For", on_delete=models.PROTECT)
#     Topic = models.CharField(max_length=5000, blank=True, null=True)
#     Proposal = models.CharField(max_length=5000, blank=True, null=True)
#     Defense = models.CharField(max_length=5000, blank=True, null=True)
#     Current_Academic_Advisor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='academic_advisor')
#     Current_Research_Advisor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='research_advisor')
#
#     class Meta:
#         unique_together = ('username', 'Questionnaire_For',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.Questionnaire_For)

################## 2nd ###########

# class term(models.Model):
#     # print("in term")
#     FALL = 'Fall'
#     SPRING = 'Spring'
#     SUMMER = 'Summer'
#     WINTER = 'Winter'
#     term_choices = (
#         (FALL, FALL),
#         (SPRING, SPRING),
#         (SUMMER, SUMMER),
#         (WINTER, WINTER),
#     )
#     semester = models.CharField(max_length=6, choices=term_choices)
#
#     year_choices = []
#     for y in range((datetime.datetime.now().year - 4), (datetime.datetime.now().year + 2)):
#         year_choices.append((y, y))
#     year = models.IntegerField(choices=year_choices, default=datetime.datetime.now().year)
#
#     class Meta:
#         unique_together = ('semester', 'year',)
#
#     def ___str___(self):
#         return self.semester + " " + str(self.year)
#
#
# class qualifyingExam(models.Model):
#     exam_Name = models.CharField(max_length=200, unique=True)
#
#     def ___str___(self):
#         return self.exam_Name
#
#
# class submissionTrack(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     term = models.ForeignKey(term, on_delete=models.PROTECT)
#     print("in submission")
#     SAVE = 'Save'
#     SUBMIT = 'Submit'
#     choices = (
#         (SAVE, 'Save'),
#         (SUBMIT, 'Submit'),
#     )
#     saveSubmit = models.CharField(max_length=6, choices=choices)
#
#     class Meta:
#         unique_together = ('username', 'term', 'saveSubmit',)
#
#     def ___str___(self):
#         return str(self.username) + " " + str(self.term) + " " + self.saveSubmit
#
#
# class coursesTaken(models.Model):
#     print("in coursesTaken")
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     term = models.ForeignKey(term, on_delete=models.PROTECT)
#     Subject_Name = models.CharField(max_length=200)
#     Subject_Code = models.CharField(max_length=50)
#     Subject_Term_and_Year = models.CharField(max_length=50)
#     Grade = models.CharField(max_length=20)
#
#     class Meta:
#         unique_together = ('username', 'term', 'Subject_Name', 'Subject_Term_and_Year',)
#
#     def __str__(self):
#         return self.Subject_Code + " " + self.Subject_Term_and_Year
#
#
# class examAttempts(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     term = models.ForeignKey(term, on_delete=models.PROTECT)
#     Exam_Name = models.ForeignKey(qualifyingExam, db_column="exam_Name",
#                                   on_delete=models.PROTECT)
#     Attempt_Number = models.IntegerField(default="1", validators=[MaxValueValidator(4), MinValueValidator(1)])
#     Grade = models.CharField(max_length=10)
#
#     class Meta:
#         unique_together = ('username', 'Exam_Name', 'Attempt_Number',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.Exam_Name) + " " + str(self.Attempt_Number)
#
#
# class techingAssistant(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     term = models.ForeignKey(term, on_delete=models.PROTECT)
#     Subject_Name = models.CharField(max_length=200)
#     Subject_Code = models.CharField(max_length=50)
#     In_Which_Semester = models.CharField(max_length=50)
#     Instructor_Name = models.CharField(max_length=200)
#     Responsibilities = models.TextField(max_length=5000)
#     Lecture_or_Presentation_Given = models.TextField(max_length=5000)
#     Area_of_Improvement = models.TextField(max_length=5000)
#
#     class Meta:
#         unique_together = ('username', 'term', 'Subject_Name',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.Subject_Code) + " " + str(self.In_Which_Semester)
#
#
# class paper(models.Model):
#     term = models.ForeignKey(term, on_delete=models.PROTECT)
#     Title = models.CharField(max_length=5000)
#     Venue = models.CharField(max_length=1000)
#     IP = 'In Progress'
#     UR = 'Under Revision'
#     PU = 'Published'
#     status_choices = (
#         (IP, IP),
#         (UR, UR),
#         (PU, PU),
#     )
#     Status_of_Paper = models.CharField(max_length=15, choices=status_choices, default=IP)
#     Author = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     Coauthor = models.TextField(max_length=5000)
#
#     class Meta:
#         unique_together = ('Author', 'term', 'Title',)
#
#     def __str__(self):
#         return str(self.Author) + " " + str(self.term) + " " + self.Title
#
#
# class research(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     term = models.ForeignKey(term, on_delete=models.PROTECT)
#     Topic = models.CharField(max_length=5000, blank=True, null=True)
#     Proposal = models.CharField(max_length=5000, blank=True, null=True)
#     Defense = models.CharField(max_length=5000, blank=True, null=True)
#     Current_Academic_Advisor = models.CharField(max_length=5000, blank=True, null=True)
#     Current_Research_Advisor = models.CharField(max_length=5000, blank=True, null=True)
#
#     class Meta:
#         unique_together = ('username', 'term',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.term) + " " + self.Topic
#
# class submission(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     term = models.ForeignKey(term, on_delete=models.PROTECT)
#     print("in submission new")
#     SAVE = 'Save'
#     SUBMIT = 'Submit'
#     choices = (
#         (SAVE, 'Save'),
#         (SUBMIT, 'Submit'),
#     )
#     saveSubmit = models.CharField(max_length=6, choices=choices)
#
#     class Meta:
#         unique_together = ('username', 'term', 'saveSubmit',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.term) + " " + self.saveSubmit


############## 1st #############
# class semester(models.Model):
#     print("in term semester")
#     FALL = 'Fall'
#     SPRING = 'Spring'
#     SUMMER = 'Summer'
#     WINTER = 'Winter'
#     term_choices = (
#         (FALL, 'Fall'),
#         (SPRING, 'Spring'),
#         (SUMMER, 'Summer'),
#         (WINTER, 'Winter'),
#     )
#     Semester = models.CharField(max_length=6, choices=term_choices, unique=True)

#     def _str_(self):
#         return self.Semester


# class year(models.Model):
#     print("in term year")
#     year_choices = []
#     for y in range((datetime.datetime.now().year - 4), (datetime.datetime.now().year + 2)):
#         year_choices.append((y, y))
#     year = models.IntegerField(choices=year_choices, default=datetime.datetime.now().year, unique=True)

#     def _str_(self):
#         return str(self.year)


# class advisor(models.Model):
#     print("in advisor")
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     term = models.ForeignKey(term, on_delete=models.PROTECT)
#     Current_Academic_Advisor = models.CharField(max_length=200)
#     Current_Research_Advisor = models.CharField(max_length=200)
#     Number_of_completed_semesters = models.IntegerField(default=0)

#     class Meta:
#         unique_together = ('username', 'term',)

#     def _str_(self):
#         return str(self.username) + " " + str(self.term)


# from django.db import models
# from django.contrib.auth.models import User
# import datetime
#
#
# class semester(models.Model):
#     # print("in term semester")
#     FALL = 'Fall'
#     SPRING = 'Spring'
#     SUMMER = 'Summer'
#     WINTER = 'Winter'
#     term_choices = (
#         (FALL, 'Fall'),
#         (SPRING, 'Spring'),
#         (SUMMER, 'Summer'),
#         (WINTER, 'Winter'),
#     )
#     Semester = models.CharField(max_length=6, choices=term_choices, unique=True)
#
#     def __str__(self):
#         return self.Semester
#
# class year(models.Model):
#     # print("in term year")
#     year_choices = []
#     for y in range(2015, (datetime.datetime.now().year + 1)):
#         year_choices.append((y, y))
#     Year = models.IntegerField(choices=year_choices, default=datetime.datetime.now().year, unique=True)
#
#     def __str__(self):
#         return str(self.Year)
#
#
# class submissionTrack(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     semester = models.ForeignKey(semester, db_column='Semester', related_name='semester_submission_Semester',
#                                  on_delete=models.PROTECT)
#     year = models.ForeignKey(year, db_column='Year', related_name='year_submission_Year',
#                              on_delete=models.PROTECT)
#     # print("in submission")
#     SAVE = 'Save'
#     SUBMIT = 'Submit'
#     choices = (
#         (SAVE, 'Save'),
#         (SUBMIT, 'Submit'),
#     )
#     saveSubmit = models.CharField(max_length=6, choices=choices)
#
#     class Meta:
#         unique_together = ('username', 'semester', 'year', 'saveSubmit',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.semester) + " " + str(self.year) + " " + self.saveSubmit
#
# class advisor(models.Model):
#     # print("in advisor")
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     semester = models.ForeignKey(semester, db_column='Semester', related_name='semester_advisor_Semester',
#                                  on_delete=models.PROTECT)
#     year = models.ForeignKey(year, db_column='Year', related_name='year_advisor_Year', on_delete=models.PROTECT)
#     Current_Academic_Advisor = models.CharField(max_length=200)
#     Current_Research_Advisor = models.CharField(max_length=200)
#     Number_of_completed_semesters = models.IntegerField(default=0)
#
#     class Meta:
#         unique_together = ('username', 'semester', 'year',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.semester) + " " + str(self.year)
#
#
# class coursesTaken(models.Model):
#     print("in coursesTaken")
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     semester = models.ForeignKey(semester, db_column='Semester', related_name='semester_coursesTaken_Semester',
#                                  on_delete=models.PROTECT)
#     year = models.ForeignKey(year, db_column='Year', related_name='year_coursesTaken_Year',
#                              on_delete=models.PROTECT)
#     Subject_Name = models.CharField(max_length=200)
#     Subject_Code = models.CharField(max_length=50)
#     Subject_Term_and_Year = models.CharField(max_length=50)
#     Grade = models.CharField(max_length=20)
#
#     class Meta:
#         unique_together = ('username', 'semester', 'year', 'Subject_Name', 'Subject_Term_and_Year',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.semester) + " " + str(
#             self.year) + " " + self.Subject_Name + " " + self.Subject_Term_and_Year
#
#
# class qualifyingExam(models.Model):
#     examName = models.CharField(max_length=200, unique=True)
#
#     def __str__(self):
#         return self.examName
#
#
# class examAttempts(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     semester = models.ForeignKey(semester, db_column='Semester', related_name='semester_examAttempts_Semester',
#                                  on_delete=models.PROTECT)
#     year = models.ForeignKey(year, db_column='Year', related_name='year_examAttempts_Year',
#                              on_delete=models.PROTECT)
#     Exam_Name = models.ForeignKey(qualifyingExam, db_column="examName",
#                                   related_name='qualifyingExam_examAttempts_examName',
#                                   on_delete=models.PROTECT)
#     Attempt_Number = models.IntegerField(default="1")
#     Grade = models.CharField(max_length=10)
#
#     class Meta:
#         unique_together = ('username', 'semester', 'year', 'Exam_Name', 'Attempt_Number',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.semester) + " " + str(
#             self.year) + " " + str(self.Exam_Name)
#
# class techingAssistant(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     semester = models.ForeignKey(semester, db_column='Semester', related_name='semester_teachingAssistant_Semester',
#                                  on_delete=models.PROTECT)
#     year = models.ForeignKey(year, db_column='Year', related_name='year_teachingAssistant_Year',
#                              on_delete=models.PROTECT)
#     Subject_Name = models.CharField(max_length=200)
#     Subject_Code = models.CharField(max_length=50)
#     In_Which_Semester = models.CharField(max_length=50)
#     Instructor_Name = models.CharField(max_length=200)
#     Responsibilities = models.TextField(max_length=5000)
#     Lecture_or_Presentation_Given = models.TextField(max_length=5000)
#     Area_of_Improvement = models.TextField(max_length=5000)
#
#     class Meta:
#         unique_together = ('username', 'semester', 'year', 'Subject_Name',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.semester) + " " + str(
#             self.year) + " " + self.Subject_Name + " " + self.In_Which_Semester
#
# class paper(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     semester = models.ForeignKey(semester, db_column='Semester', related_name='semester_paper_Semester',
#                                  on_delete=models.PROTECT)
#     year = models.ForeignKey(year, db_column='Year', related_name='year_paper_Year',
#                              on_delete=models.PROTECT)
#     Title = models.CharField(max_length=5000)
#     Venue = models.CharField(max_length=1000)
#     Status_of_Paper = models.CharField(max_length=500)
#     # Author_First_Name = models.ForeignKey(User, db_column=User.first_name, related_name='User_paper_first_name',
#     #                                       on_delete=models.PROTECT)
#     # Author_Last_Name = models.ForeignKey(User, db_column=User.last_name, related_name='User_paper_last_name',
#     #                                      on_delete=models.PROTECT)
#     Author = models.CharField(max_length=2000)
#     Coauthor = models.TextField(max_length=5000)
#
#     class Meta:
#         unique_together = ('username', 'semester', 'year', 'Title',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.semester) + " " + str(
#             self.year) + " " + self.Title
#
#
# class thesis(models.Model):
#     username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
#     semester = models.ForeignKey(semester, db_column='Semester', related_name='semester_thesis_Semester',
#                                  on_delete=models.PROTECT)
#     year = models.ForeignKey(year, db_column='Year', related_name='year_thesis_Year',
#                              on_delete=models.PROTECT)
#     Topic = models.CharField(max_length=5000, blank=True, null=True)
#     Proposal = models.CharField(max_length=5000, blank=True, null=True)
#     Defense = models.CharField(max_length=5000, blank=True, null=True)
#
#     class Meta:
#         unique_together = ('username', 'semester', 'year',)
#
#     def __str__(self):
#         return str(self.username) + " " + str(self.semester) + " " + str(
#             self.year) + " " + self.Topic
