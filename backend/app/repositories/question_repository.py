"""
Question repository interface for question data access operations
"""
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from .base_repository import Repository
from ..models.question import Question, QuestionType


class QuestionRepository(Repository[Question]):
    """
    Repository interface for Question entity with specialized methods
    """
    
    def get_by_topic(self, topic_id: str, difficulty: Optional[int] = None, 
                   count: int = 10) -> List[Question]:
        """
        Get questions for a specific topic with optional difficulty filter
        
        Args:
            topic_id: The ID of the topic
            difficulty: Optional difficulty level filter
            count: Maximum number of questions to return
            
        Returns:
            List of questions matching criteria
        """
        pass
    
    def get_random_questions(self, subject_ids: List[str] = None, topic_ids: List[str] = None,
                           count: int = 10, difficulty_range: Tuple[int, int] = (1, 5),
                           question_type: Optional[QuestionType] = None) -> List[Question]:
        """
        Get random questions based on criteria
        
        Args:
            subject_ids: Optional list of subject IDs to include
            topic_ids: Optional list of topic IDs to include
            count: Number of questions to return
            difficulty_range: Range of difficulty levels (min, max)
            question_type: Optional specific question type
            
        Returns:
            List of random questions matching criteria
        """
        pass
    
    def get_questions_by_tags(self, tags: List[str], count: int = 10) -> List[Question]:
        """
        Get questions with specific tags
        
        Args:
            tags: List of tags to filter by
            count: Maximum number of questions to return
            
        Returns:
            List of questions with the specified tags
        """
        pass
    
    def get_total_by_topic(self, topic_id: str) -> int:
        """
        Count total questions for a specific topic
        
        Args:
            topic_id: The ID of the topic
            
        Returns:
            Number of questions for the topic
        """
        pass
    
    def get_total_by_difficulty(self, difficulty: int) -> int:
        """
        Count total questions with a specific difficulty level
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            Number of questions with the specified difficulty
        """
        pass
    
    def update_question_difficulty(self, question_id: str, new_difficulty: int) -> bool:
        """
        Update a question's difficulty rating
        
        Args:
            question_id: ID of the question
            new_difficulty: New difficulty rating
            
        Returns:
            True if updated successfully, False otherwise
        """
        pass