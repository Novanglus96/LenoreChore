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


@pytest.mark.django_db
@pytest.mark.api
def test_chore_names_lists_only_recurring_tasks(auth_client, area, other_area):
    """The "same task in several rooms" index.

    A name carried by a single chore cannot be worked through room by room,
    so it is not offered.
    """
    _chore(area, "Dust", due_offset=1)
    _chore(other_area, "Dust", due_offset=2)
    _chore(area, "Descale the kettle", due_offset=1)

    response = auth_client.get("/api/v2/chores/names")
    assert response.status_code == 200
    data = response.json()

    assert [row["chore_name"] for row in data] == ["Dust"]
    assert data[0]["chore_count"] == 2
    assert data[0]["area_count"] == 2


@pytest.mark.django_db
@pytest.mark.api
def test_chore_names_counts_areas_distinctly(auth_client, area, other_area):
    """Two chores of the same name in ONE area is still one area."""
    _chore(area, "Dust", due_offset=1)
    _chore(area, "Dust", due_offset=2)
    _chore(other_area, "Dust", due_offset=3)

    data = auth_client.get("/api/v2/chores/names").json()
    assert data[0]["chore_count"] == 3
    assert data[0]["area_count"] == 2


@pytest.mark.django_db
@pytest.mark.api
def test_chore_names_ignores_disabled_chores(auth_client, area, other_area):
    from api.models import Chore

    _chore(area, "Dust", due_offset=1)
    disabled = _chore(other_area, "Dust", due_offset=2)
    Chore.objects.filter(id=disabled.id).update(status=1)

    # Down to a single active chore, so it stops being a recurring task.
    assert auth_client.get("/api/v2/chores/names").json() == []


@pytest.mark.django_db
@pytest.mark.api
def test_chore_names_is_not_parsed_as_a_chore_id(auth_client, area):
    """/chores/{chore_id} is declared first and converts to int.

    Declared in the wrong order, this path 422s instead of reaching the
    index endpoint.
    """
    response = auth_client.get("/api/v2/chores/names")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
@pytest.mark.api
def test_filter_by_chore_name_spans_areas(auth_client, area, other_area):
    """The point of the filter: one task, every area it lives in."""
    _chore(area, "Dust", due_offset=1)
    _chore(other_area, "Dust", due_offset=2)
    _chore(area, "Mop", due_offset=1)

    response = auth_client.get("/api/v2/chores?chore_name=Dust")
    assert response.status_code == 200
    data = response.json()
    assert [c["chore_name"] for c in data] == ["Dust", "Dust"]
    assert {c["area"]["id"] for c in data} == {area.id, other_area.id}


@pytest.mark.django_db
@pytest.mark.api
def test_filter_by_chore_name_is_case_insensitive(auth_client, area, other_area):
    _chore(area, "Dust", due_offset=1)
    _chore(other_area, "dust", due_offset=2)

    data = auth_client.get("/api/v2/chores?chore_name=DUST").json()
    assert len(data) == 2


@pytest.mark.django_db
@pytest.mark.api
def test_chore_name_is_in_the_cache_key(auth_client, area, other_area):
    _chore(area, "Dust", due_offset=1)
    _chore(other_area, "Mop", due_offset=2)

    everything = auth_client.get("/api/v2/chores")
    assert len(everything.json()) == 2

    # Same request but for one task: must not be served the cached full list.
    just_dust = auth_client.get("/api/v2/chores?chore_name=Dust")
    assert [c["chore_name"] for c in just_dust.json()] == ["Dust"]


