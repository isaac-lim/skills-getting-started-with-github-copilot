import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert "participants" in data[expected_activity]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "student@example.com"
    assert new_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={new_email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_activity_returns_400_when_duplicate():
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={existing_email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_deletes_the_student():
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = activities[activity_name]["participants"][0]
    assert email_to_remove in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={email_to_remove}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email_to_remove} from {activity_name}"}
    assert email_to_remove not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={missing_email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_from_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
