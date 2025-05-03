"""
Tests for the transformer module that converts raw question data to the application model
"""
import pytest
from unittest.mock import patch

from backend.app.utils.pdf_processing.transformer import (
    map_question_type,
    assign_topic,
    transform_to_question_model,
    transform_questions_to_json
)
from backend.app.models.question import QuestionType


class TestTransformer:
    """Test suite for the transformer module"""
    
    def test_map_question_type(self):
        """Test mapping raw question types to QuestionType enum"""
        # Test mapping multiple choice
        assert map_question_type("multiple_choice") == QuestionType.MULTIPLE_CHOICE
        
        # Test mapping grid-in
        assert map_question_type("grid_in") == QuestionType.GRID_IN
        
        # Test mapping evidence-based
        assert map_question_type("evidence_based") == QuestionType.EVIDENCE_BASED
        
        # Test mapping reading comprehension
        assert map_question_type("reading_comprehension") == QuestionType.READING_COMPREHENSION
        
        # Test default fallback for unknown type
        assert map_question_type("unknown_type") == QuestionType.MULTIPLE_CHOICE
        
    @patch('backend.app.utils.pdf_processing.transformer.TOPIC_MAP', {
        "MATH": {
            "algebra": "algebra_topic_id",
            "geometry": "geometry_topic_id",
            "statistics": "statistics_topic_id",
            "problem_solving": "problem_solving_topic_id",
        },
        "READING_WRITING": {
            "reading_comprehension": "reading_comprehension_topic_id",
            "grammar": "grammar_topic_id",
            "vocabulary": "vocabulary_topic_id",
            "writing": "writing_topic_id",
        }
    })
    def test_assign_topic_math(self):
        """Test assigning topic IDs to math questions"""
        # Algebra question
        algebra_question = {
            "section": "MATH",
            "text": "Solve the equation 2x + 3 = 7 for x."
        }
        assert assign_topic(algebra_question) == "algebra_topic_id"
        
        # Geometry question
        geometry_question = {
            "section": "MATH",
            "text": "What is the area of a triangle with base 6 and height 8?"
        }
        assert assign_topic(geometry_question) == "geometry_topic_id"
        
        # Statistics question
        stats_question = {
            "section": "MATH",
            "text": "What is the probability of rolling a 6 on a fair six-sided die?"
        }
        assert assign_topic(stats_question) == "statistics_topic_id"
        
        # Default math question
        default_math_question = {
            "section": "MATH",
            "text": "A train travels from station A to station B in 2 hours."
        }
        assert assign_topic(default_math_question) == "problem_solving_topic_id"
        
    @patch('backend.app.utils.pdf_processing.transformer.TOPIC_MAP', {
        "MATH": {
            "algebra": "algebra_topic_id",
            "geometry": "geometry_topic_id",
            "statistics": "statistics_topic_id",
            "problem_solving": "problem_solving_topic_id",
        },
        "READING_WRITING": {
            "reading_comprehension": "reading_comprehension_topic_id",
            "grammar": "grammar_topic_id",
            "vocabulary": "vocabulary_topic_id",
            "writing": "writing_topic_id",
        }
    })
    def test_assign_topic_reading_writing(self):
        """Test assigning topic IDs to reading and writing questions"""
        # Reading comprehension question
        reading_question = {
            "section": "READING_WRITING",
            "text": "According to the passage, what does the author suggest?",
            "question_type": "reading_comprehension"
        }
        assert assign_topic(reading_question) == "reading_comprehension_topic_id"
        
        # Grammar question
        grammar_question = {
            "section": "READING_WRITING",
            "text": "Select the most appropriate punctuation for the underlined portion."
        }
        assert assign_topic(grammar_question) == "grammar_topic_id"
        
        # Vocabulary question
        vocab_question = {
            "section": "READING_WRITING",
            "text": "The meaning of 'verbose' is most similar to which of the following?"
        }
        assert assign_topic(vocab_question) == "vocabulary_topic_id"
        
        # Default writing question
        default_writing_question = {
            "section": "READING_WRITING",
            "text": "Which choice most effectively establishes the main idea of the paragraph?"
        }
        assert assign_topic(default_writing_question) == "writing_topic_id"
        
    def test_transform_to_question_model(self):
        """Test transforming raw question data to Question model"""
        # Sample multiple choice question
        raw_question = {
            "section": "MATH",
            "text": "What is 2+2?",
            "question_type": "multiple_choice",
            "options": [
                {"id": "A", "text": "3", "is_correct": False},
                {"id": "B", "text": "4", "is_correct": True},
                {"id": "C", "text": "5", "is_correct": False},
                {"id": "D", "text": "6", "is_correct": False}
            ],
            "topic_id": "test_topic_id",
            "answer": "B",
            "explanation": "2 + 2 = 4",
            "difficulty": 1
        }
        
        # Test with mocked topic_id
        with patch('backend.app.utils.pdf_processing.transformer.assign_topic', return_value="default_topic"):
            question = transform_to_question_model(raw_question)
            
            assert question.topic_id == "test_topic_id"  # Should use the provided topic_id
            assert question.question_type == QuestionType.MULTIPLE_CHOICE
            assert question.content == "What is 2+2?"
            assert question.answer == "B"
            assert question.explanation == "2 + 2 = 4"
            assert question.difficulty == 1
            assert len(question.options) == 4
            
    def test_transform_questions_to_json(self):
        """Test transforming extracted questions to JSON format"""
        # Sample questions
        questions = [
            {
                "text": "Question 1",
                "section": "MATH",
                "question_type": "multiple_choice",
                "options": [
                    {"id": "A", "text": "Option A"},
                    {"id": "B", "text": "Option B"}
                ],
                "answer": "A",
                "explanation": "Explanation 1"
            },
            {
                "text": "Question 2",
                "section": "READING_WRITING",
                "question_type": "reading_comprehension",
                "options": [],
                "context": "Sample passage text",
                "answer": "Sample answer",
                "explanation": "Explanation 2"
            }
        ]
        
        # Test with mocked topic assignment
        with patch('backend.app.utils.pdf_processing.transformer.assign_topic', return_value="mock_topic_id"):
            result = transform_questions_to_json(questions)
            
            assert len(result) == 2
            assert result[0]["text"] == "Question 1"
            assert result[0]["topic_id"] == "mock_topic_id"
            assert result[0]["section"] == "MATH"
            assert len(result[0]["options"]) == 2
            
            assert result[1]["text"] == "Question 2"
            assert result[1]["topic_id"] == "mock_topic_id"
            assert result[1]["section"] == "READING_WRITING"
            assert "context" in result[1]
            assert result[1]["context"] == "Sample passage text"