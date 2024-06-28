"""
Module: tasks.py
Description: Contains task definitions to be scheduuled.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from django_q.tasks import async_task, result, schedule
import arrow
from api.models import Chore
from django_q.models import Schedule
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
import csv
from io import StringIO
from django.db import IntegrityError, connection, transaction
from django.db.models import F, Window
from django.db.models.functions import RowNumber
from decimal import Decimal


def process_seasonal():
    """
    The function `process_seasonal` enables or disables chores when out or in
    season.

    """
    current_month = datetime.now().strftime("%b")
    active_chores = Chore.objects.filter(status=0).exclude(
        active_months__name=current_month
    )
    inactive_chores = Chore.objects.filter(
        status=2, active_months__name=current_month
    )
    for chore in active_chores:
        chore.status = 2
        chore.save()
    for chore in inactive_chores:
        chore.status = 0
        chore.nextDue = date.today()
        chore.save()
    return "Complete"
