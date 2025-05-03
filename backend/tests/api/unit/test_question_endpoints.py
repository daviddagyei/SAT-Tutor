"""
Unit tests for the question-related endpoints
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models.user import User, UserRole
from app.models.question import Question, QuestionType
from app.models.topic import Topic
from app.models.practice_session import PracticeSession
from app.services.learning_service import LearningService
from app.api.v1.endpoints.questions import router as question_router


@pytest.fixture
def mock_learning_service():
    """Mock learning service for testing endpoints"""
    return MagicMock(spec=LearningService)


@pytest.fixture
def test_app(mock_learning_service):
    """Create a test FastAPI app with the questions router"""
    app = FastAPI()
    
    # Override the dependency to return our mock service
    def get_learning_service():
        return mock_learning_service
    
    # Use the same router but override dependencies
    app.include_router(question_router)
    
    # Override dependencies
    app.dependency_overrides = {
        # Replace the real services with our mocks
        "get_learning_service": get_learning_service,
        # Mock the get_current_user dependency to return a test user
        "get_current_user": lambda: sample_user()
    }
    
    return app


@pytest.fixture
def client(test_app):
    """Create a test client for the FastAPI app"""
    return TestClient(test_app)


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(
        id="user_123",
        email="student@example.com",
        hashed_password="hashed_password",
        full_name="Student User",
        role=UserRole.STUDENT,
        is_email_confirmed=True
    )


@pytest.fixture
def sample_topics():
    """Create sample topics for testing"""
    return [
        Topic(
            id="topic_1",
            name="Algebra",
            description="Basic algebra questions",
            subject_id="math_subject",
            difficulty_level=2
        ),
        Topic(
            id="topic_2",
            name="Geometry",
            description="Basic geometry questions",
            subject_id="math_subject",
            difficulty_level=3
        )
    ]


@pytest.fixture
def sample_questions():
    """Create sample questions for testing"""
    return [
        Question(
            id="q1",
            topic_id="topic_1",
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 2+2?",
            answer="B",
            explanation="Simple addition",
            options=[
                {"id": "A", "text": "3"},
                {"id": "B", "text": "4"},
                {"id": "C", "text": "5"}
            ],
            difficulty=2
        ),
        Question(
            id="q2",
            topic_id="topic_1",
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 3+3?",
            answer="C",
            explanation="Addition",
            options=[
                {"id": "A", "text": "4"},
                {"id": "B", "text": "5"},
                {"id": "C", "text": "6"}
            ],
            difficulty=2
        )
    ]


@pytest.fixture
def sample_practice_session(sample_user):
    """Create a sample practice session for testing"""
    session = PracticeSession(
        id="session_123",
        user_id=sample_user.id,
        topic_ids=["topic_1"],
        question_ids=["q1", "q2"],
        completed=False
    )
    return session


class TestQuestionEndpoints:
    """Tests for question endpoints"""
    
    def test_get_questions_by_topic(self, client, mock_learning_service, sample_questions):
        """Test getting questions by topic"""
        # Configure the mock service
        mock_learning_service.get_questions_by_topic.return_value = sample_questions
        
        # Make the request
        response = client.get("/questions/topic/topic_1")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "q1"
        assert data[0]["content"] == "What is 2+2?"
        assert data[1]["id"] == "q2"
        
        # Check that the service was called correctly
        mock_learning_service.get_questions_by_topic.assert_called_once_with(
            topic_id="topic_1"
        )
    
    def test_get_question_by_id(self, client, mock_learning_service, sample_questions):
        """Test getting a question by ID"""
        # Configure the mock service
        mock_learning_service.get_question_by_id.return_value = sample_questions[0]
        
        # Make the request
        response = client.get("/questions/q1")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "q1"
        assert data["content"] == "What is 2+2?"
        assert data["answer"] == "B"  # Should include the answer
        assert data["explanation"] == "Simple addition"
        
        # Check that the service was called correctly
        mock_learning_service.get_question_by_id.assert_called_once_with("q1")
    
    def test_get_question_not_found(self, client, mock_learning_service):
        """Test getting a question that doesn't exist"""
        # Configure the mock service
        mock_learning_service.get_question_by_id.return_value = None
        
        # Make the request
        response = client.get("/questions/nonexistent")
        
        # Check the response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Question not found" in data["detail"]
    
    def test_create_practice_session(self, client, mock_learning_service, sample_practice_session):
        """Test creating a practice session"""
        # Configure the mock service
        mock_learning_service.create_practice_session.return_value = sample_practice_session
        
        # Make the request
        response = client.post(
            "/questions/practice-sessions",
            json={
                "topic_ids": ["topic_1"],
                "question_count": 2,
                "difficulty_range": [1, 3]
            }
        )
        
        # Check the response
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "session_123"
        assert data["user_id"] == "user_123"
        assert data["topic_ids"] == ["topic_1"]
        assert data["question_ids"] == ["q1", "q2"]
        assert data["completed"] is False
        
        # Check that the service was called correctly
        mock_learning_service.create_practice_session.assert_called_once_with(
            user_id="user_123",  # From the current user
            topic_ids=["topic_1"],
            question_count=2,
            difficulty_range=(1, 3)
        )
    
    def test_get_practice_session(self, client, mock_learning_service, sample_practice_session):
        """Test getting a practice session by ID"""
        # Configure the mock service
        mock_learning_service.get_practice_session.return_value = sample_practice_session
        
        # Make the request
        response = client.get("/questions/practice-sessions/session_123")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "session_123"
        assert data["user_id"] == "user_123"
        assert data["topic_ids"] == ["topic_1"]
        assert data["question_ids"] == ["q1", "q2"]
        
        # Check that the service was called correctly
        mock_learning_service.get_practice_session.assert_called_once_with("session_123")
    
    def test_get_practice_session_not_found(self, client, mock_learning_service):
        """Test getting a practice session that doesn't exist"""
        # Configure the mock service
        mock_learning_service.get_practice_session.return_value = None
        
        # Make the request
        response = client.get("/questions/practice-sessions/nonexistent")
        
        # Check the response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Practice session not found" in data["detail"]
    
    def test_answer_question(self, client, mock_learning_service):
        """Test answering a question in a practice session"""
        # Configure the mock service
        mock_learning_service.answer_question.return_value = {
            "is_correct": True,
            "correct_answer": "B",
            "explanation": "Simple addition"
        }
        
        # Make the request
        response = client.post(
            "/questions/practice-sessions/session_123/questions/q1/answer",
            json={
                "answer": "B",
                "time_taken_seconds": 30
            }
        )
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True
        assert data["correct_answer"] == "B"
        assert data["explanation"] == "Simple addition"
        
        # Check that the service was called correctly
        mock_learning_service.answer_question.assert_called_once_with(
            session_id="session_123",
            question_id="q1",
            answer="B",
            time_taken_seconds=30
        )
    
    def test_complete_practice_session(self, client, mock_learning_service, sample_practice_session):
        """Test completing a practice session"""
        # Create a completed session
        completed_session = sample_practice_session
        completed_session.completed = True
        completed_session.score = 1.0
        
        # Configure the mock service
        mock_learning_service.complete_practice_session.return_value = completed_session
        
        # Make the request
        response = client.post("/questions/practice-sessions/session_123/complete")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True
        assert data["score"] == 1.0
        
        # Check that the service was called correctly
        mock_learning_service.complete_practice_session.assert_called_once_with("session_123")
    
    def test_get_user_statistics(self, client, mock_learning_service):
        """Test getting user learning statistics"""
        # Configure the mock service
        mock_learning_service.get_user_statistics.return_value = {
            "total_sessions": 5,
            "total_questions": 20,
            "correct_answers": 15,
            "average_score": 0.75,
            "average_time_per_question": 45.5,
            "topic_statistics": {
                "topic_1": {
                    "total_questions": 10,
                    "correct_answers": 8,
                    "average_score": 0.8
                },
                "topic_2": {
                    "total_questions": 10,
                    "correct_answers": 7,
                    "average_score": 0.7
                }
            }
        }
        
        # Make the request
        response = client.get("/questions/statistics/user")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 5
        assert data["total_questions"] == 20
        assert data["correct_answers"] == 15
        assert data["average_score"] == 0.75
        assert "topic_statistics" in data
        assert len(data["topic_statistics"]) == 2
        
        # Check that the service was called correctly
        mock_learning_service.get_user_statistics.assert_called_once_with("user_123")
    
    def test_get_question_statistics(self, client, mock_learning_service):
        """Test getting statistics for a specific question"""
        # Configure the mock service
        mock_learning_service.get_question_statistics.return_value = {
            "total_attempts": 100,
            "correct_answers": 75,
            "accuracy_rate": 0.75,
            "average_time": 42.5,
            "answer_distribution": {
                "A": 15,
                "B": 75,  # Correct answer
                "C": 10
            }
        }
        
        # Make the request
        response = client.get("/questions/q1/statistics")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["total_attempts"] == 100
        assert data["correct_answers"] == 75
        assert data["accuracy_rate"] == 0.75
        assert "answer_distribution" in data
        assert data["answer_distribution"]["B"] == 75
        
        # Check that the service was called correctly
        mock_learning_service.get_question_statistics.assert_called_once_with("q1")
    
    def test_generate_study_plan(self, client, mock_learning_service):
        """Test generating a personalized study plan"""
        # Configure the mock service
        mock_learning_service.generate_study_plan.return_value = {
            "recommended_topics": [
                {
                    "topic_id": "topic_3",
                    "topic_name": "Trigonometry",
                    "performance_score": 0.2,
                    "recommended_question_count": 10,
                    "priority": "high"
                },
                {
                    "topic_id": "topic_2",
                    "topic_name": "Geometry",
                    "performance_score": 0.5,
                    "recommended_question_count": 5,
                    "priority": "medium"
                },
                {
                    "topic_id": "topic_1",
                    "topic_name": "Algebra",
                    "performance_score": 0.9,
                    "recommended_question_count": 2,
                    "priority": "low"
                }
            ],
            "estimated_study_time_minutes": 90,
            "recommendations": [
                "Focus on improving your Trigonometry skills",
                "Practice Geometry problems regularly",
                "Review Algebra concepts occasionally"
            ]
        }
        
        # Make the request
        response = client.get("/questions/study-plan")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "recommended_topics" in data
        assert len(data["recommended_topics"]) == 3
        assert data["recommended_topics"][0]["topic_id"] == "topic_3"
        assert data["recommended_topics"][0]["priority"] == "high"
        assert "recommendations" in data
        
        # Check that the service was called correctly
        mock_learning_service.generate_study_plan.assert_called_once_with("user_123")
    
    def test_get_learning_progress(self, client, mock_learning_service):
        """Test getting user's learning progress over time"""
        # Configure the mock service
        mock_learning_service.get_learning_progress.return_value = {
            "sessions_by_date": {
                "2025-04-30": {"count": 1, "average_score": 0.7},
                "2025-05-01": {"count": 2, "average_score": 0.8},
                "2025-05-02": {"count": 1, "average_score": 0.9}
            },
            "improvement_rate": 0.1,
            "total_time_spent_minutes": 120
        }
        
        # Make the request
        response = client.get("/questions/progress")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "sessions_by_date" in data
        assert len(data["sessions_by_date"]) == 3
        assert data["improvement_rate"] == 0.1
        
        # Check that the service was called correctly
        mock_learning_service.get_learning_progress.assert_called_once_with("user_123")