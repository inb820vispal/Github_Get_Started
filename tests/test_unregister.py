"""Tests for DELETE unregister endpoint."""

import pytest


class TestUnregisterSuccess:
    """Test suite for successful unregister scenarios."""

    def test_unregister_removes_participant_from_activity(self, client, test_activities):
        """Test that unregistering removes a participant from the activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        initial_participant_count = len(test_activities["Chess Club"]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was removed
        updated_activity = client.get("/activities").json()["Chess Club"]
        assert email not in updated_activity["participants"]
        assert len(updated_activity["participants"]) == initial_participant_count - 1

    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns the correct success message."""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_updates_availability(self, client):
        """Test that unregistering increases the number of available spots."""
        # Arrange
        activity_name = "Tennis Club"
        email = "alex@mergington.edu"
        
        # Get initial availability
        initial_response = client.get("/activities").json()
        initial_participants = len(initial_response["Tennis Club"]["participants"])
        max_participants = initial_response["Tennis Club"]["max_participants"]
        initial_spots_left = max_participants - initial_participants

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Check updated availability
        updated_response = client.get("/activities").json()
        updated_participants = len(updated_response["Tennis Club"]["participants"])
        updated_spots_left = max_participants - updated_participants
        
        assert updated_spots_left == initial_spots_left + 1
        assert updated_participants == initial_participants - 1

    def test_unregister_multiple_times_from_different_activities(self, client):
        """Test unregistering the same person from multiple activities."""
        # Arrange
        email = "noah@mergington.edu"  # Signed up for Art Studio
        activities_to_leave = ["Art Studio"]

        # Act & Assert
        for activity_name in activities_to_leave:
            response = client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": email}
            )
            assert response.status_code == 200
            
            # Verify student was removed from this activity
            updated = client.get("/activities").json()
            assert email not in updated[activity_name]["participants"]


class TestUnregisterErrors:
    """Test suite for unregister error scenarios."""

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_participant_not_signed_up_returns_400(self, client):
        """Test that unregistering someone not signed up returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "notasignedupstudent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_twice_returns_400_on_second_attempt(self, client):
        """Test that unregistering twice from the same activity returns 400 on second attempt."""
        # Arrange
        activity_name = "Drama Club"
        email = "lucas@mergington.edu"

        # Act - First unregister (should succeed)
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert - First unregister
        assert response1.status_code == 200

        # Act - Second unregister (should fail)
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert - Second unregister
        assert response2.status_code == 400
        data = response2.json()
        assert "not signed up" in data["detail"]


class TestSignupAndUnregisterFlow:
    """Test suite for signup and unregister workflows."""

    def test_signup_then_unregister_flow(self, client):
        """Test that a user can sign up and then unregister from an activity."""
        # Arrange
        activity_name = "Basketball Team"
        email = "frank@mergington.edu"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Signup succeeded
        assert signup_response.status_code == 200
        
        # Verify participant is in list
        after_signup = client.get("/activities").json()
        assert email in after_signup[activity_name]["participants"]

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert - Unregister succeeded
        assert unregister_response.status_code == 200
        
        # Verify participant is removed
        after_unregister = client.get("/activities").json()
        assert email not in after_unregister[activity_name]["participants"]

    def test_signup_unregister_signup_again_flow(self, client):
        """Test that a user can sign up, unregister, and sign up again."""
        # Arrange
        activity_name = "Debate Team"
        email = "grace@mergington.edu"

        # Act & Assert - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Act & Assert - Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200

        # Act & Assert - Sign up again
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify participant is back in list
        final = client.get("/activities").json()
        assert email in final[activity_name]["participants"]
