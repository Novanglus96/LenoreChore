import json

import pytest


@pytest.fixture
def second_group(db):
    from api.models import AreaGroup

    return AreaGroup.objects.create(
        group_name="Second Group",
        group_order=2,
        group_color="#654321",
    )


@pytest.mark.django_db
@pytest.mark.api
def test_list_areagroups_is_ordered(auth_client, area_group, second_group):
    """The list was a bare .all(), so every group picker was in database order.

    group_order exists precisely to order this and nothing used it.
    """
    from api.models import AreaGroup

    # Created last but ordered first, so insertion order cannot produce a pass.
    first = AreaGroup.objects.create(
        group_name="Zeroth Group", group_order=0, group_color="#000000"
    )

    response = auth_client.get("/api/v2/areagroups")
    assert response.status_code == 200
    ids = [g["id"] for g in response.json()]
    assert ids.index(first.id) < ids.index(area_group.id) < ids.index(second_group.id)


@pytest.mark.django_db
@pytest.mark.api
def test_create_areagroup_appends_to_the_end(auth_client, area_group, second_group):
    """A new group goes last instead of colliding on the hardcoded order 1."""
    from api.models import AreaGroup

    response = auth_client.post(
        "/api/v2/areagroups",
        data=json.dumps({"group_name": "Third", "group_color": "#abcdef"}),
        content_type="application/json",
    )
    assert response.status_code == 200

    created = AreaGroup.objects.get(id=response.json()["id"])
    assert created.group_order == 3


@pytest.mark.django_db
@pytest.mark.api
def test_update_areagroup_without_order_keeps_it(auth_client, area_group):
    """group_order is optional on the way in but the column is NOT NULL.

    A rename that omits it must not try to write None.
    """
    response = auth_client.put(
        f"/api/v2/areagroups/{area_group.id}",
        data=json.dumps({"group_name": "Renamed", "group_color": "#123456"}),
        content_type="application/json",
    )
    assert response.status_code == 200

    area_group.refresh_from_db()
    assert area_group.group_name == "Renamed"
    assert area_group.group_order == 1


@pytest.mark.django_db
@pytest.mark.api
def test_delete_areagroup_reassigns_its_areas(
    auth_client, area, area_group, second_group
):
    """Areas move to a real group rather than relying on SET_DEFAULT."""

    response = auth_client.delete(
        f"/api/v2/areagroups/{area_group.id}?reassign_to={second_group.id}"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reassigned_to"] == second_group.id
    assert body["areas_moved"] == 1

    area.refresh_from_db()
    assert area.group_id == second_group.id


@pytest.mark.django_db
@pytest.mark.api
def test_delete_areagroup_defaults_to_lowest_ordered_remaining(
    auth_client, area, area_group, second_group
):
    """With no reassign_to, areas land in the first remaining group."""
    response = auth_client.delete(f"/api/v2/areagroups/{second_group.id}")
    assert response.status_code == 200
    assert response.json()["reassigned_to"] == area_group.id


@pytest.mark.django_db
@pytest.mark.api
def test_delete_the_default_group_does_not_break(auth_client, area, second_group):
    """The case that used to violate the foreign key.

    Area.group defaults to 1 with on_delete=SET_DEFAULT, so deleting group 1
    told Django to set its own areas' group_id to the row being deleted.
    """
    from api.models import AreaGroup

    # It has to be id 1 specifically: that is the value Area.group defaults to,
    # so this is the row whose deletion told Django to point its own areas at
    # it. get_or_create because the area_group fixture may already hold id 1.
    default_group, _ = AreaGroup.objects.get_or_create(
        id=1,
        defaults={
            "group_name": "Default",
            "group_order": 1,
            "group_color": "#111111",
        },
    )
    area.group = default_group
    area.save()

    response = auth_client.delete(f"/api/v2/areagroups/{default_group.id}")
    assert response.status_code == 200

    assert not AreaGroup.objects.filter(id=1).exists()
    area.refresh_from_db()
    assert area.group_id == second_group.id

    # And the endpoints that read through the group still work.
    assert auth_client.get("/api/v2/areas").status_code == 200
    assert auth_client.get("/api/v2/chores").status_code == 200


@pytest.mark.django_db
@pytest.mark.api
def test_cannot_delete_the_only_group(auth_client, area, area_group):
    """There has to be somewhere for the areas to land."""
    from api.models import AreaGroup

    response = auth_client.delete(f"/api/v2/areagroups/{area_group.id}")
    assert response.status_code == 400
    assert AreaGroup.objects.filter(id=area_group.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_cannot_reassign_to_the_group_being_deleted(
    auth_client, area_group, second_group
):
    response = auth_client.delete(
        f"/api/v2/areagroups/{area_group.id}?reassign_to={area_group.id}"
    )
    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.api
def test_delete_areagroup_invalidates_the_areas_cache(
    auth_client, area, area_group, second_group
):
    """The old delete invalidated "areagroups" alone.

    /areas stayed cached, so every area kept reporting a group that no longer
    existed until the TTL expired.
    """
    first = auth_client.get("/api/v2/areas")
    assert first.status_code == 200
    assert first.json()[0]["group"]["id"] == area_group.id

    auth_client.delete(f"/api/v2/areagroups/{area_group.id}")

    after = auth_client.get("/api/v2/areas")
    assert after.status_code == 200
    assert after.json()[0]["group"]["id"] == second_group.id


@pytest.mark.django_db
@pytest.mark.api
def test_area_with_no_group_does_not_500(auth_client, area):
    """AreaOut.group was non-Optional while Area.group is null=True.

    One group-less area took down /areas and /chores together.
    """
    area.group = None
    area.save()

    areas = auth_client.get("/api/v2/areas")
    assert areas.status_code == 200
    assert areas.json()[0]["group"] is None

    assert auth_client.get("/api/v2/chores").status_code == 200
