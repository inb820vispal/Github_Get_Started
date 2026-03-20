"""Tests for POST signup endpoint."""

import pytest


class TestSignupSuccess:
    """Test suite for successful signup scenarios."""

    def test_signup_adds_participant_to_activity(self, client, test_activities):
        """Test that a new participant is added to the activity's participant list."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_participants = test_activities["Chess Club"]["participants"].copy()

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added to the activity
        updated_activity = client.get("/activities").json()["Chess Club"]
        assert email in updated_activity["participants"]
        assert len(updated_activity["participants"]) == len(initial_participants) + 1

    def test_signup_returns_success_message(self, client):
        """Test that signup returns the correct success message."""
        # Arrange
        activity_name = "Programming Class"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_updates_availability(self, client):
        """Test that signing up decreases the number of available spots."""
        # Arrange
        activity_name = "Tennis Club"
        email = "bob@mergington.edu"
        
        # Get initial availability
        initial_response = client.get("/activities").json()
        initial_participants = len(initial_response["Tennis Club"]["participants"])
        max_participants = initial_response["Tennis Club"]["max_participants"]
        initial_spots_left = max_participants - initial_participants

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Check updated availability
        updated_response = client.get("/activities").json()
        updated_participants = len(updated_response["Tennis Club"]["participants"])
        updated_spots_left = max_participants - updated_participants
        
        assert updated_spots_left == initial_spots_left - 1
        assert updated_participants == initial_participants + 1

    def test_signup_to_different_activities(self, client):
        """Test signing up the same email to multiple different activities."""
        # Arrange
        email = "charlie@mergington.edu"
        activities_to_join = ["Chess Club", "Drama Club", "Science Club"]

        # Act & Assert
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
            
            # Verify student was added to this activity
            updated = client.get("/activities").json()
            assert email in updated[activity_name]["participants"]


class TestSignupErrors:
    """Test suite for signup error scenarios."""

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that signing up with a duplicate email returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up for Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
