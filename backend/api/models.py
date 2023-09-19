from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from datetime import date

from .managers import CustomUserManager

import os

def user_profile_picture_upload(instance, filename):
    _, file_extension = os.path.splitext(filename)
    
    return f"profile_pictures/{instance.email}{file_extension}"

# Create your models here.

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_upload, blank=True, null=True)
    male = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Area(models.Model):
    area_name = models.CharField(max_length=254)
    area_icon = models.CharField(max_length=254)
    def __str__(self):
        return self.area_name

class Chore(models.Model):
    chore_name = models.CharField(max_length=254)
    area = models.ForeignKey(Area, null=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=True)
    nextDue = models.DateField(auto_now_add=True)
    lastCompleted = models.DateField(auto_now_add=True)
    intervalNumber = models.IntegerField(default=1)
    unit = models.CharField(max_length=1, default='d')
    m_jan = models.BooleanField(default=True)
    m_feb = models.BooleanField(default=True)
    m_mar = models.BooleanField(default=True)
    m_apr = models.BooleanField(default=True)
    m_may = models.BooleanField(default=True)
    m_jun = models.BooleanField(default=True)
    m_jul = models.BooleanField(default=True)
    m_aug = models.BooleanField(default=True)
    m_sep = models.BooleanField(default=True)
    m_oct = models.BooleanField(default=True)
    m_nov = models.BooleanField(default=True)
    m_dec = models.BooleanField(default=True)
    assignee = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    effort = models.IntegerField(default=0)
    vacationPause = models.IntegerField(default=0)
    def __str__(self):
        return self.chore_name

class HistoryItem(models.Model):
    completed_date = models.DateField()
    completed_by = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)

class Option(models.Model):
    vacation_mode = models.BooleanField(default=False)
    def __str__(self):
        return 'Options'