"""
Question model for practice and test content
"""
from enum import Enum
from typing import List, Dict, Any, Optional

from .base import BaseModel


class QuestionType(Enum):
    """Types of questions in the SAT"""
    MULTIPLE_CHOICE = "multiple_choice"
    GRID_IN = "grid_in"
    EVIDENCE_BASED = "evidence_based"
    READING_COMPREHENSION = "reading_comprehension"


class Question(BaseModel):
    """
    Question entity representing practice or test questions
    """
    
    def __init__(
        self,
        topic_id: str,
        question_type: QuestionType,
        content: str,
        answer: str,
        explanation: str,
        difficulty: int = 3,
        options: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize a new question
        
        Args:
            topic_id: ID of the associated topic
            question_type: Type of question (multiple choice, grid-in, etc.)
            content: Question text/prompt
            answer: Correct answer
            explanation: Detailed explanation of the solution
            difficulty: Difficulty rating (1-5)
            options: For multiple choice questions, list of options including text and identifier
            tags: List of tags for categorizing and filtering questions
        """
        super().__init__(**kwargs)
        self.topic_id = topic_id
        self.question_type = question_type
        self.content = content
        self.answer = answer
        self.explanation = explanation
        self.difficulty = difficulty
        self.options = options or []
        self.tags = tags or []
        
        # Validate difficulty
        if not 1 <= self.difficulty <= 5:
            raise ValueError("Difficulty must be between 1 and 5")
        
        # Ensure options are provided for multiple choice questions
        if self.question_type == QuestionType.MULTIPLE_CHOICE and not self.options:
            raise ValueError("Multiple choice questions must have options")
    
    def is_correct_answer(self, student_answer: str) -> bool:
        """
        Check if the student's answer is correct
        
        Args:
            student_answer: The student's submitted answer
            
        Returns:
            True if the answer is correct, False otherwise
        """
        # For multiple choice, just compare the option identifiers
        if self.question_type == QuestionType.MULTIPLE_CHOICE:
            return student_answer.strip().lower() == self.answer.strip().lower()
        
        # For grid-in questions, allow for equivalent numerical answers
        elif self.question_type == QuestionType.GRID_IN:
            try:
                return abs(float(student_answer) - float(self.answer)) < 0.000001
            except ValueError:
                return False
        
        # For other question types
        else:
            return student_answer.strip().lower() == self.answer.strip().lower()
    
    def get_hint(self) -> str:
        """
        Get a hint for the question based on the explanation
        
        Returns:
            A hint extracted from the explanation
        """
        # Simple implementation - return first 25% of explanation
        # In a real application, hints would be more sophisticated
        hint_length = max(20, len(self.explanation) // 4)
        return self.explanation[:hint_length] + "..."