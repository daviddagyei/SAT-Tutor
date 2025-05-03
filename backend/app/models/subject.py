"""
Subject model for categorizing SAT content areas
"""
from typing import Optional

from .base import BaseModel


class Subject(BaseModel):
    """
    Subject entity representing main SAT content areas (Math, Reading, Writing)
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        icon: str = "book",
        **kwargs
    ):
        """
        Initialize a new subject
        
        Args:
            name: Subject name (Math, Reading, Writing)
            description: Detailed description of the subject
            icon: Icon identifier for the subject
        """
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.icon = icon
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description[:50]}{'...' if len(self.description) > 50 else ''}"