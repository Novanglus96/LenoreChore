"""Tests for PUT /api/v2/me and for the retirement of the legacy DRF API.

The DRF router that used to sit at `/api/` had no DEFAULT_PERMISSION_CLASSES and
no permission_classes on any viewset, so it fell back to AllowAny: full
unauthenticated CRUD on chores, areas, options and users. These tests pin both
halves of the fix -- the legacy routes are gone, and the endpoint replacing them
is authenticated and narrow.
"""

import json

import pytest


PROFILE = {
    "first_name": "Ada",
    "last_name": "Lovelace",
    "male": False,
    "user_color": "#3F51B5",
}


def _put(client, payload):
    return client.put(
        "/api/v2/me",
        data=json.dumps(payload),
        content_type="application/json",
    )


# ── The legacy DRF surface must stay gone ────────────────────────────────────

# Every route the retired router registered. Parameterised rather than spot
# checked so re-adding any one of them fails loudly.
@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.parametrize(
    "path",
    [
        "/api/users/",
        "/api/chores/",
        "/api/areas/",
        "/api/areagroups/",
        "/api/historyitems/",
        "/api/options/",
        "/api/months/",
        "/api/chore-complete/",
        "/api/chore-snooze/",
        "/api/historyitem-create/",
    ],
)
def test_legacy_drf_routes_are_gone(api_client, path):
    assert api_client.get(path).status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_legacy_user_detail_cannot_be_written(api_client, user):
    """The specific hole: unauthenticated PATCH of any user, any field."""
    response = api_client.patch(
        f"/api/users/{user.id}/",
        data=json.dumps({"is_superuser": True}),
        content_type="application/json",
    )
    assert response.status_code == 404
    user.refresh_from_db()
    assert user.is_superuser is False


# ── PUT /api/v2/me ───────────────────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.api
def test_update_me_requires_auth(api_client):
    assert _put(api_client, PROFILE).status_code == 401


@pytest.mark.django_db
@pytest.mark.api
def test_update_me_updates_own_profile(auth_client, user):
    response = _put(auth_client, PROFILE)
    assert response.status_code == 200

    body = response.json()
    assert body["first_name"] == "Ada"
    assert body["last_name"] == "Lovelace"
    assert body["male"] is False
    assert body["user_color"] == "#3F51B5"

    user.refresh_from_db()
    assert user.first_name == "Ada"
    assert user.male is False
    assert user.user_color == "#3F51B5"


@pytest.mark.django_db
@pytest.mark.api
def test_update_me_ignores_privilege_fields(auth_client, user):
    """Payload fields outside ProfileIn must not reach the model."""
    response = _put(
        auth_client,
        {**PROFILE, "is_superuser": True, "is_staff": True, "email": "evil@example.com"},
    )
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.is_superuser is False
    assert user.is_staff is False
    assert user.email == "test@example.com"


@pytest.mark.django_db
@pytest.mark.api
def test_update_me_cannot_target_another_user(auth_client, django_user_model):
    """There is no id in the payload or path, so a second user is untouchable."""
    other = django_user_model.objects.create(
        email="other@example.com",
        first_name="Other",
        last_name="Person",
        user_color="#009688",
    )

    assert _put(auth_client, {**PROFILE, "id": other.id}).status_code == 200

    other.refresh_from_db()
    assert other.first_name == "Other"
    assert other.user_color == "#009688"


@pytest.mark.django_db
@pytest.mark.api
def test_update_me_rejects_malformed_colour(auth_client, user):
    response = _put(auth_client, {**PROFILE, "user_color": "red; DROP TABLE"})
    assert response.status_code == 422

    user.refresh_from_db()
    assert user.user_color == "#336699"


@pytest.mark.django_db
@pytest.mark.api
def test_update_me_blank_colour_leaves_it_unchanged(auth_client, user):
    response = _put(auth_client, {**PROFILE, "user_color": ""})
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.user_color == "#336699"


@pytest.mark.django_db
@pytest.mark.api
def test_update_me_rejects_overlong_name(auth_client, user):
    """AbstractUser caps names at 150; without the guard this is a 500."""
    response = _put(auth_client, {**PROFILE, "first_name": "x" * 151})
    assert response.status_code == 422

    user.refresh_from_db()
    assert user.first_name == "Test"


@pytest.mark.django_db
@pytest.mark.api
def test_update_me_invalidates_the_users_cache(auth_client, user):
    """The DRF endpoint did not, so /users kept serving the stale name."""
    from django.core.cache import cache

    assert auth_client.get("/api/v2/users").status_code == 200
    assert cache.get("users") is not None

    _put(auth_client, PROFILE)
    assert cache.get("users") is None

    names = [u["first_name"] for u in auth_client.get("/api/v2/users").json()]
    assert "Ada" in names
