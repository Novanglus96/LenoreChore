import pytest
from datetime import date, timedelta


# ── Chore.dirtiness ──────────────────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.unit
def test_chore_dirtiness_zero_when_interval_is_zero(chore):
    """lastCompleted == nextDue → timeperiod is 0 → dirtiness is 0."""
    chore.lastCompleted = date.today()
    chore.nextDue = date.today()
    chore.save()

    assert chore.dirtiness == 0


@pytest.mark.django_db
@pytest.mark.unit
def test_chore_dirtiness_halfway(chore):
    """Halfway through a 14-day interval → 50%."""
    chore.lastCompleted = date.today() - timedelta(days=7)
    chore.nextDue = date.today() + timedelta(days=7)
    chore.save()

    assert chore.dirtiness == 50


@pytest.mark.django_db
@pytest.mark.unit
def test_chore_dirtiness_capped_at_100_when_overdue(chore):
    """Chore past its due date → capped at 100%."""
    chore.lastCompleted = date.today() - timedelta(days=14)
    chore.nextDue = date.today() - timedelta(days=7)
    chore.save()

    assert chore.dirtiness == 100


# ── Chore.duedays ────────────────────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.unit
def test_chore_duedays_future(chore):
    chore.nextDue = date.today() + timedelta(days=5)
    chore.save()

    assert chore.duedays == 5


@pytest.mark.django_db
@pytest.mark.unit
def test_chore_duedays_today(chore):
    chore.nextDue = date.today()
    chore.save()

    assert chore.duedays == 0


@pytest.mark.django_db
@pytest.mark.unit
def test_chore_duedays_overdue(chore):
    chore.nextDue = date.today() - timedelta(days=3)
    chore.save()

    assert chore.duedays == -3


# ── Area.dirtiness ───────────────────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.unit
def test_area_dirtiness_no_chores(area):
    assert area.dirtiness == 0


@pytest.mark.django_db
@pytest.mark.unit
def test_area_dirtiness_averages_chore_dirtiness(area, chore):
    """Area dirtiness = average dirtiness of its active chores."""
    from api.models import Chore

    chore.lastCompleted = date.today() - timedelta(days=7)
    chore.nextDue = date.today() + timedelta(days=7)
    chore.save()

    chore2 = Chore.objects.create(
        chore_name="Chore 2",
        area=area,
        intervalNumber=14,
        unit="day(s)",
        effort=1,
        nextDue=date.today() + timedelta(days=7),
        lastCompleted=date.today() - timedelta(days=7),
        status=0,
    )

    assert area.dirtiness == (chore.dirtiness + chore2.dirtiness) / 2


@pytest.mark.django_db
@pytest.mark.unit
def test_area_dirtiness_excludes_inactive_chores(area, chore):
    """Inactive chores (status != 0) should not affect area dirtiness."""
    chore.lastCompleted = date.today() - timedelta(days=7)
    chore.nextDue = date.today() + timedelta(days=7)
    chore.save()
    active_dirtiness = area.dirtiness

    from api.models import Chore

    Chore.objects.create(
        chore_name="Inactive",
        area=area,
        intervalNumber=7,
        unit="day(s)",
        effort=1,
        nextDue=date.today() - timedelta(days=30),
        lastCompleted=date.today() - timedelta(days=60),
        status=1,  # inactive
    )

    assert area.dirtiness == active_dirtiness


# ── Area.dueCount / totalCount ───────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.unit
def test_area_due_count(area, chore):
    from api.models import Chore

    chore.nextDue = date.today() - timedelta(days=1)
    chore.save()

    Chore.objects.create(
        chore_name="Not Due",
        area=area,
        intervalNumber=7,
        unit="day(s)",
        effort=1,
        nextDue=date.today() + timedelta(days=3),
        lastCompleted=date.today(),
        status=0,
    )

    assert area.dueCount == 1


@pytest.mark.django_db
@pytest.mark.unit
def test_area_total_count_excludes_inactive(area, chore):
    from api.models import Chore

    Chore.objects.create(
        chore_name="Inactive",
        area=area,
        intervalNumber=7,
        unit="day(s)",
        effort=1,
        nextDue=date.today(),
        lastCompleted=date.today(),
        status=1,
    )

    assert area.totalCount == 1
