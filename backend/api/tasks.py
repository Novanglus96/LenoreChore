"""
Module: tasks.py
Description: Contains task definitions to be scheduuled.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from api.models import Chore, CustomUser, Option
from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.conf import settings
from django.utils import timezone
from backend.push import send_web_push


def _user_timezone(user):
    """
    Resolve a user's notification timezone, falling back to the server's
    configured timezone when unset or invalid.

    Args:
        user (CustomUser): The user whose timezone to resolve.

    Returns:
        (ZoneInfo): The timezone to evaluate the user's notify_time in.
    """
    name = user.notify_timezone or settings.TIME_ZONE
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo(settings.TIME_ZONE)


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

    Each user's notify_time is interpreted in their own timezone
    (notify_timezone, falling back to the server timezone), so reminders fire
    at the right local wall-clock time and stay correct across DST. Each
    eligible user is marked notified for the day regardless of whether a
    message was sent, so the rollup fires once per day rather than repeatedly.

    Returns:
        (str): A short summary of how many users were notified.
    """
    option = Option.objects.filter(id=1).first()
    if option and option.vacation_mode:
        return "Vacation mode active; no notifications sent"

    now_utc = timezone.now()

    notified = 0
    for user in CustomUser.objects.filter(notify_enabled=True):
        local_now = now_utc.astimezone(_user_timezone(user))
        local_today = local_now.date()

        if user.last_notified_date == local_today:
            continue
        if user.notify_time > local_now.time():
            continue

        due_today = Chore.objects.filter(
            status=0, nextDue__lte=local_today
        ).count()
        if due_today > 0:
            overdue = Chore.objects.filter(
                status=0, nextDue__lt=local_today
            ).count()
            assigned = Chore.objects.filter(
                status=0, nextDue__lte=local_today, assignee=user
            ).count()
            payload = build_rollup_payload(due_today, overdue, assigned)
            for subscription in user.push_subscriptions.all():
                send_web_push(subscription, payload)
            notified += 1
        user.last_notified_date = local_today
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
