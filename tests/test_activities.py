"""
Comprehensive test suite for Mergington High School API

This test suite covers all endpoints with positive and negative test cases
using the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Team practices and games for students who love basketball",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Lap swimming, stroke drills, and swim meet preparation",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["nina@mergington.edu", "leo@mergington.edu"]
        },
        "Art Club": {
            "description": "Painting, drawing, and mixed-media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops, rehearsals, and stage production",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "isabella@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Advanced math problem solving and competition prep",
            "schedule": "Wednesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["oliver@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, research projects, and science fairs",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["liam@mergington.edu", "emma@mergington.edu"]
        }
    })
    yield
    activities.clear()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities_positive(self, client):
        """POSITIVE: Verify getting all activities returns complete list"""
        # Arrange: setup is done by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 9
        assert "Chess Club" in response.json()
        assert "Programming Class" in response.json()
        assert "Science Club" in response.json()
    
    def test_get_activities_returns_complete_activity_data_positive(self, client):
        """POSITIVE: Verify each activity contains required fields"""
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert set(activity_data.keys()) == expected_fields
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_returns_correct_participant_data_positive(self, client):
        """POSITIVE: Verify participant lists are correctly returned"""
        # Arrange
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert data["Chess Club"]["participants"] == expected_chess_participants
        assert len(data["Gym Class"]["participants"]) == 2


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_for_activity_positive(self, client):
        """POSITIVE: Successfully sign up a new student for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_student_without_prior_registration_positive(self, client):
        """POSITIVE: Student with no prior activities can sign up"""
        # Arrange
        activity_name = "Art Club"
        email = "newemail@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
    
    def test_signup_multiple_students_for_same_activity_positive(self, client):
        """POSITIVE: Multiple different students can sign up for same activity"""
        # Arrange
        activity_name = "Gym Class"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Act
        responses = [
            client.post(f"/activities/{activity_name}/signup", params={"email": email})
            for email in emails
        ]
        
        # Assert
        for response in responses:
            assert response.status_code == 200
        for email in emails:
            assert email in activities[activity_name]["participants"]
    
    def test_signup_for_nonexistent_activity_negative(self, client):
        """NEGATIVE: Attempting to sign up for non-existent activity fails"""
        # Arrange
        activity_name = "Non-existent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}
    
    def test_signup_duplicate_student_for_activity_negative(self, client):
        """NEGATIVE: Student cannot sign up twice for the same activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json() == {"detail": "Student already signed up for this activity"}
    
    def test_signup_without_email_parameter_negative(self, client):
        """NEGATIVE: Signup request without email parameter fails"""
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_signup_with_empty_email_negative(self, client):
        """NEGATIVE: Signup with empty email string is still added (edge case)"""
        # Arrange
        activity_name = "Chess Club"
        email = ""
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        # Empty email is technically allowed by the API (no validation)
        assert response.status_code == 200
    
    def test_signup_with_special_characters_in_email_positive(self, client):
        """POSITIVE: Allow email with special characters (already in db)"""
        # Arrange
        activity_name = "Programming Class"
        email = "test+tag@example.com"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
    
    def test_signup_case_sensitive_activity_name_positive(self, client):
        """POSITIVE: Activity names are case-sensitive"""
        # Arrange
        activity_name = "Chess Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_signup_case_sensitive_activity_name_negative(self, client):
        """NEGATIVE: Incorrect case for activity name returns 404"""
        # Arrange
        activity_name = "chess club"  # lowercase
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_enrolled_student_positive(self, client):
        """POSITIVE: Successfully unregister an enrolled student"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_multiple_students_positive(self, client):
        """POSITIVE: Successfully unregister multiple students from same activity"""
        # Arrange
        activity_name = "Gym Class"
        emails = ["john@mergington.edu", "olivia@mergington.edu"]
        
        # Act
        responses = [
            client.delete(f"/activities/{activity_name}/signup", params={"email": email})
            for email in emails
        ]
        
        # Assert
        for response in responses:
            assert response.status_code == 200
        for email in emails:
            assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 0
    
    def test_unregister_from_nonexistent_activity_negative(self, client):
        """NEGATIVE: Attempting to unregister from non-existent activity fails"""
        # Arrange
        activity_name = "Non-existent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}
    
    def test_unregister_student_not_enrolled_negative(self, client):
        """NEGATIVE: Cannot unregister a student who is not enrolled"""
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"  # Not enrolled
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Student not signed up for this activity"}
    
    def test_unregister_without_email_parameter_negative(self, client):
        """NEGATIVE: Unregister request without email parameter fails"""
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_unregister_already_unregistered_student_negative(self, client):
        """NEGATIVE: Cannot unregister same student twice"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act
        # First unregister succeeds
        response1 = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # Second unregister should fail
        response2 = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 404
        assert response2.json() == {"detail": "Student not signed up for this activity"}
    
    def test_unregister_case_sensitive_activity_name_negative(self, client):
        """NEGATIVE: Incorrect case for activity name returns 404"""
        # Arrange
        activity_name = "programming class"  # lowercase
        email = "sophia@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404


class TestLifecycleIntegration:
    """Integration tests for complete lifecycle: signup -> verify -> unregister"""
    
    def test_full_signup_lifecycle_positive(self, client):
        """POSITIVE: Complete lifecycle - verify data consistency"""
        # Arrange
        activity_name = "Art Club"
        email = "lifecycle@mergington.edu"
        
        # Act (Signup)
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act (Verify existence)
        activities_response = client.get("/activities")
        
        # Assert (Signup successful)
        assert signup_response.status_code == 200
        
        # Assert (Student in list)
        activity_data = activities_response.json()[activity_name]
        assert email in activity_data["participants"]
        
        # Act (Unregister)
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert (Unregister successful)
        assert unregister_response.status_code == 200
        
        # Act (Verify removal)
        activities_after = client.get("/activities").json()
        
        # Assert (Student removed)
        assert email not in activities_after[activity_name]["participants"]
    
    def test_signup_and_verify_concurrent_students_positive(self, client):
        """POSITIVE: Multiple students can signup and be tracked correctly"""
        # Arrange
        activity_name = "Basketball Team"
        students = [
            "concurrent1@mergington.edu",
            "concurrent2@mergington.edu",
            "concurrent3@mergington.edu"
        ]
        
        # Act
        for email in students:
            client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        for email in students:
            assert email in activity_data["participants"]
        assert len(activity_data["participants"]) >= 3 + 2  # 3 new + 2 original