"""
Module: tasks.py
Description: Contains task definitions to be scheduuled.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from api.models import Chore
from datetime import date, datetime


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
