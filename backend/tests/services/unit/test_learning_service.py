"""
Unit tests for the LearningService
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.models.user import User, UserRole
from app.models.question import Question, QuestionType
from app.models.practice_session import PracticeSession
from app.models.topic import Topic
from app.services.learning_service import LearningService


class TestLearningService:
    """Tests for the LearningService"""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository for testing"""
        return MagicMock()
    
    @pytest.fixture
    def mock_question_repository(self):
        """Mock question repository for testing"""
        return MagicMock()
    
    @pytest.fixture
    def learning_service(self, mock_user_repository, mock_question_repository):
        """Create a LearningService instance for testing"""
        return LearningService(mock_user_repository, mock_question_repository)
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing"""
        return User(
            id="user_123",
            email="student@example.com",
            hashed_password="hashed_pwd",
            full_name="Student User",
            role=UserRole.STUDENT,
            is_email_confirmed=True
        )
    
    @pytest.fixture
    def sample_topics(self):
        """Create sample topics for testing"""
        return [
            Topic(
                id="topic_1",
                name="Algebra",
                description="Basic algebra",
                subject_id="math_subject",
                difficulty_level=2
            ),
            Topic(
                id="topic_2",
                name="Geometry",
                description="Basic geometry",
                subject_id="math_subject",
                difficulty_level=3
            )
        ]
    
    @pytest.fixture
    def sample_questions(self):
        """Create sample questions for testing"""
        return [
            Question(
                id="q1",
                topic_id="topic_1",
                question_type=QuestionType.MULTIPLE_CHOICE,
                content="What is 2+2?",
                answer="B",
                explanation="Addition",
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
            ),
            Question(
                id="q3",
                topic_id="topic_2",
                question_type=QuestionType.MULTIPLE_CHOICE,
                content="What is a triangle?",
                answer="A",
                explanation="Basic geometry",
                options=[
                    {"id": "A", "text": "3 sides"},
                    {"id": "B", "text": "4 sides"},
                    {"id": "C", "text": "5 sides"}
                ],
                difficulty=3
            )
        ]
    
    def test_create_practice_session(self, learning_service, mock_question_repository, sample_user, sample_topics, sample_questions):
        """Test creating a practice session"""
        # Configure mock repository
        mock_question_repository.get_random_questions.return_value = sample_questions[:2]
        
        # Create practice session
        session = learning_service.create_practice_session(
            user_id=sample_user.id,
            topic_ids=[sample_topics[0].id],
            question_count=2,
            difficulty_range=(1, 3)
        )
        
        # Check that session was created correctly
        assert session is not None
        assert session.user_id == sample_user.id
        assert session.topic_ids == [sample_topics[0].id]
        assert len(session.question_ids) == 2
        assert session.completed is False
        assert session.score is None
        
        # Check that repository method was called correctly
        mock_question_repository.get_random_questions.assert_called_once_with(
            topic_ids=[sample_topics[0].id],
            count=2,
            difficulty_range=(1, 3)
        )
    
    def test_get_practice_session(self, learning_service, mock_user_repository, sample_user):
        """Test getting a practice session by ID"""
        # Create session
        session = PracticeSession(
            id="session_123",
            user_id=sample_user.id,
            topic_ids=["topic_1"],
            question_ids=["q1", "q2"],
            start_time=datetime.utcnow()
        )
        
        # Configure mock repository
        mock_user_repository.get_session_by_id = MagicMock(return_value=session)
        
        # Get session
        retrieved_session = learning_service.get_practice_session("session_123")
        
        # Check that session was retrieved correctly
        assert retrieved_session is not None
        assert retrieved_session.id == "session_123"
        assert retrieved_session.user_id == sample_user.id
        
        # Check that repository method was called correctly
        mock_user_repository.get_session_by_id.assert_called_once_with("session_123")
    
    def test_complete_practice_session(self, learning_service, mock_user_repository):
        """Test completing a practice session"""
        # Create session
        session = PracticeSession(
            id="session_123",
            user_id="user_123",
            topic_ids=["topic_1"],
            question_ids=["q1", "q2"]
        )
        
        # Add answers
        session.add_answer("q1", "B", True, 30)
        session.add_answer("q2", "C", True, 40)
        
        # Configure mock repository
        mock_user_repository.get_session_by_id = MagicMock(return_value=session)
        mock_user_repository.update_session = MagicMock(return_value=session)
        
        # Complete session
        completed_session = learning_service.complete_practice_session("session_123")
        
        # Check that session was marked as completed
        assert completed_session is not None
        assert completed_session.completed is True
        assert completed_session.score == 1.0  # 2 out of 2 correct
        assert completed_session.end_time is not None
        
        # Check that repository methods were called correctly
        mock_user_repository.get_session_by_id.assert_called_once_with("session_123")
        mock_user_repository.update_session.assert_called_once()
    
    def test_answer_question_correct(self, learning_service, mock_user_repository, mock_question_repository):
        """Test answering a question correctly"""
        # Create session
        session = PracticeSession(
            id="session_123",
            user_id="user_123",
            topic_ids=["topic_1"],
            question_ids=["q1", "q2"]
        )
        
        # Create question
        question = Question(
            id="q1",
            topic_id="topic_1",
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 2+2?",
            answer="B",
            options=[
                {"id": "A", "text": "3"},
                {"id": "B", "text": "4"},
                {"id": "C", "text": "5"}
            ]
        )
        
        # Configure mock repositories
        mock_user_repository.get_session_by_id = MagicMock(return_value=session)
        mock_user_repository.update_session = MagicMock(return_value=session)
        mock_question_repository.get_by_id = MagicMock(return_value=question)
        
        # Answer the question
        result = learning_service.answer_question(
            session_id="session_123",
            question_id="q1",
            answer="B",
            time_taken_seconds=30
        )
        
        # Check that answer was recorded correctly
        assert result["is_correct"] is True
        assert result["correct_answer"] == "B"
        assert result["explanation"] is not None
        
        # Check that repository methods were called correctly
        mock_user_repository.get_session_by_id.assert_called_once_with("session_123")
        mock_question_repository.get_by_id.assert_called_once_with("q1")
        mock_user_repository.update_session.assert_called_once()
        
        # Check that answer was added to session
        assert len(session.user_answers) == 1
        answer = session.user_answers[0]
        assert answer["question_id"] == "q1"
        assert answer["answer"] == "B"
        assert answer["is_correct"] is True
        assert answer["time_taken_seconds"] == 30
    
    def test_answer_question_incorrect(self, learning_service, mock_user_repository, mock_question_repository):
        """Test answering a question incorrectly"""
        # Create session
        session = PracticeSession(
            id="session_123",
            user_id="user_123",
            topic_ids=["topic_1"],
            question_ids=["q1", "q2"]
        )
        
        # Create question
        question = Question(
            id="q1",
            topic_id="topic_1",
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 2+2?",
            answer="B",
            explanation="Addition",
            options=[
                {"id": "A", "text": "3"},
                {"id": "B", "text": "4"},
                {"id": "C", "text": "5"}
            ]
        )
        
        # Configure mock repositories
        mock_user_repository.get_session_by_id = MagicMock(return_value=session)
        mock_user_repository.update_session = MagicMock(return_value=session)
        mock_question_repository.get_by_id = MagicMock(return_value=question)
        
        # Answer the question incorrectly
        result = learning_service.answer_question(
            session_id="session_123",
            question_id="q1",
            answer="A",  # Wrong answer
            time_taken_seconds=30
        )
        
        # Check that answer was recorded correctly
        assert result["is_correct"] is False
        assert result["correct_answer"] == "B"
        assert result["explanation"] == "Addition"
        
        # Check that repository methods were called correctly
        mock_user_repository.get_session_by_id.assert_called_once_with("session_123")
        mock_question_repository.get_by_id.assert_called_once_with("q1")
        mock_user_repository.update_session.assert_called_once()
        
        # Check that answer was added to session
        assert len(session.user_answers) == 1
        answer = session.user_answers[0]
        assert answer["question_id"] == "q1"
        assert answer["answer"] == "A"
        assert answer["is_correct"] is False
        assert answer["time_taken_seconds"] == 30
    
    def test_get_user_statistics(self, learning_service, mock_user_repository, sample_user):
        """Test getting user learning statistics"""
        # Create completed sessions with different scores
        yesterday = datetime.utcnow() - timedelta(days=1)
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        
        sessions = [
            # Recent perfect session
            PracticeSession(
                id="session_1",
                user_id=sample_user.id,
                topic_ids=["topic_1"],
                question_ids=["q1", "q2"],
                start_time=datetime.utcnow() - timedelta(hours=2),
                end_time=datetime.utcnow() - timedelta(hours=1),
                completed=True,
                score=1.0,  # 100%
                user_answers=[
                    {"question_id": "q1", "answer": "B", "is_correct": True, "time_taken_seconds": 30},
                    {"question_id": "q2", "answer": "C", "is_correct": True, "time_taken_seconds": 45}
                ]
            ),
            # Yesterday's session with 50% score
            PracticeSession(
                id="session_2",
                user_id=sample_user.id,
                topic_ids=["topic_2"],
                question_ids=["q3", "q4"],
                start_time=yesterday - timedelta(hours=3),
                end_time=yesterday - timedelta(hours=2),
                completed=True,
                score=0.5,  # 50%
                user_answers=[
                    {"question_id": "q3", "answer": "A", "is_correct": True, "time_taken_seconds": 60},
                    {"question_id": "q4", "answer": "B", "is_correct": False, "time_taken_seconds": 90}
                ]
            ),
            # Two days ago session with 0% score
            PracticeSession(
                id="session_3",
                user_id=sample_user.id,
                topic_ids=["topic_1", "topic_2"],
                question_ids=["q5", "q6"],
                start_time=two_days_ago - timedelta(hours=5),
                end_time=two_days_ago - timedelta(hours=4),
                completed=True,
                score=0.0,  # 0%
                user_answers=[
                    {"question_id": "q5", "answer": "C", "is_correct": False, "time_taken_seconds": 45},
                    {"question_id": "q6", "answer": "B", "is_correct": False, "time_taken_seconds": 50}
                ]
            )
        ]
        
        # Configure mock repository
        mock_user_repository.get_completed_sessions_for_user = MagicMock(return_value=sessions)
        
        # Get statistics
        stats = learning_service.get_user_statistics(sample_user.id)
        
        # Check that repository method was called correctly
        mock_user_repository.get_completed_sessions_for_user.assert_called_once_with(sample_user.id)
        
        # Check statistics
        assert stats is not None
        assert stats["total_sessions"] == 3
        assert stats["total_questions"] == 6
        assert stats["correct_answers"] == 3
        assert stats["average_score"] == 0.5  # (1.0 + 0.5 + 0.0) / 3
        assert stats["average_time_per_question"] == 53.33  # (30+45+60+90+45+50) / 6 = 320/6
        
        # Check topic statistics
        assert "topic_1" in stats["topic_statistics"]
        assert "topic_2" in stats["topic_statistics"]
        
        # Topic 1 should have 4 questions (from session 1 and 3)
        topic1_stats = stats["topic_statistics"]["topic_1"]
        assert topic1_stats["total_questions"] == 4
        assert topic1_stats["correct_answers"] == 2
        assert topic1_stats["average_score"] == 0.5  # (1.0 + 0.0) / 2
        
        # Topic 2 should have 4 questions (from session 2 and 3)
        topic2_stats = stats["topic_statistics"]["topic_2"]
        assert topic2_stats["total_questions"] == 4
        assert topic2_stats["correct_answers"] == 1
        assert topic2_stats["average_score"] == 0.25  # (0.5 + 0.0) / 2
    
    def test_get_question_statistics(self, learning_service, mock_question_repository):
        """Test getting statistics for a specific question"""
        # Create mock session data with answers for the question
        question_answers = [
            {"session_id": "s1", "answer": "B", "is_correct": True, "time_taken_seconds": 30},
            {"session_id": "s2", "answer": "A", "is_correct": False, "time_taken_seconds": 45},
            {"session_id": "s3", "answer": "B", "is_correct": True, "time_taken_seconds": 35},
            {"session_id": "s4", "answer": "C", "is_correct": False, "time_taken_seconds": 60}
        ]
        
        # Configure mock repository
        mock_question_repository.get_answers_for_question = MagicMock(return_value=question_answers)
        
        # Get statistics
        stats = learning_service.get_question_statistics("q1")
        
        # Check that repository method was called correctly
        mock_question_repository.get_answers_for_question.assert_called_once_with("q1")
        
        # Check statistics
        assert stats is not None
        assert stats["total_attempts"] == 4
        assert stats["correct_answers"] == 2
        assert stats["accuracy_rate"] == 0.5  # 2 out of 4 correct
        assert stats["average_time"] == 42.5  # (30+45+35+60) / 4
        
        # Check answer distribution
        assert stats["answer_distribution"]["A"] == 1
        assert stats["answer_distribution"]["B"] == 2
        assert stats["answer_distribution"]["C"] == 1
    
    def test_generate_study_plan(self, learning_service, mock_question_repository, mock_user_repository, sample_user):
        """Test generating a personalized study plan"""
        # Create mock topic performance data
        topic_performance = {
            "topic_1": {"score": 0.9, "total_questions": 20},  # Strong topic
            "topic_2": {"score": 0.5, "total_questions": 15},  # Moderate topic
            "topic_3": {"score": 0.2, "total_questions": 10}   # Weak topic
        }
        
        # Configure mock repositories
        mock_user_repository.get_topic_performance = MagicMock(return_value=topic_performance)
        mock_question_repository.get_total_by_topic = MagicMock(return_value=50)  # For any topic
        
        # Generate study plan
        plan = learning_service.generate_study_plan(sample_user.id)
        
        # Check that repository methods were called correctly
        mock_user_repository.get_topic_performance.assert_called_once_with(sample_user.id)
        
        # Check study plan
        assert plan is not None
        assert len(plan["recommended_topics"]) == 3
        
        # Topics should be ordered by performance (worst first)
        assert plan["recommended_topics"][0]["topic_id"] == "topic_3"
        assert plan["recommended_topics"][1]["topic_id"] == "topic_2"
        assert plan["recommended_topics"][2]["topic_id"] == "topic_1"
        
        # Check that each topic has appropriate recommendations
        weak_topic = plan["recommended_topics"][0]
        assert weak_topic["recommended_question_count"] > plan["recommended_topics"][1]["recommended_question_count"]
        assert weak_topic["performance_score"] == 0.2
        assert weak_topic["priority"] == "high"
        
        strong_topic = plan["recommended_topics"][2]
        assert strong_topic["performance_score"] == 0.9
        assert strong_topic["priority"] == "low"