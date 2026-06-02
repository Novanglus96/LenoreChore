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


@pytest.mark.django_db
@pytest.mark.api
def test_version_details_requires_auth(api_client):
    """The detailed version endpoint must NOT be public."""
    response = api_client.get("/api/v2/version/details")
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.api
def test_version_details_reports_stack(auth_client, version):
    response = auth_client.get("/api/v2/version/details")
    assert response.status_code == 200
    data = response.json()
    assert data["app_version"] == version.version_number
    assert data["python_version"]
    assert data["django_version"]
    # packages is a name->version map including known dependencies
    assert isinstance(data["packages"], dict)
    assert "django-ninja" in data["packages"]
    assert data["packages"]["django-ninja"] != "not installed"
