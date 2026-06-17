import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        # Arrange
        # (No setup needed - API should return default activities)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_includes_required_fields(self, client):
        """Test that activities include all required fields."""
        # Arrange
        expected_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        for field in expected_fields:
            assert field in activity
    
    def test_get_activities_has_no_cache_header(self, client):
        """Test that /activities response has no-store cache control."""
        # Arrange
        # (No setup needed)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert "Cache-Control" in response.headers
        assert "no-store" in response.headers["Cache-Control"]
    
    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list."""
        # Arrange
        # (No setup needed)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity in data.items():
            assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_student_success(self, client):
        """Test successful signup for a new student."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
    
    def test_signup_updates_participants_list(self, client):
        """Test that signup actually adds student to participants."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email in activities[activity]["participants"]
    
    def test_signup_duplicate_student_fails(self, client):
        """Test that signup fails for student already registered."""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup fails for non-existent activity."""
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple different students can signup for same activity."""
        # Arrange
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        activity = "Chess Club"
        
        # Act
        client.post(f"/activities/{activity}/signup?email={email1}")
        response2 = client.post(f"/activities/{activity}/signup?email={email2}")
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert response2.status_code == 200
        assert email1 in activities[activity]["participants"]
        assert email2 in activities[activity]["participants"]
    
    def test_signup_same_student_different_activities(self, client):
        """Test that same student can signup for different activities."""
        # Arrange
        email = "versatile@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act
        response1 = client.post(f"/activities/{activity1}/signup?email={email}")
        response2 = client.post(f"/activities/{activity2}/signup?email={email}")
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_unregister_existing_participant_success(self, client):
        """Test successful unregister of existing participant."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes student from participants."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        client.delete(f"/activities/{activity}/participants?email={email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email not in activities[activity]["participants"]
    
    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregister fails for non-existent participant."""
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister fails for non-existent activity."""
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_multiple_from_same_activity(self, client):
        """Test unregistering multiple students from same activity."""
        # Arrange
        email1 = "michael@mergington.edu"
        email2 = "daniel@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response1 = client.delete(
            f"/activities/{activity}/participants?email={email1}"
        )
        response2 = client.delete(
            f"/activities/{activity}/participants?email={email2}"
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(activities[activity]["participants"]) == 0


class TestIntegration:
    """Integration tests combining multiple operations."""
    
    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signup and then unregister."""
        # Arrange
        email = "testflow@mergington.edu"
        activity = "Chess Club"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert signup succeeded
        assert signup_response.status_code == 200
        
        # Act - Verify in list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert student is registered
        assert email in activities[activity]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        
        # Assert unregister succeeded
        assert unregister_response.status_code == 200
        
        # Act - Verify removed from list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert student is unregistered
        assert email not in activities[activity]["participants"]
    
    def test_register_unregister_then_reregister(self, client):
        """Test that student can re-register after unregistering."""
        # Arrange
        email = "reregister@mergington.edu"
        activity = "Chess Club"
        
        # Act - Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Act - Unregister
        client.delete(f"/activities/{activity}/participants?email={email}")
        
        # Act - Re-register
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert re-registration succeeded
        assert response.status_code == 200
        
        # Act - Verify in list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert student is registered again
        assert email in activities[activity]["participants"]
