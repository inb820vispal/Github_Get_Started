"""Pytest configuration and fixtures for API tests."""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def test_activities():
    """
    Fixture that provides a deep copy of activities data for each test.
    
    This ensures that each test gets a fresh copy of the activities data,
    preventing cross-test contamination when tests modify the data.
    """
    return copy.deepcopy(activities)


@pytest.fixture
def client(test_activities, monkeypatch):
    """
    Fixture that provides a TestClient instance with isolated activity data.
    
    Uses monkeypatch to replace the app's activities dict with a test-specific
    copy, ensuring tests don't affect each other.
    """
    # Replace the app's activities with the test-specific copy
    monkeypatch.setattr("src.app.activities", test_activities)
    
    # Return a TestClient connected to the app
    return TestClient(app)
