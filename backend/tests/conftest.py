"""
Test configuration and shared fixtures for the SAT Tutor backend
"""
import os
import pytest
from datetime import datetime
from typing import Dict, Generator, Any
from unittest.mock import MagicMock, patch

from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import sessionmaker, Session  # type: ignore

from app.models.user import User, UserRole
from app.models.profile import Profile
from app.models.question import Question, QuestionType
from app.models.practice_session import PracticeSession
from app.models.subject import Subject
from app.models.topic import Topic
from app.repositories.user_repository import UserRepository
from app.repositories.question_repository import QuestionRepository
from app.infrastructure.database.session import Base


# Use an in-memory SQLite database for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_engine():
    """Create a SQLAlchemy engine for testing"""
    engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create a new database session for testing"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_user_repository():
    """Create a mocked user repository"""
    return MagicMock(spec=UserRepository)


@pytest.fixture
def mock_question_repository():
    """Create a mocked question repository"""
    return MagicMock(spec=QuestionRepository)


@pytest.fixture
def test_user():
    """Create a test user for testing"""
    return User(
        email="test@example.com",
        hashed_password="hashed_password123",
        full_name="Test User",
        role=UserRole.STUDENT,
        is_email_confirmed=True,
        id="user_id_1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def test_admin_user():
    """Create a test admin user for testing"""
    return User(
        email="admin@example.com",
        hashed_password="admin_hashed_password",
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_email_confirmed=True,
        id="admin_id_1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def test_profile():
    """Create a test profile for testing"""
    return Profile(
        user_id="user_id_1",
        bio="Test bio",
        study_goals={"math_score": 700, "verbal_score": 650},
        achievements=[{"name": "First Login", "date": datetime.utcnow().isoformat()}],
        study_streak=3,
        sat_target_score=1400,
        current_estimated_score={"math": 650, "verbal": 600},
        id="profile_id_1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def test_subject():
    """Create a test subject for testing"""
    return Subject(
        name="Mathematics",
        description="Math section of the SAT",
        icon="calculator",
        id="subject_id_1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def test_topic():
    """Create a test topic for testing"""
    return Topic(
        subject_id="subject_id_1",
        name="Algebra",
        description="Linear equations and inequalities",
        difficulty_level=3,
        id="topic_id_1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def test_question():
    """Create a test question for testing"""
    return Question(
        topic_id="topic_id_1",
        question_type=QuestionType.MULTIPLE_CHOICE,
        content="What is the value of x in the equation 2x + 5 = 15?",
        answer="5",
        explanation="Subtract 5 from both sides: 2x = 10. Divide both sides by 2: x = 5.",
        difficulty=3,
        options=[
            {"id": "A", "text": "4"},
            {"id": "B", "text": "5"},
            {"id": "C", "text": "6"},
            {"id": "D", "text": "7"}
        ],
        tags=["algebra", "linear-equations"],
        id="question_id_1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def test_practice_session():
    """Create a test practice session for testing"""
    return PracticeSession(
        user_id="user_id_1",
        topic_ids=["topic_id_1"],
        question_ids=["question_id_1", "question_id_2"],
        start_time=datetime.utcnow(),
        id="session_id_1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )