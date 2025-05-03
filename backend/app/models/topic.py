"""
Topic model for specific content areas within subjects
"""
from typing import Optional

from .base import BaseModel


class Topic(BaseModel):
    """
    Topic entity representing specific content areas within subjects
    Examples: Linear Equations, Reading Comprehension, Grammar Rules
    """
    
    def __init__(
        self,
        subject_id: str,
        name: str,
        description: str,
        difficulty_level: int = 1,
        **kwargs
    ):
        """
        Initialize a new topic
        
        Args:
            subject_id: ID of the parent subject
            name: Topic name
            description: Detailed description of the topic
            difficulty_level: Difficulty rating (1-5)
        """
        super().__init__(**kwargs)
        self.subject_id = subject_id
        self.name = name
        self.description = description
        self.difficulty_level = difficulty_level
        
        # Validate difficulty level
        if not 1 <= self.difficulty_level <= 5:
            raise ValueError("Difficulty level must be between 1 and 5")
    
    def __str__(self) -> str:
        return f"{self.name} (Level {self.difficulty_level})"