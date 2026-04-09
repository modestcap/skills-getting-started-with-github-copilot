import copy

from fastapi.testclient import TestClient
from src.app import app, activities as activities_data

client = TestClient(app)
initial_activities = copy.deepcopy(activities_data)


def setup_function():
    # Arrange: reset the in-memory activity state for each test
    activities_data.clear()
    activities_data.update(copy.deepcopy(initial_activities))


def test_get_activities_returns_known_activity():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert activity_name in data
    assert data[activity_name]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "teststudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={participant_email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {participant_email} for {activity_name}"

    activities_response = client.get("/activities")
    assert participant_email in activities_response.json()[activity_name]["participants"]


def test_signup_duplicate_returns_error():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "duplicate@mergington.edu"

    client.post(f"/activities/{activity_name}/signup?email={participant_email}")

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={participant_email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_delete_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={participant_email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"

    activities_response = client.get("/activities")
    assert participant_email not in activities_response.json()[activity_name]["participants"]


def test_delete_nonexistent_participant_returns_error():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={participant_email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
