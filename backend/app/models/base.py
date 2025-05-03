"""
Base model definition for all domain entities
"""
from abc import ABC
import datetime
import uuid
from typing import Optional


class BaseModel(ABC):
    """Base model for all domain entities with common functionality"""
    
    def __init__(self, id: Optional[str] = None, 
                 created_at: Optional[datetime.datetime] = None,
                 updated_at: Optional[datetime.datetime] = None):
        """
        Initialize a base model with standard fields
        
        Args:
            id: Unique identifier, defaults to UUID if not provided
            created_at: Creation timestamp, defaults to current UTC time
            updated_at: Last update timestamp, defaults to current UTC time
        """
        self.id = id if id else str(uuid.uuid4())
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.UTC)
        self.updated_at = updated_at if updated_at else datetime.datetime.now(datetime.UTC)
    
    def update(self):
        """Update the updated_at timestamp to current UTC time"""
        self.updated_at = datetime.datetime.now(datetime.UTC)