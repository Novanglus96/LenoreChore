import pytest
from datetime import date


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear locmem cache before and after each test to prevent bleed-over."""
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user(db):
    from api.models import CustomUser

    return CustomUser.objects.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        male=True,
        user_color="#336699",
        is_active=True,
    )


@pytest.fixture
def area_group(db):
    from api.models import AreaGroup

    return AreaGroup.objects.create(
        group_name="Test Group",
        group_order=1,
        group_color="#123456",
    )


@pytest.fixture
def area(db, area_group):
    from api.models import Area

    return Area.objects.create(
        area_name="Test Area",
        area_icon="mdi-home",
        group=area_group,
    )


@pytest.fixture
def chore(db, area):
    from api.models import Chore

    return Chore.objects.create(
        chore_name="Test Chore",
        area=area,
        intervalNumber=7,
        unit="day(s)",
        effort=1,
        nextDue=date.today(),
        lastCompleted=date.today(),
        status=0,
    )


@pytest.fixture
def option(db):
    from api.models import Option

    return Option.objects.create(
        vacation_mode=False,
        med_thresh=50,
        high_thresh=75,
    )


@pytest.fixture
def version(db):
    from api.models import Version

    return Version.objects.create(version_number="1.0.0-test")


@pytest.fixture
def api_client(db):
    from django.test import Client

    return Client()


@pytest.fixture
def auth_client(db, user):
    from django.test import Client

    client = Client()
    client.force_login(user)
    return client
