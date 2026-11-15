import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_static_index_returns_html(client):
    response = client.get("/static/index.html")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Mergington High School" in response.text


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Gym Class" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_success(client):
    activity_name = "Chess Club"
    before = len(activities[activity_name]["participants"])
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "new-student@mergington.edu"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new-student@mergington.edu for Chess Club"
    }
    assert len(activities[activity_name]["participants"]) == before + 1


def test_signup_duplicate_email_rejected(client):
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_activity_not_found(client):
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
