import pytest
import json
from datetime import date, timedelta


@pytest.mark.django_db
@pytest.mark.api
def test_list_chores_requires_auth(api_client):
    response = api_client.get("/api/v2/chores")
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.api
def test_list_chores(auth_client, chore):
    response = auth_client.get("/api/v2/chores")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(c["id"] == chore.id for c in data)


@pytest.mark.django_db
@pytest.mark.api
def test_list_chores_with_assignee(auth_client, chore, user):
    """Listing a chore that has an assignee must serialize the nested user.

    Regression: the nested CustomUserSchema failed to resolve `groups` during
    response re-validation, 500ing the chore list after a chore was claimed.
    """
    chore.assignee = user
    chore.save()

    response = auth_client.get("/api/v2/chores")
    assert response.status_code == 200
    result = next(c for c in response.json() if c["id"] == chore.id)
    assert result["assignee"] is not None
    assert result["assignee"]["id"] == user.id
    assert result["assignee"]["groups"] == []


@pytest.mark.django_db
@pytest.mark.api
def test_create_chore(auth_client, area):
    payload = {
        "chore_name": "New Chore",
        "area_id": area.id,
        "intervalNumber": 14,
        "unit": "day(s)",
        "effort": 2,
        "active_months": [],
    }
    response = auth_client.post(
        "/api/v2/chores",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert "id" in response.json()

    from api.models import Chore
    assert Chore.objects.filter(chore_name="New Chore").exists()


@pytest.mark.django_db
@pytest.mark.api
def test_complete_chore_updates_next_due(auth_client, chore, user):
    today = date.today()
    payload = {
        "lastCompleted": today.isoformat(),
        "completed_by_id": user.id,
    }
    response = auth_client.patch(
        f"/api/v2/chores/completechore/{chore.id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    chore.refresh_from_db()
    assert chore.nextDue == today + timedelta(days=chore.intervalNumber)
    assert chore.lastCompleted == today


@pytest.mark.django_db
@pytest.mark.api
def test_complete_chore_creates_history_item(auth_client, chore, user):
    from api.models import HistoryItem

    initial_count = HistoryItem.objects.count()
    payload = {
        "lastCompleted": date.today().isoformat(),
        "completed_by_id": user.id,
    }
    auth_client.patch(
        f"/api/v2/chores/completechore/{chore.id}",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert HistoryItem.objects.count() == initial_count + 1
    item = HistoryItem.objects.latest("id")
    assert item.chore_id == chore.id
    assert item.completed_by_id == user.id


@pytest.mark.django_db
@pytest.mark.api
def test_complete_chore_clears_assignee(auth_client, chore, user):
    chore.assignee = user
    chore.save()

    payload = {
        "lastCompleted": date.today().isoformat(),
        "completed_by_id": user.id,
    }
    auth_client.patch(
        f"/api/v2/chores/completechore/{chore.id}",
        data=json.dumps(payload),
        content_type="application/json",
    )

    chore.refresh_from_db()
    assert chore.assignee is None


@pytest.mark.django_db
@pytest.mark.api
def test_snooze_chore(auth_client, chore):
    new_due = date.today() + timedelta(days=5)
    payload = {"nextDue": new_due.isoformat()}
    response = auth_client.patch(
        f"/api/v2/chores/snoozechore/{chore.id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200

    chore.refresh_from_db()
    assert chore.nextDue == new_due


@pytest.mark.django_db
@pytest.mark.api
def test_claim_chore(auth_client, chore, user):
    payload = {"assignee_id": user.id}
    response = auth_client.patch(
        f"/api/v2/chores/claimchore/{chore.id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200

    chore.refresh_from_db()
    assert chore.assignee_id == user.id


@pytest.mark.django_db
@pytest.mark.api
def test_unclaim_chore(auth_client, chore, user):
    chore.assignee = user
    chore.save()

    payload = {"assignee_id": None}
    auth_client.patch(
        f"/api/v2/chores/claimchore/{chore.id}",
        data=json.dumps(payload),
        content_type="application/json",
    )

    chore.refresh_from_db()
    assert chore.assignee is None


@pytest.mark.django_db
@pytest.mark.api
def test_delete_chore(auth_client, chore):
    from api.models import Chore

    response = auth_client.delete(f"/api/v2/chores/{chore.id}")
    assert response.status_code == 200
    assert not Chore.objects.filter(id=chore.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_complete_chore_weekly_interval(auth_client, area, user):
    """Completing a weekly chore sets nextDue to lastCompleted + 1 week."""
    from api.models import Chore

    today = date.today()
    weekly = Chore.objects.create(
        chore_name="Weekly",
        area=area,
        intervalNumber=1,
        unit="week(s)",
        effort=1,
        nextDue=today,
        lastCompleted=today - timedelta(weeks=1),
        status=0,
    )
    payload = {"lastCompleted": today.isoformat(), "completed_by_id": user.id}
    auth_client.patch(
        f"/api/v2/chores/completechore/{weekly.id}",
        data=json.dumps(payload),
        content_type="application/json",
    )

    weekly.refresh_from_db()
    assert weekly.nextDue == today + timedelta(weeks=1)
