"""
Unit tests for the QuestionRepository implementation
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from app.repositories.question_repository import QuestionRepository
from app.infrastructure.repositories.sqlalchemy_question_repository import SQLAlchemyQuestionRepository
from app.infrastructure.database.models import QuestionModel, TopicModel
from app.models.question import Question, QuestionType


class TestSQLAlchemyQuestionRepository:
    """Tests for the SQLAlchemyQuestionRepository implementation"""
    
    @pytest.fixture
    def topic_model_instance(self, db_session):
        """Create a topic model instance for testing"""
        topic = TopicModel(
            id="topic_id_123",
            name="Algebra",
            description="Basic algebra concepts",
            subject_id="subject_id_123",
            difficulty_level=2,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(topic)
        db_session.commit()
        return topic
    
    @pytest.fixture
    def question_model_instance(self, topic_model_instance):
        """Create a sample SQLAlchemy question model instance"""
        return QuestionModel(
            id="question_id_123",
            topic_id=topic_model_instance.id,
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 2+2?",
            answer="B",
            explanation="Addition of 2 and 2 equals 4",
            difficulty=2,
            options=[
                {"id": "A", "text": "3"},
                {"id": "B", "text": "4"},
                {"id": "C", "text": "5"}
            ],
            tags=["math", "addition"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def question_domain_instance(self, topic_model_instance):
        """Create a sample question domain model instance"""
        return Question(
            id="question_id_123",
            topic_id=topic_model_instance.id,
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 2+2?",
            answer="B",
            explanation="Addition of 2 and 2 equals 4",
            difficulty=2,
            options=[
                {"id": "A", "text": "3"},
                {"id": "B", "text": "4"},
                {"id": "C", "text": "5"}
            ],
            tags=["math", "addition"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def test_get_by_id(self, db_session, question_model_instance):
        """Test retrieving a question by ID"""
        # Add a question to the session
        db_session.add(question_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyQuestionRepository(db_session)
        
        # Retrieve the question
        question = repo.get_by_id("question_id_123")
        
        # Check that question was retrieved correctly
        assert question is not None
        assert question.id == "question_id_123"
        assert question.content == "What is 2+2?"
        assert question.answer == "B"
        assert question.question_type == QuestionType.MULTIPLE_CHOICE
        assert question.difficulty == 2
        assert len(question.options) == 3
        assert question.tags == ["math", "addition"]
    
    def test_get_by_topic(self, db_session, question_model_instance, topic_model_instance):
        """Test retrieving questions by topic"""
        # Add a question to the session
        db_session.add(question_model_instance)
        
        # Add another question with the same topic
        second_question = QuestionModel(
            id="question_id_456",
            topic_id=topic_model_instance.id,
            question_type=QuestionType.SHORT_ANSWER,
            content="What is 3+3?",
            answer="6",
            explanation="Addition of 3 and 3 equals 6",
            difficulty=1,
            tags=["math", "addition"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(second_question)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyQuestionRepository(db_session)
        
        # Get questions for the topic
        questions = repo.get_by_topic(topic_model_instance.id)
        
        # Check that both questions were retrieved
        assert len(questions) == 2
        question_ids = {q.id for q in questions}
        assert "question_id_123" in question_ids
        assert "question_id_456" in question_ids
    
    def test_get_by_topic_with_difficulty(self, db_session, question_model_instance, topic_model_instance):
        """Test retrieving questions by topic and difficulty"""
        # Add a question to the session
        db_session.add(question_model_instance)  # difficulty = 2
        
        # Add another question with the same topic but different difficulty
        second_question = QuestionModel(
            id="question_id_456",
            topic_id=topic_model_instance.id,
            question_type=QuestionType.SHORT_ANSWER,
            content="What is 3+3?",
            answer="6",
            explanation="Addition of 3 and 3 equals 6",
            difficulty=3,  # Different difficulty
            tags=["math", "addition"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(second_question)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyQuestionRepository(db_session)
        
        # Get questions for the topic with difficulty=2
        questions = repo.get_by_topic(topic_model_instance.id, difficulty=2)
        
        # Check that only the question with difficulty=2 was retrieved
        assert len(questions) == 1
        assert questions[0].id == "question_id_123"
        assert questions[0].difficulty == 2
    
    def test_get_random_questions(self, db_session, question_model_instance):
        """Test retrieving random questions"""
        # Add the first question to the session
        db_session.add(question_model_instance)
        
        # Add more questions with different attributes
        for i in range(10):
            q = QuestionModel(
                id=f"question_id_{i+1000}",
                topic_id="topic_id_123",
                question_type=QuestionType.MULTIPLE_CHOICE,
                content=f"Question {i}?",
                answer=f"Answer {i}",
                explanation=f"Explanation {i}",
                difficulty=(i % 5) + 1,  # Difficulties 1-5
                tags=["math"]
            )
            db_session.add(q)
        
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyQuestionRepository(db_session)
        
        # Get 5 random questions with difficulty range 1-3
        questions = repo.get_random_questions(
            topic_ids=["topic_id_123"],
            count=5,
            difficulty_range=(1, 3)
        )
        
        # Check that we got the right number of questions
        assert len(questions) == 5
        
        # Check that all questions have the right difficulty range
        for q in questions:
            assert 1 <= q.difficulty <= 3
            assert q.topic_id == "topic_id_123"
    
    def test_get_questions_by_tags(self, db_session, question_model_instance):
        """Test retrieving questions by tags"""
        # Add the first question to the session with tags ["math", "addition"]
        db_session.add(question_model_instance)
        
        # Add another question with different tags
        second_question = QuestionModel(
            id="question_id_456",
            topic_id="topic_id_123",
            question_type=QuestionType.SHORT_ANSWER,
            content="What is x in 2x = 10?",
            answer="5",
            explanation="Divide both sides by 2",
            difficulty=3,
            tags=["math", "algebra"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(second_question)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyQuestionRepository(db_session)
        
        # Get questions with tag "addition"
        questions = repo.get_questions_by_tags(tags=["addition"])
        
        # Check that only the question with "addition" tag was retrieved
        assert len(questions) == 1
        assert questions[0].id == "question_id_123"
        
        # Get questions with tag "algebra"
        questions = repo.get_questions_by_tags(tags=["algebra"])
        
        # Check that only the question with "algebra" tag was retrieved
        assert len(questions) == 1
        assert questions[0].id == "question_id_456"
        
        # Get questions with tag "math"
        questions = repo.get_questions_by_tags(tags=["math"])
        
        # Check that both questions were retrieved (both have "math" tag)
        assert len(questions) == 2
    
    def test_get_total_by_topic(self, db_session, question_model_instance, topic_model_instance):
        """Test counting questions by topic"""
        # Add the first question to the session
        db_session.add(question_model_instance)
        
        # Add another question with the same topic
        second_question = QuestionModel(
            id="question_id_456",
            topic_id=topic_model_instance.id,
            question_type=QuestionType.SHORT_ANSWER,
            content="What is 3+3?",
            answer="6",
            explanation="Addition of 3 and 3 equals 6",
            difficulty=1,
            tags=["math", "addition"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(second_question)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyQuestionRepository(db_session)
        
        # Get count of questions for the topic
        count = repo.get_total_by_topic(topic_model_instance.id)
        
        # Check that count is correct
        assert count == 2
    
    def test_get_total_by_difficulty(self, db_session, question_model_instance):
        """Test counting questions by difficulty"""
        # Add the first question to the session (difficulty=2)
        db_session.add(question_model_instance)
        
        # Add two more questions with difficulty=3
        for i in range(2):
            q = QuestionModel(
                id=f"question_id_{i+500}",
                topic_id="topic_id_123",
                question_type=QuestionType.MULTIPLE_CHOICE,
                content=f"Question {i}?",
                answer=f"Answer {i}",
                explanation=f"Explanation {i}",
                difficulty=3,
                tags=["math"]
            )
            db_session.add(q)
        
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyQuestionRepository(db_session)
        
        # Get count of questions for difficulty=2
        count_diff_2 = repo.get_total_by_difficulty(2)
        
        # Check that count is correct
        assert count_diff_2 == 1
        
        # Get count of questions for difficulty=3
        count_diff_3 = repo.get_total_by_difficulty(3)
        
        # Check that count is correct
        assert count_diff_3 == 2
    
    def test_update_question_difficulty(self, db_session, question_model_instance):
        """Test updating a question's difficulty"""
        # Add the question to the session
        db_session.add(question_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyQuestionRepository(db_session)
        
        # Update the difficulty
        result = repo.update_question_difficulty("question_id_123", 4)
        
        # Check that update was successful
        assert result is True
        
        # Verify difficulty was updated
        question = repo.get_by_id("question_id_123")
        assert question.difficulty == 4