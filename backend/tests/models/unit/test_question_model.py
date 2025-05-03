"""
Unit tests for the Question model
"""
import pytest
from datetime import datetime

from app.models.question import Question, QuestionType


class TestQuestionModel:
    """Tests for the Question model"""

    def test_init_with_required_values(self):
        """Test that Question initializes correctly with required values"""
        options = [
            {"id": "A", "text": "3"},
            {"id": "B", "text": "4"},
            {"id": "C", "text": "5"}
        ]
        
        question = Question(
            topic_id="topic_123",
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 2+2?",
            answer="4",
            explanation="Addition of 2 and 2",
            options=options
        )
        
        # Check required fields
        assert question.topic_id == "topic_123"
        assert question.question_type == QuestionType.MULTIPLE_CHOICE
        assert question.content == "What is 2+2?"
        assert question.answer == "4"
        assert question.explanation == "Addition of 2 and 2"
        
        # Check default values
        assert question.difficulty == 3  # Default difficulty
        assert question.options == options
        assert question.tags == []

    def test_init_with_all_values(self):
        """Test that Question initializes correctly with all values provided"""
        options = [
            {"id": "A", "text": "3"},
            {"id": "B", "text": "4"},
            {"id": "C", "text": "5"}
        ]
        
        question = Question(
            topic_id="topic_123",
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 2+2?",
            answer="B",
            explanation="Addition of 2 and 2",
            difficulty=2,
            options=options,
            tags=["math", "addition"]
        )
        
        # Check all fields
        assert question.topic_id == "topic_123"
        assert question.question_type == QuestionType.MULTIPLE_CHOICE
        assert question.content == "What is 2+2?"
        assert question.answer == "B"
        assert question.explanation == "Addition of 2 and 2"
        assert question.difficulty == 2
        assert question.options == options
        assert question.tags == ["math", "addition"]

    def test_is_correct_answer_multiple_choice(self):
        """Test correct answer checking for multiple choice questions"""
        options = [
            {"id": "A", "text": "3"},
            {"id": "B", "text": "4"},
            {"id": "C", "text": "5"}
        ]
        
        question = Question(
            topic_id="topic_123",
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 2+2?",
            answer="B",
            explanation="Addition of 2 and 2",
            options=options
        )
        
        # Test with correct answer (exact match)
        assert question.is_correct_answer("B") is True
        
        # Test with correct answer (case insensitive)
        assert question.is_correct_answer("b") is True
        
        # Test with incorrect answers
        assert question.is_correct_answer("A") is False
        assert question.is_correct_answer("C") is False
        assert question.is_correct_answer("") is False
        assert question.is_correct_answer("D") is False

    def test_is_correct_answer_grid_in(self):
        """Test correct answer checking for grid-in questions"""
        question = Question(
            topic_id="topic_123",
            question_type=QuestionType.GRID_IN,
            content="What is 5 + 7?",
            answer="12",
            explanation="Basic addition of 5 and 7 equals 12"
        )
        
        # Test with correct answer (exact match)
        assert question.is_correct_answer("12") is True
        
        # Test with different formatting but same value
        assert question.is_correct_answer("12.0") is True
        assert question.is_correct_answer("12.00") is True
        assert question.is_correct_answer("012") is True
        
        # Test with incorrect answers
        assert question.is_correct_answer("13") is False
        assert question.is_correct_answer("") is False
        assert question.is_correct_answer("twelve") is False

    def test_is_correct_answer_numerical(self):
        """Test correct answer checking for numerical grid-in questions"""
        question = Question(
            topic_id="topic_123",
            question_type=QuestionType.GRID_IN,
            content="What is the value of π rounded to 2 decimal places?",
            answer="3.14",
            explanation="π is approximately 3.14159..."
        )
        
        # Test with correct answer (exact match)
        assert question.is_correct_answer("3.14") is True
        
        # Test with different formatting but same value
        assert question.is_correct_answer("3.140") is True
        assert question.is_correct_answer("03.14") is True
        
        # Test with incorrect answers
        assert question.is_correct_answer("3.15") is False
        assert question.is_correct_answer("3") is False
        assert question.is_correct_answer("") is False

    def test_get_hint(self):
        """Test getting a hint for a question"""
        options = [
            {"id": "A", "text": "3"},
            {"id": "B", "text": "4"},
            {"id": "C", "text": "5"}
        ]
        
        question = Question(
            topic_id="topic_123",
            question_type=QuestionType.MULTIPLE_CHOICE,
            content="What is 2+2?",
            answer="4",
            explanation="Addition of 2 and 2",
            options=options
        )
        
        # Since this is a simple implementation, we're just testing
        # that the method returns a non-empty string
        hint = question.get_hint()
        assert isinstance(hint, str)
        assert len(hint) > 0