@pytest.mark.django_db
@pytest.mark.api
def test_renaming_a_chore_refreshes_the_name_index(auth_client, area, other_area):
    """The index is derived from the chore table, so a write invalidates it.

    Twelve call sites invalidate the chore caches; this is why they go
    through one helper.
    """
    import json as _json

    first = _chore(area, "Dust", due_offset=1)
    _chore(other_area, "Dust", due_offset=2)

    assert auth_client.get("/api/v2/chores/names").json()[0]["chore_count"] == 2

    response = auth_client.put(
        f"/api/v2/chores/{first.id}",
        data=_json.dumps(
            {
                "chore_name": "Polish",
                "area_id": area.id,
                "nextDue": str(date.today()),
                "lastCompleted": str(date.today()),
                "intervalNumber": 1,
                "unit": "day(s)",
                "effort": 1,
                "active_months": [],
                "status": 0,
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200

    # Only one "Dust" left, so it drops out of the index entirely.
    assert auth_client.get("/api/v2/chores/names").json() == []


@pytest.mark.django_db
@pytest.mark.api
def test_toggle_vacation_reports_the_state_it_landed_in(auth_client, option, area):
    """A toggle whose response omits the new state leaves callers guessing."""
    _chore(area, "Dust", due_offset=1)

    on = auth_client.post("/api/v2/toggle_vacation")
    assert on.status_code == 200
    assert on.json()["vacation_mode"] is True

    off = auth_client.post("/api/v2/toggle_vacation")
    assert off.status_code == 200
    assert off.json()["vacation_mode"] is False


@pytest.mark.django_db
@pytest.mark.api
def test_complete_chores_in_bulk(auth_client, area, other_area, user):
    """Working one task through every area it lives in."""
    import json as _json
    from api.models import HistoryItem

    a = _chore(area, "Dust", due_offset=-1)
    b = _chore(other_area, "Dust", due_offset=-1)
    untouched = _chore(area, "Mop", due_offset=-1)

    response = auth_client.post(
        "/api/v2/chores/complete",
        data=_json.dumps(
            {
                "ids": [a.id, b.id],
                "lastCompleted": str(date.today()),
                "completed_by_id": user.id,
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["completed"] == 2

    a.refresh_from_db()
    b.refresh_from_db()
    untouched.refresh_from_db()

    # Rolled forward by their interval, exactly as a single completion does.
    assert a.lastCompleted == date.today()
    assert a.nextDue == date.today() + timedelta(days=1)
    assert b.nextDue == date.today() + timedelta(days=1)
    # Anything not named is left alone.
    assert untouched.lastCompleted != date.today()

    assert HistoryItem.objects.filter(chore__in=[a, b]).count() == 2


@pytest.mark.django_db
@pytest.mark.api
def test_complete_chores_skips_inactive_ones(auth_client, area, user):
    """A paused or disabled chore is skipped, not silently marked done."""
    import json as _json
    from api.models import Chore

    active = _chore(area, "Dust", due_offset=-1)
    paused = _chore(area, "Dust", due_offset=-1)
    Chore.objects.filter(id=paused.id).update(status=3)  # vacation

    response = auth_client.post(
        "/api/v2/chores/complete",
        data=_json.dumps(
            {
                "ids": [active.id, paused.id],
                "lastCompleted": str(date.today()),
                "completed_by_id": user.id,
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    # The count reports what actually happened rather than what was asked.
    assert response.json()["completed"] == 1

    paused.refresh_from_db()
    assert paused.lastCompleted != date.today()


@pytest.mark.django_db
@pytest.mark.api
def test_complete_chores_rejects_an_empty_batch(auth_client, user):
    import json as _json

    response = auth_client.post(
        "/api/v2/chores/complete",
        data=_json.dumps(
            {
                "ids": [],
                "lastCompleted": str(date.today()),
                "completed_by_id": user.id,
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 422


@pytest.mark.django_db
@pytest.mark.api
def test_bulk_and_single_completion_agree(auth_client, area, other_area, user):
    """The interval arithmetic is shared, so the two must land identically.

    This is the drift the shared helper exists to prevent.
    """
    import json as _json

    single = _chore(area, "Weekly", due_offset=-1)
    single.unit = "week(s)"
    single.intervalNumber = 2
    single.save()

    batched = _chore(other_area, "Weekly", due_offset=-1)
    batched.unit = "week(s)"
    batched.intervalNumber = 2
    batched.save()

    auth_client.patch(
        f"/api/v2/chores/completechore/{single.id}",
        data=_json.dumps(
            {"lastCompleted": str(date.today()), "completed_by_id": user.id}
        ),
        content_type="application/json",
    )
    auth_client.post(
        "/api/v2/chores/complete",
        data=_json.dumps(
            {
                "ids": [batched.id],
                "lastCompleted": str(date.today()),
                "completed_by_id": user.id,
            }
        ),
        content_type="application/json",
    )

    single.refresh_from_db()
    batched.refresh_from_db()
    assert single.nextDue == batched.nextDue
    assert single.assignee_id is None and batched.assignee_id is None
