import pytest
import json
import datetime as dt
from datetime import date, time


# ── VAPID key ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.api
def test_vapid_key_requires_auth(api_client):
    response = api_client.get("/api/v2/push/vapid-key")
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.api
def test_vapid_key_returns_public_key(auth_client, settings):
    settings.VAPID_PUBLIC_KEY = "test-public-key"
    response = auth_client.get("/api/v2/push/vapid-key")
    assert response.status_code == 200
    assert response.json()["public_key"] == "test-public-key"


# ── Subscribe / unsubscribe ──────────────────────────────────────────────────

SUB = {"endpoint": "https://push.example.com/abc", "p256dh": "key", "auth": "sec"}


@pytest.mark.django_db
@pytest.mark.api
def test_subscribe_requires_auth(api_client):
    response = api_client.post(
        "/api/v2/push/subscribe",
        data=json.dumps(SUB),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.api
def test_subscribe_creates_subscription(auth_client, user):
    from api.models import PushSubscription

    response = auth_client.post(
        "/api/v2/push/subscribe",
        data=json.dumps(SUB),
        content_type="application/json",
    )
    assert response.status_code == 200
    sub = PushSubscription.objects.get(endpoint=SUB["endpoint"])
    assert sub.user_id == user.id
    assert sub.p256dh == "key"


@pytest.mark.django_db
@pytest.mark.api
def test_subscribe_is_idempotent(auth_client):
    from api.models import PushSubscription

    for _ in range(2):
        auth_client.post(
            "/api/v2/push/subscribe",
            data=json.dumps(SUB),
            content_type="application/json",
        )
    assert PushSubscription.objects.filter(endpoint=SUB["endpoint"]).count() == 1


@pytest.mark.django_db
@pytest.mark.api
def test_unsubscribe_removes_subscription(auth_client, user):
    from api.models import PushSubscription

    PushSubscription.objects.create(user=user, **SUB)
    response = auth_client.post(
        "/api/v2/push/unsubscribe",
        data=json.dumps({"endpoint": SUB["endpoint"]}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert not PushSubscription.objects.filter(endpoint=SUB["endpoint"]).exists()


# ── Notification preferences ─────────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.api
def test_get_notification_prefs(auth_client, user):
    response = auth_client.get("/api/v2/me/notifications")
    assert response.status_code == 200
    data = response.json()
    assert data["notify_enabled"] is False
    assert "notify_time" in data


@pytest.mark.django_db
@pytest.mark.api
def test_update_notification_prefs(auth_client, user):
    response = auth_client.put(
        "/api/v2/me/notifications",
        data=json.dumps(
            {
                "notify_enabled": True,
                "notify_time": "07:30:00",
                "notify_timezone": "America/Chicago",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.notify_enabled is True
    assert user.notify_time == time(7, 30)
    assert user.notify_timezone == "America/Chicago"


def _pin_now_to_1pm_eastern(mocker):
    """Pin the endpoint clock to 17:00 UTC (12-13:00 US-Eastern)."""
    now_utc = dt.datetime.combine(
        date.today(), dt.time(17, 0), tzinfo=dt.timezone.utc
    )
    mocker.patch("backend.api.timezone.now", return_value=now_utc)


@pytest.mark.django_db
@pytest.mark.api
def test_update_prefs_future_time_resets_today_dedup(auth_client, user, mocker):
    """Moving the reminder to a still-future time clears last_notified_date."""
    _pin_now_to_1pm_eastern(mocker)
    user.last_notified_date = date.today()
    user.save()

    response = auth_client.put(
        "/api/v2/me/notifications",
        data=json.dumps(
            {
                "notify_enabled": True,
                "notify_time": "23:00:00",  # ahead of ~1 PM Eastern
                "notify_timezone": "America/New_York",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.last_notified_date is None


@pytest.mark.django_db
@pytest.mark.api
def test_update_prefs_past_time_keeps_dedup(auth_client, user, mocker):
    """A time already passed today must NOT re-arm the reminder."""
    _pin_now_to_1pm_eastern(mocker)
    user.last_notified_date = date.today()
    user.save()

    auth_client.put(
        "/api/v2/me/notifications",
        data=json.dumps(
            {
                "notify_enabled": True,
                "notify_time": "08:00:00",  # before ~1 PM Eastern
                "notify_timezone": "America/New_York",
            }
        ),
        content_type="application/json",
    )

    user.refresh_from_db()
    assert user.last_notified_date == date.today()


@pytest.mark.django_db
@pytest.mark.api
def test_update_prefs_disabled_does_not_reset_dedup(auth_client, user, mocker):
    """Disabling reminders never re-arms today's dedup."""
    _pin_now_to_1pm_eastern(mocker)
    user.last_notified_date = date.today()
    user.save()

    auth_client.put(
        "/api/v2/me/notifications",
        data=json.dumps(
            {
                "notify_enabled": False,
                "notify_time": "23:00:00",
                "notify_timezone": "America/New_York",
            }
        ),
        content_type="application/json",
    )

    user.refresh_from_db()
    assert user.last_notified_date == date.today()


@pytest.mark.django_db
@pytest.mark.api
def test_update_notification_prefs_rejects_invalid_timezone(auth_client, user):
    response = auth_client.put(
        "/api/v2/me/notifications",
        data=json.dumps(
            {
                "notify_enabled": True,
                "notify_time": "07:30:00",
                "notify_timezone": "Not/AZone",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200

    user.refresh_from_db()
    # Invalid timezone is dropped (empty = server fallback), never stored.
    assert user.notify_timezone == ""
