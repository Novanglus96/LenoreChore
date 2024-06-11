from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from datetime import date
from django.utils import dateformat
from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from .managers import CustomUserManager

import os


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError("There is already one instance of this model")
        return super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("You cannot delete this object")


def user_profile_picture_upload(instance, filename):
    _, file_extension = os.path.splitext(filename)

    return f"profile_pictures/{instance.email}{file_extension}"


# Create your models here.


class CustomUser(AbstractUser):
    COLOR_PALETTE = [
        ("#E91E63", "Color1"),
        ("#3F51B5", "Color2"),
        ("#009688", "Color3"),
        ("#CDDC39", "Color4"),
    ]
    username = None
    email = models.EmailField("email address", unique=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_upload, blank=True, null=True
    )
    male = models.BooleanField(default=True)
    user_color = ColorField(default="#E91E63", samples=COLOR_PALETTE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def fullname(self):
        fullname = self.first_name + " " + self.last_name
        return fullname


class AreaGroup(models.Model):
    group_name = models.CharField(max_length=254)
    group_order = models.IntegerField(default=1)
    group_color = models.CharField(max_length=12)

    def __str__(self):
        return self.group_name


class Area(models.Model):
    area_name = models.CharField(max_length=254)
    area_icon = models.CharField(max_length=254)
    group = models.ForeignKey(
        AreaGroup, null=True, on_delete=models.SET_DEFAULT, default=1
    )
    area_order = models.IntegerField(default=1)

    def __str__(self):
        return self.area_name

    @property
    def dirtiness(self):
        total_dirtiness = self.total_dirtiness()
        total_chores = self.chore_set.filter(active=True).count()

        if total_chores > 0:
            # Calculate the percentage if there are chores
            percentage = total_dirtiness / total_chores
            perecentage = round(percentage)
        else:
            # Handle the case when there are no chores
            percentage = 0

        return percentage

    @property
    def dueCount(self):
        today = date.today().isoformat()
        count = self.chore_set.filter(active=True, nextDue__lte=today).count()
        return count

    @property
    def totalCount(self):
        count = self.chore_set.filter(active=True).count()
        return count

    def total_dirtiness(self):
        total = sum(
            chore.dirtiness for chore in self.chore_set.filter(active=True)
        )
        return total


class Month(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Chore(models.Model):
    chore_name = models.CharField(max_length=254)
    area = models.ForeignKey(Area, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    nextDue = models.DateField(default=date.today)
    lastCompleted = models.DateField(default=date.today)
    intervalNumber = models.IntegerField(default=1)
    unit = models.CharField(max_length=10, default="day(s)")
    active_months = models.ManyToManyField(Month)
    assignee = models.ForeignKey(
        CustomUser, null=True, on_delete=models.SET_NULL
    )
    effort = models.IntegerField(default=0)
    vacationPause = models.IntegerField(default=0)
    expand = models.BooleanField(default=False)

    def __str__(self):
        return self.chore_name

    @property
    def dirtiness(self):
        timesincedone = self.lastCompleted - date.today()
        timeperiod = self.lastCompleted - self.nextDue
        if timeperiod.days == 0:
            dirtiness = 0
        else:
            dirtiness = round((timesincedone.days / timeperiod.days) * 100)
            if dirtiness > 100:
                dirtiness = 100
        return dirtiness

    @property
    def duedays(self):
        delta = self.nextDue - date.today()
        return delta.days


class HistoryItem(models.Model):
    completed_date = models.DateField(default=date.today)
    completed_by = models.ForeignKey(
        CustomUser, null=True, on_delete=models.SET_NULL
    )
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)


class Option(SingletonModel):
    vacation_mode = models.BooleanField(default=False)
    med_thresh = models.IntegerField(default=50)
    high_thresh = models.IntegerField(default=50)

    def __str__(self):
        return "Options"

    @classmethod
    def load(cls):
        return cls.objects.first()
