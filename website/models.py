from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    gender = models.CharField(max_length=1, default='M',choices=GENDER_CHOICES)
    profileFilled  = models.IntegerField(default=0)
    bdate = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d',blank=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)

class dummyDoctor(models.Model):
    fullname = models.CharField(max_length=250)
    organization = models.CharField(max_length=250)
    specialization = models.CharField(max_length=250,default=None)
    insurance = models.CharField(max_length=250,default=None)
    rating = models.IntegerField(default=0)
    phoneNumber = models.IntegerField(default=1234567890)
    address = models.CharField(max_length=250,default=None)
    digit = models.CharField(max_length=250,default=None)

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    id_num = models.IntegerField(blank=False, null=False, primary_key=True,default=1)
    organization = models.CharField(max_length=250)
    specialization = models.CharField(max_length=250,default=None)
    insurance = models.CharField(max_length=250,default=None)
    rating = models.IntegerField(default=0)
    phoneNumber = models.IntegerField(default=1234567890)
    address = models.CharField(max_length=250,default=None)


    def __str__(self):
        return str(self.user.username)

class appointment(models.Model):
    patient = models.ForeignKey(Profile, on_delete=models.CASCADE,default=None)
    doc = models.ForeignKey(Doctor, on_delete=models.CASCADE,default=None)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(auto_now=False, auto_now_add=False,null=True, blank=True)
    status = models.CharField(max_length=250,default=None)
    #date = application_data.scheduled_at.date()
