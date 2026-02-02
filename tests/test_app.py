import copy

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def _reset_activities():
    original = copy.deepcopy(activities)
    def _restore():
        activities.clear()
        activities.update(original)
    return _restore


def test_get_activities_returns_data():
    restore = _reset_activities()
    try:
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Tennis Club" in data
        assert "Chess Club" in data
    finally:
        restore()


def test_signup_adds_participant():
    restore = _reset_activities()
    try:
        email = "newstudent@mergington.edu"
        response = client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": email},
        )
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]

        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Tennis Club"]["participants"]
    finally:
        restore()


def test_signup_duplicate_student_returns_error():
    restore = _reset_activities()
    try:
        email = "alex@mergington.edu"
        response = client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": email},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for an activity"
    finally:
        restore()


def test_signup_unknown_activity_returns_error():
    restore = _reset_activities()
    try:
        response = client.post(
            "/activities/Unknown%20Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    finally:
        restore()
