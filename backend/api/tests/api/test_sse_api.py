import pytest


@pytest.mark.django_db
@pytest.mark.api
def test_sse_endpoint_requires_auth(api_client):
    response = api_client.get("/api/v2/events/")
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.api
def test_version_endpoint_no_auth_required(api_client, version):
    """Version endpoint uses auth=None and must be accessible without login."""
    response = api_client.get("/api/v2/version/list")
    assert response.status_code == 200
    assert response.json()["version_number"] == version.version_number
