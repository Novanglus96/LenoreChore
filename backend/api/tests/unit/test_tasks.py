import pytest
import datetime as dt

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

def _make_user(email, enabled, hour, minute=0, tz="America/New_York"):
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
        notify_timezone=tz,
    )


@pytest.fixture
def fixed_now(mocker):
    """Pin the task clock to 14:00 UTC today.

    That is ~9-10 AM US-Eastern and ~6-7 AM US-Pacific regardless of DST, so an
    08:00 reminder has passed for an Eastern user but not for a Pacific one.
    """
    now_utc = dt.datetime.combine(
        dt.date.today(), dt.time(14, 0), tzinfo=dt.timezone.utc
    )
    mocker.patch("api.tasks.timezone.now", return_value=now_utc)
    return now_utc


@pytest.mark.django_db
@pytest.mark.unit
def test_notifies_eligible_user_and_pushes(db, chore, fixed_now, mocker):
    from api.models import PushSubscription

    send = mocker.patch("api.tasks.send_web_push", return_value=True)
    user = _make_user("a@example.com", enabled=True, hour=8)
    PushSubscription.objects.create(
        user=user, endpoint="https://p/x", p256dh="k", auth="s"
    )

    result = send_due_notifications()

    assert send.call_count == 1
    user.refresh_from_db()
    assert user.last_notified_date is not None
    assert "Notified 1" in result


@pytest.mark.django_db
@pytest.mark.unit
def test_skips_disabled_future_and_already_notified(db, chore, fixed_now, mocker):
    send = mocker.patch("api.tasks.send_web_push", return_value=True)
    _make_user("off@example.com", enabled=False, hour=8)          # disabled
    _make_user("later@example.com", enabled=True, hour=23)        # time not reached
    done = _make_user("done@example.com", enabled=True, hour=8)   # already notified
    done.last_notified_date = dt.date.today()
    done.save()

    result = send_due_notifications()

    assert send.call_count == 0
    assert "Notified 0" in result


@pytest.mark.django_db
@pytest.mark.unit
def test_honors_user_timezone(db, chore, fixed_now, mocker):
    """At 14:00 UTC an Eastern 08:00 has passed but a Pacific 08:00 has not."""
    from api.models import PushSubscription

    send = mocker.patch("api.tasks.send_web_push", return_value=True)
    east = _make_user("east@example.com", True, 8, tz="America/New_York")
    west = _make_user("west@example.com", True, 8, tz="America/Los_Angeles")
    PushSubscription.objects.create(
        user=east, endpoint="https://p/e", p256dh="k", auth="s"
    )
    PushSubscription.objects.create(
        user=west, endpoint="https://p/w", p256dh="k", auth="s"
    )

    result = send_due_notifications()

    assert send.call_count == 1
    east.refresh_from_db()
    west.refresh_from_db()
    assert east.last_notified_date is not None
    assert west.last_notified_date is None
    assert "Notified 1" in result


@pytest.mark.django_db
@pytest.mark.unit
def test_invalid_timezone_falls_back_to_server(db, chore, fixed_now, mocker):
    """A bad timezone string must not crash; it falls back to the server tz."""
    from api.models import PushSubscription

    send = mocker.patch("api.tasks.send_web_push", return_value=True)
    user = _make_user("bad@example.com", True, 8, tz="Not/AZone")
    PushSubscription.objects.create(
        user=user, endpoint="https://p/b", p256dh="k", auth="s"
    )

    result = send_due_notifications()

    # Server tz is America/New_York in tests, so 08:00 has passed at 14:00 UTC.
    assert send.call_count == 1
    assert "Notified 1" in result


@pytest.mark.django_db
@pytest.mark.unit
def test_no_due_chores_marks_notified_without_pushing(db, fixed_now, mocker):
    send = mocker.patch("api.tasks.send_web_push", return_value=True)
    user = _make_user("a@example.com", enabled=True, hour=8)

    result = send_due_notifications()

    assert send.call_count == 0
    user.refresh_from_db()
    assert user.last_notified_date is not None
    assert "Notified 0" in result
