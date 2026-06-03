import pytest
import json
from datetime import date, timedelta


def _add_chore(area, name, due_offset, completed_offset, status=0):
    from api.models import Chore

    return Chore.objects.create(
        chore_name=name,
        area=area,
        intervalNumber=1,
        unit="day(s)",
        effort=1,
        nextDue=date.today() + timedelta(days=due_offset),
        lastCompleted=date.today() - timedelta(days=completed_offset),
        status=status,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_list_areas_with_fractional_dirtiness(auth_client, area):
    """Areas whose average dirtiness is fractional must not 500.

    Regression: AreaOut.dirtiness is an int, but the model returned a raw
    float average; Pydantic v2 rejected the fractional value.
    """
    # Two chores with different dirtiness so the average is fractional.
    _add_chore(area, "A", due_offset=2, completed_offset=1)   # ~33
    _add_chore(area, "B", due_offset=1, completed_offset=1)   # 50

    response = auth_client.get("/api/v2/areas")
    assert response.status_code == 200
    result = next(a for a in response.json() if a["id"] == area.id)
    assert isinstance(result["dirtiness"], int)


@pytest.mark.django_db
@pytest.mark.api
def test_list_areas_requires_auth(api_client):
    response = api_client.get("/api/v2/areas")
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.api
def test_list_areas(auth_client, area):
    response = auth_client.get("/api/v2/areas")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(a["id"] == area.id for a in data)


@pytest.mark.django_db
@pytest.mark.api
def test_create_area(auth_client, area_group):
    payload = {
        "area_name": "New Area",
        "area_icon": "mdi-broom",
        "group_id": area_group.id,
    }
    response = auth_client.post(
        "/api/v2/areas",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert "id" in response.json()

    from api.models import Area
    assert Area.objects.filter(area_name="New Area").exists()


@pytest.mark.django_db
@pytest.mark.api
def test_update_area(auth_client, area, area_group):
    payload = {
        "area_name": "Renamed",
        "area_icon": "mdi-broom",
        "group_id": area_group.id,
    }
    response = auth_client.put(
        f"/api/v2/areas/{area.id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200

    area.refresh_from_db()
    assert area.area_name == "Renamed"


@pytest.mark.django_db
@pytest.mark.api
def test_delete_area(auth_client, area):
    from api.models import Area

    response = auth_client.delete(f"/api/v2/areas/{area.id}")
    assert response.status_code == 200
    assert not Area.objects.filter(id=area.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_area_includes_computed_stats(auth_client, area, chore):
    response = auth_client.get("/api/v2/areas")
    assert response.status_code == 200
    result = next(a for a in response.json() if a["id"] == area.id)
    assert "dirtiness" in result
    assert "dueCount" in result
    assert "totalCount" in result
    assert result["totalCount"] == 1
