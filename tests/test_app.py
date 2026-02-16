"""Tests for the Mergington High School API"""


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Tennis Club" in activities
    assert "Basketball Team" in activities
    assert activities["Tennis Club"]["description"] is not None
    assert activities["Tennis Club"]["max_participants"] > 0


def test_get_activities_contains_participants(client):
    """Test that activities include existing participants"""
    response = client.get("/activities")
    activities = response.json()
    
    # Tennis Club should have at least one participant
    assert len(activities["Tennis Club"]["participants"]) > 0
    assert "alex@mergington.edu" in activities["Tennis Club"]["participants"]


def test_successful_signup(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Tennis Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]


def test_duplicate_signup_fails(client):
    """Test that signing up twice fails"""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/Tennis Club/signup?email={email}"
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        f"/activities/Tennis Club/signup?email={email}"
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_nonexistent_activity_fails(client):
    """Test that signup for non-existent activity fails"""
    response = client.post(
        "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_successful_participant_removal(client):
    """Test successfully removing a participant"""
    email = "remove-test@mergington.edu"
    
    # First, sign up
    signup_response = client.post(
        f"/activities/Tennis Club/signup?email={email}"
    )
    assert signup_response.status_code == 200
    
    # Then, remove
    remove_response = client.delete(
        f"/activities/Tennis Club/remove?email={email}"
    )
    assert remove_response.status_code == 200
    assert "Removed" in remove_response.json()["message"]
    
    # Verify participant is gone
    get_response = client.get("/activities")
    assert email not in get_response.json()["Tennis Club"]["participants"]


def test_remove_nonexistent_participant_fails(client):
    """Test that removing non-existent participant fails"""
    response = client.delete(
        "/activities/Tennis Club/remove?email=nonexistent@mergington.edu"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_remove_from_nonexistent_activity_fails(client):
    """Test that removing from non-existent activity fails"""
    response = client.delete(
        "/activities/Nonexistent Activity/remove?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_signup_updates_participant_count(client):
    """Test that participants list is updated after signup"""
    email = "count-test@mergington.edu"
    
    # Get initial count
    response1 = client.get("/activities")
    initial_count = len(response1.json()["Chess Club"]["participants"])
    
    # Sign up
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Get updated count
    response2 = client.get("/activities")
    updated_count = len(response2.json()["Chess Club"]["participants"])
    
    assert updated_count == initial_count + 1
