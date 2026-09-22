from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities_returns_activity_list():
    # Arrange
    # No special setup required for this endpoint

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_adds_participant():
    # Arrange
    activity_name = "Science Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in client.get("/activities").json()[activity_name]["participants"]

    # Cleanup
    client.delete(f"/activities/{activity_name}/participants/{email}")


def test_signup_rejects_duplicate_for_same_activity():
    # Arrange
    activity_name = "Science Club"
    email = "duplicate@mergington.edu"

    # Act
    first = client.post(f"/activities/{activity_name}/signup?email={email}")
    second = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["detail"] == "Student already signed up for this activity"

    # Cleanup
    client.delete(f"/activities/{activity_name}/participants/{email}")


def test_signup_rejects_unknown_activity():
    # Arrange
    path = "/activities/Unknown Activity/signup?email=student@mergington.edu"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Art Club"
    email = "remove-me@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_rejects_missing_participant():
    # Arrange
    activity_name = "Debate Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"
