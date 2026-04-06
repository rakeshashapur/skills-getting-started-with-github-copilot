import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    # Arrange: Set up the test client (already done globally)

    # Act: Make a GET request to /activities
    response = client.get("/activities")

    # Assert: Check the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_successful():
    # Arrange: Prepare test data
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make a POST request to signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Check the response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]

    # Verify the participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_email():
    # Arrange: Sign up once first
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act: Try to sign up again with the same email
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should prevent duplicates
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up" in data["detail"]

    # Verify duplicate was not added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    count = activities[activity_name]["participants"].count(email)
    assert count == 1  # Only one instance


def test_signup_invalid_activity():
    # Arrange: Use a non-existent activity
    activity_name = "NonExistent Club"
    email = "test@mergington.edu"

    # Act: Make a POST request
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should return 404
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_missing_email():
    # Arrange: Activity exists, but no email
    activity_name = "Gym Class"

    # Act: POST without email param
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert: Should handle missing email (FastAPI might return 422 for validation)
    # Assuming email is required via query param
    assert response.status_code == 422  # Unprocessable Entity for missing required param