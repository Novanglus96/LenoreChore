from datetime import date, timedelta

import pytest


def _chore(area, name, due_offset, completed_offset=1, effort=1, assignee=None):
    from api.models import Chore

    return Chore.objects.create(
        chore_name=name,
        area=area,
        intervalNumber=1,
        unit="day(s)",
        effort=effort,
        nextDue=date.today() + timedelta(days=due_offset),
        lastCompleted=date.today() - timedelta(days=completed_offset),
        status=0,
        assignee=assignee,
    )


@pytest.fixture
def other_group(db):
    from api.models import AreaGroup

    return AreaGroup.objects.create(
        group_name="Other Group", group_order=2, group_color="#654321"
    )


@pytest.fixture
def other_area(db, other_group):
    from api.models import Area

    return Area.objects.create(
        area_name="Other Area", area_icon="mdi-home", group=other_group
    )


@pytest.mark.django_db
@pytest.mark.api
def test_filter_by_group(auth_client, area, area_group, other_area):
    """Chores reach a group through their area."""
    _chore(area, "In group", due_offset=1)
    _chore(other_area, "In other group", due_offset=1)

    response = auth_client.get(f"/api/v2/chores?group_id={area_group.id}")
    assert response.status_code == 200
    names = [c["chore_name"] for c in response.json()]
    assert names == ["In group"]


@pytest.mark.django_db
@pytest.mark.api
def test_overdue_excludes_due_today(auth_client, area):
    """Due today is not yet overdue, matching how the card reads it."""
    _chore(area, "Overdue", due_offset=-3)
    _chore(area, "Due today", due_offset=0)
    _chore(area, "Later", due_offset=5)

    response = auth_client.get("/api/v2/chores?overdue=true")
    assert response.status_code == 200
    names = [c["chore_name"] for c in response.json()]
    assert names == ["Overdue"]


@pytest.mark.django_db
@pytest.mark.api
def test_sort_by_name(auth_client, area):
    _chore(area, "Zebra", due_offset=1)
    _chore(area, "Apple", due_offset=2)

    response = auth_client.get("/api/v2/chores?sort=name")
    assert response.status_code == 200
    assert [c["chore_name"] for c in response.json()] == ["Apple", "Zebra"]


@pytest.mark.django_db
@pytest.mark.api
def test_sort_by_effort_puts_least_first(auth_client, area):
    _chore(area, "Big job", due_offset=1, effort=3)
    _chore(area, "Quick", due_offset=2, effort=1)

    response = auth_client.get("/api/v2/chores?sort=effort")
    assert response.status_code == 200
    assert [c["chore_name"] for c in response.json()] == ["Quick", "Big job"]


@pytest.mark.django_db
@pytest.mark.api
def test_sort_by_dirtiest(auth_client, area):
    """dirtiness is a Python property, so this cannot be an order_by.

    The dirtier chore is the one further past its interval: completed longer
    ago relative to how long it had.
    """
    # Filthy: completed 15 days ago on a 10-day interval -> well past due.
    _chore(area, "Filthy", due_offset=-5, completed_offset=15)
    # Cleanish: completed yesterday on a 10-day interval -> 10%.
    _chore(area, "Cleanish", due_offset=9, completed_offset=1)

    response = auth_client.get("/api/v2/chores?sort=dirtiest")
    assert response.status_code == 200
    data = response.json()
    assert [c["chore_name"] for c in data] == ["Filthy", "Cleanish"]
    assert data[0]["dirtiness"] >= data[1]["dirtiness"]


@pytest.mark.django_db
@pytest.mark.api
def test_unknown_sort_is_rejected(auth_client, area):
    response = auth_client.get("/api/v2/chores?sort=whatever")
    assert response.status_code == 422


@pytest.mark.django_db
@pytest.mark.api
def test_new_params_are_in_the_cache_key(auth_client, area, area_group, other_area):
    """The regression this guards is silent and looks like a caching win.

    The key was f"chores:{inactive}:{timeframe}:{assignee_id}:{area_id}", so a
    request that differed only by sort or group hit the previous request's
    entry and returned the wrong list.
    """
    # Everything up front: creating a chore through the ORM mid-test bypasses
    # the API's cache invalidation, which would make this a test of staleness
    # rather than of the key.
    _chore(area, "Apple", due_offset=5)
    _chore(area, "Zebra", due_offset=1)
    _chore(other_area, "Elsewhere", due_offset=1)

    by_due = auth_client.get("/api/v2/chores?sort=due")
    assert [c["chore_name"] for c in by_due.json()] == [
        "Elsewhere",
        "Zebra",
        "Apple",
    ]

    # Same filters, different sort: must not be served the cached due-order
    # list. Under the old key these two requests collided exactly.
    by_name = auth_client.get("/api/v2/chores?sort=name")
    assert [c["chore_name"] for c in by_name.json()] == [
        "Apple",
        "Elsewhere",
        "Zebra",
    ]

    # Same again for group, which also did not exist in the old key.
    grouped = auth_client.get(f"/api/v2/chores?group_id={area_group.id}")
    assert [c["chore_name"] for c in grouped.json()] == ["Zebra", "Apple"]

    # And overdue, likewise absent from it.
    overdue = auth_client.get("/api/v2/chores?overdue=true")
    assert overdue.json() == []


@pytest.mark.django_db
@pytest.mark.api
def test_filters_combine(auth_client, area, area_group, other_area, user):
    """Group, overdue and assignee all apply together."""
    _chore(area, "Mine and overdue", due_offset=-2, assignee=user)
    _chore(area, "Overdue but unassigned", due_offset=-2)
    _chore(area, "Mine but not overdue", due_offset=4, assignee=user)
    _chore(other_area, "Other group", due_offset=-2, assignee=user)

    response = auth_client.get(
        f"/api/v2/chores?group_id={area_group.id}&overdue=true&assignee_id={user.id}"
    )
    assert response.status_code == 200
    assert [c["chore_name"] for c in response.json()] == ["Mine and overdue"]
