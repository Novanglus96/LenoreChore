"""
Module: tasks.py
Description: Contains task definitions to be scheduuled.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from api.models import Chore, CustomUser
from datetime import date, datetime
from django.utils import timezone
from backend.push import send_web_push


def build_rollup_payload(due_today, overdue, assigned):
    """
    Build the notification payload for a daily reminder.

    Args:
        due_today (int): Household chores due today.
        overdue (int): Household chores overdue.
        assigned (int): Chores due today assigned to the recipient.

    Returns:
        (dict): The notification payload (title, body, url).
    """
    chore_word = "chore" if due_today == 1 else "chores"
    body = f"{due_today} {chore_word} due today, {overdue} overdue"
    if assigned:
        body += f" — {assigned} assigned to you"
    return {"title": "LenoreChore reminders", "body": body, "url": "/list"}


def send_due_notifications():
    """
    The function `send_due_notifications` sends a daily household rollup of
    due/overdue chores to each opted-in user once per day, at or after their
    chosen local time. Designed to run frequently (e.g. every 5 minutes).

    Each eligible user is marked notified for the day regardless of whether a
    message was sent, so the rollup fires once per day rather than repeatedly.

    Returns:
        (str): A short summary of how many users were notified.
    """
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    due_today = Chore.objects.filter(status=0, nextDue__lte=today).count()
    overdue = Chore.objects.filter(status=0, nextDue__lt=today).count()

    users = CustomUser.objects.filter(
        notify_enabled=True, notify_time__lte=current_time
    ).exclude(last_notified_date=today)

    notified = 0
    for user in users:
        if due_today > 0:
            assigned = Chore.objects.filter(
                status=0, nextDue__lte=today, assignee=user
            ).count()
            payload = build_rollup_payload(due_today, overdue, assigned)
            for subscription in user.push_subscriptions.all():
                send_web_push(subscription, payload)
            notified += 1
        user.last_notified_date = today
        user.save(update_fields=["last_notified_date"])

    return f"Notified {notified} user(s)"


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
