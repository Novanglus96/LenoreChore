import pytest
from django.core.management import call_command


@pytest.mark.django_db
@pytest.mark.unit
def test_scheduletasks_creates_both_schedules():
    """The command must register both the daily and the interval schedule.

    Regression guard: an empty time on the MINUTES task previously crashed
    the command, so "Send Due Notifications" was never created.
    """
    from django_q.models import Schedule

    call_command("scheduletasks")

    names = set(Schedule.objects.values_list("name", flat=True))
    assert "Process Seasonal Chores" in names
    assert "Send Due Notifications" in names

    notif = Schedule.objects.get(name="Send Due Notifications")
    assert notif.schedule_type == Schedule.MINUTES
    assert notif.minutes == 5
    assert notif.func == "api.tasks.send_due_notifications"


@pytest.mark.django_db
@pytest.mark.unit
def test_scheduletasks_is_idempotent():
    from django_q.models import Schedule

    call_command("scheduletasks")
    call_command("scheduletasks")

    assert Schedule.objects.filter(name="Send Due Notifications").count() == 1
    assert Schedule.objects.filter(name="Process Seasonal Chores").count() == 1
