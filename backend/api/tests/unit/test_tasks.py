import pytest
import datetime as dt
from django.utils import timezone as djtz

from api.tasks import build_rollup_payload, send_due_notifications


# ── build_rollup_payload ─────────────────────────────────────────────────────

@pytest.mark.unit
def test_rollup_payload_plural():
    payload = build_rollup_payload(due_today=5, overdue=2, assigned=3)
    assert payload["title"] == "LenoreChore reminders"
    assert payload["body"] == "5 chores due today, 2 overdue — 3 assigned to you"
    assert payload["url"] == "/list"


@pytest.mark.unit
def test_rollup_payload_singular_and_no_assigned():
    payload = build_rollup_payload(due_today=1, overdue=0, assigned=0)
    assert payload["body"] == "1 chore due today, 0 overdue"
    assert "assigned to you" not in payload["body"]


# ── send_due_notifications ───────────────────────────────────────────────────

def _make_user(email, enabled, hour, minute=0):
    from api.models import CustomUser

    return CustomUser.objects.create(
        email=email,
        first_name="T",
        last_name="U",
        male=True,
        user_color="#336699",
        is_active=True,
        notify_enabled=enabled,
        notify_time=dt.time(hour, minute),
    )


@pytest.fixture
def fixed_now(mocker):
    """Pin the task's clock to 09:00 today (app tz)."""
    now = djtz.make_aware(dt.datetime.combine(dt.date.today(), dt.time(9, 0)))
    mocker.patch("api.tasks.timezone.localtime", return_value=now)
    return now


@pytest.mark.django_db
@pytest.mark.unit
def test_notifies_eligible_user_and_pushes(db, chore, fixed_now, mocker):
    """A due chore exists; an opted-in user past their time gets pushed."""
    from api.models import PushSubscription

    send = mocker.patch("api.tasks.send_web_push", return_value=True)
    user = _make_user("a@example.com", enabled=True, hour=8)
    PushSubscription.objects.create(
        user=user, endpoint="https://p/x", p256dh="k", auth="s"
    )

    result = send_due_notifications()

    assert send.call_count == 1
    user.refresh_from_db()
    assert user.last_notified_date == fixed_now.date()
    assert "Notified 1" in result


@pytest.mark.django_db
@pytest.mark.unit
def test_skips_disabled_and_future_time_and_already_notified(
    db, chore, fixed_now, mocker
):
    send = mocker.patch("api.tasks.send_web_push", return_value=True)
    _make_user("off@example.com", enabled=False, hour=8)          # disabled
    _make_user("later@example.com", enabled=True, hour=10)        # time not reached
    done = _make_user("done@example.com", enabled=True, hour=8)   # already notified
    done.last_notified_date = fixed_now.date()
    done.save()

    result = send_due_notifications()

    assert send.call_count == 0
    assert "Notified 0" in result


@pytest.mark.django_db
@pytest.mark.unit
def test_no_due_chores_marks_notified_without_pushing(db, fixed_now, mocker):
    """With nothing due, eligible users are marked done but get no push."""
    send = mocker.patch("api.tasks.send_web_push", return_value=True)
    user = _make_user("a@example.com", enabled=True, hour=8)

    result = send_due_notifications()

    assert send.call_count == 0
    user.refresh_from_db()
    assert user.last_notified_date == fixed_now.date()
    assert "Notified 0" in result
