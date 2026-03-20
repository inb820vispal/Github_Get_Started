"""Tests for GET activities endpoints."""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        # Arrange
        # (no setup needed - using fixtures)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        # Verify all expected activities are present
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club",
        ]
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_has_correct_structure(self, client):
        """Test that each activity has the required fields."""
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == expected_fields
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_shows_correct_participant_count(self, client):
        """Test that participant counts match the actual participants list."""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_get_activities_shows_correct_availability(self, client):
        """Test that availability calculation is accurate (max - current participants)."""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        # Chess Club: max 12, 2 participants, should have 10 spots left
        chess_club = activities["Chess Club"]
        max_participants = chess_club["max_participants"]
        current_participants = len(chess_club["participants"])
        spots_left = max_participants - current_participants
        assert spots_left == 10


class TestRootRedirect:
    """Test suite for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"

    def test_root_with_follow_redirects_returns_html(self, client):
        """Test that following the redirect returns HTML content."""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # The static files are mounted, so this should return the HTML file
        assert "text/html" in response.headers.get("content-type", "")
