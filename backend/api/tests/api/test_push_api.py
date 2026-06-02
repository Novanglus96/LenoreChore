import pytest
import json
from datetime import time


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
