from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class studentName(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    name = models.CharField(max_length= 500, blank=True)

    def __str__(self):
        return self.name

class professorName(models.Model):
    username = models.ForeignKey(User, db_column="username", on_delete=models.PROTECT)
    name = models.CharField(max_length= 500, blank=True)

    def __str__(self):
        return self.name


class professorWhiteList(models.Model):
    email = models.EmailField(max_length=200, unique=True)

    def __str__(self):
        return self.email

class announcement(models.Model):
    announcement = models.CharField(max_length=1000)

    def __str__(self):
        return self.announcement

class userInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    #please do not make any changes to studentOrProfessor field in future
    studentOrProfessor = models.CharField(blank=True, max_length=50, default="default")

    def __str__(self):
        return self.user.username + " " + self.studentOrProfessor

class studentProfile(models.Model):
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    email = models.EmailField(unique=True)
    SUNY_ID = models.IntegerField(blank=True, null=True)
    native_country = models.CharField(max_length=100, blank=True)
    program_joining_date = models.DateField(blank=True, null=True)


    def __str__(self):
        return self.email + " " + self.first_name + " " + self.last_name