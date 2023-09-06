from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Area(models.Model):
    area_name = models.CharField(max_length=254)
    area_bgcolor = models.CharField(max_length=10)
    area_textcolor = models.CharField(max_length=10)
    def __str__(self):
        return self.area_name

class Chore(models.Model):
    chore_name = models.CharField(max_length=254)
    area = models.ForeignKey(Area, null=True, on_delete=models.SET_NULL)
    chore_type = models.CharField(max_length=254)
    active = models.BooleanField(default=True)
    dueDate = models.DateField(auto_now_add=True)
    lastCompleted = models.DateField(auto_now_add=True)
    intervalNumber = models.IntegerField()
    unit = models.CharField(max_length=1)
    mon = models.BooleanField(default=False)
    tue = models.BooleanField(default=False)
    wed = models.BooleanField(default=False)
    thu = models.BooleanField(default=False)
    fri = models.BooleanField(default=False)
    sat = models.BooleanField(default=False)
    sun = models.BooleanField(default=False)
    m_jan = models.BooleanField(default=False)
    m_feb = models.BooleanField(default=False)
    m_mar = models.BooleanField(default=False)
    m_apr = models.BooleanField(default=False)
    m_may = models.BooleanField(default=False)
    m_jun = models.BooleanField(default=False)
    m_jul = models.BooleanField(default=False)
    m_aug = models.BooleanField(default=False)
    m_sep = models.BooleanField(default=False)
    m_oct = models.BooleanField(default=False)
    m_nov = models.BooleanField(default=False)
    m_dec = models.BooleanField(default=False)
    assignee = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    effort = models.IntegerField()
    seasonal = models.BooleanField(default=False)
    vacationMode = models.BooleanField(default=False)
    vacationPause = models.IntegerField()
    vSeasonal = models.BooleanField(default=False)
    def __str__(self):
        return self.chore_name

class HistoryItem(models.Model):
    completed_date = models.DateField()
    completed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)

class Option(models.Model):
    vacation_mode = models.BooleanField(default=False)