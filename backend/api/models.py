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
    """
    Model representing a singleton model.

    Attributes:
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Override save method to validate only one instance exists.
        """
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError("There is already one instance of this model")
        return super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override delete method to block deletes.
        """
        raise ValidationError("You cannot delete this object")


def user_profile_picture_upload(instance, filename):
    _, file_extension = os.path.splitext(filename)

    return f"profile_pictures/{instance.email}{file_extension}"


# Create your models here.


class CustomUser(AbstractUser):
    """
    Custom user object using AbstractUser.

    Attributes:
        username (): The username of the user.
        email (EmailField): The email of the user. Unique.
        profile_picture (ImageField): An image to use as the user profile
            picture.
        male (BooleanField): True if the user is male.
        user_color (ColorField): A color used to represent the user.
    """

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
        """
        Returns:
            (String): The user's email address.
        """
        return self.email

    @property
    def fullname(self):
        fullname = self.first_name + " " + self.last_name
        return fullname


class AreaGroup(models.Model):
    """
    Model representing an area group.

    Attributes:
        group_name (CharField): The name of the group. Max=254.
        group_order (IntegerField): The order index of the group. Default=1.
        group_color (CharField): A hex value of a color to represent the group. Max=12.
    """

    group_name = models.CharField(max_length=254)
    group_order = models.IntegerField(default=1)
    group_color = models.CharField(max_length=12)

    def __str__(self):
        """
        Returns:
            (String): The area group name.
        """
        return self.group_name


class Area(models.Model):
    """
    Model representing an area.

    Attributes:
        area_name (CharField): The name of a store. Max=254
        area_icon (CharField): The name of an icon to use. Max=254
        group (AreaGroup): An area group object.
        area_order (IntegerField): The order index of the area.
    """

    area_name = models.CharField(max_length=254)
    area_icon = models.CharField(max_length=254)
    group = models.ForeignKey(
        AreaGroup, null=True, on_delete=models.SET_DEFAULT, default=1
    )
    area_order = models.IntegerField(default=1)

    def __str__(self):
        """
        Returns:
            (String): The Area Object name.
        """
        return self.area_name

    @property
    def dirtiness(self):
        """
        Calculates the dirtiness percentage of an area.

        Returns:
            percentage (integer): The dirtiness of an area as a percentage.
        """
        total_dirtiness = self.total_dirtiness()
        total_chores = self.chore_set.filter(status=0).count()

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
        """
        Determines the number of chores due for this area.

        Returns:
            count (integer): The count of chores due for this area.
        """
        today = date.today().isoformat()
        count = self.chore_set.filter(status=0, nextDue__lte=today).count()
        return count

    @property
    def totalCount(self):
        """
        Calculates the total chores in this area.

        Returns:
            count (integer): The total count of chores for this area.
        """
        count = self.chore_set.filter(status=0).count()
        return count

    def total_dirtiness(self):
        """
        Returns:
            total (integer): The total dirtiness of an area.
        """
        total = sum(
            chore.dirtiness for chore in self.chore_set.filter(status=0)
        )
        return total


class Month(models.Model):
    """
    Model representing a month.

    Attributes:
        name (CharField): The name of the month. Max=20
    """

    name = models.CharField(max_length=20)

    def __str__(self):
        """
        Returns:
            (String): The Month Object name.
        """
        return self.name


class Chore(models.Model):
    """
    Model representing a month.

    Attributes:
        chore_name (CharField): The name of the chore. Max=254
        area (Area): An area object.
        nextDue (DateField): The date chore is next due. Default=Today
        lastCompleted (DateField): The date chore was last completed. Default=Today.
        intervalNumber (integer): The repeat interval. Default=1.
        unit (CharField): The unit of the repeat intervals. Default="day(s)".
        active_months (Month): An array of Months chore is active.
        assignee (CustomUser): A CustomUser object assigned to chore. Default=None.
        effort (IntegerField): How difficult the task is. Default=0.
        vacationPause (IntegerField): Default=0.
        expand (BooleanField): Default=False.
        status (IntegerField): The status of the chore. Default=0.
    """

    chore_name = models.CharField(max_length=254)
    area = models.ForeignKey(Area, null=True, on_delete=models.CASCADE)
    nextDue = models.DateField(default=date.today)
    lastCompleted = models.DateField(default=date.today)
    intervalNumber = models.IntegerField(default=1)
    unit = models.CharField(max_length=10, default="day(s)")
    active_months = models.ManyToManyField(Month)
    assignee = models.ForeignKey(
        CustomUser,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        default=None,
    )
    effort = models.IntegerField(default=0)
    vacationPause = models.IntegerField(default=0)
    expand = models.BooleanField(default=False)
    status = models.IntegerField(default=0)

    def __str__(self):
        """
        Returns:
            (String): The Chore Object name.
        """
        return self.chore_name

    @property
    def dirtiness(self):
        """
        Calculates how dirty the chore is.

        Returns:
            dirtiness (integer): The dirtiness of the chore.
        """
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
        """
        Calculates the days until chore is due.

        Returns:
            (integer): The days until chore is due.
        """
        delta = self.nextDue - date.today()
        return delta.days


class HistoryItem(models.Model):
    """
    Model representing a history item for a chore.

    Attributes:
        completed_date (DateField): The date a chore was completed. Default=Today.
        completed_by (CustomUser): The user object who completed the chore.
        chore (Chore): The chore object.
    """

    completed_date = models.DateField(default=date.today)
    completed_by = models.ForeignKey(
        CustomUser, null=True, on_delete=models.SET_NULL
    )
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)


class Option(SingletonModel):
    """
    Model representing an option.

    Attributes:
        vacation_mode (BooleanField): Is vacation mode active or not. Default=False.
        med_thresh (IntegerField): The medium threshold for dirtiness. Default=50.
        high_thresh (IntegerField): The high threshold for dirtiness. Default=50.
    """

    vacation_mode = models.BooleanField(default=False)
    med_thresh = models.IntegerField(default=50)
    high_thresh = models.IntegerField(default=50)

    def __str__(self):
        """
        Returns:
            (String): The option object.
        """
        return "Options"

    @classmethod
    def load(cls):
        return cls.objects.first()


class Version(SingletonModel):
    """
    Model representing app version.

    Fields:
    - version_number (CharField): The current version of the app.
    """

    version_number = models.CharField(max_length=10)

    def __str__(self):
        """
        Returns:
            (String): The app version number.
        """
        return self.version_number
