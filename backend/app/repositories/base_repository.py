"""
Base repository interface defining standard data access operations
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Dict, Any, Optional

from ..models.base import BaseModel

T = TypeVar('T', bound=BaseModel)


class Repository(Generic[T], ABC):
    """
    Base repository interface for all entity types
    Defines standard CRUD operations that all repositories must implement
    """
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """
        Get an entity by its ID
        
        Args:
            id: The unique identifier of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        pass
        
    @abstractmethod
    def list(self, filters: Dict[str, Any] = None, 
             page: int = 1, page_size: int = 20) -> List[T]:
        """
        List entities with optional filtering and pagination
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            List of entities matching the criteria
        """
        pass
        
    @abstractmethod
    def create(self, entity: T) -> T:
        """
        Create a new entity
        
        Args:
            entity: The entity to create
            
        Returns:
            The created entity with any auto-generated fields populated
        """
        pass
        
    @abstractmethod
    def update(self, entity: T) -> T:
        """
        Update an existing entity
        
        Args:
            entity: The entity to update
            
        Returns:
            The updated entity
        """
        pass
        
    @abstractmethod
    def delete(self, id: str) -> bool:
        """
        Delete an entity by its ID
        
        Args:
            id: The unique identifier of the entity
            
        Returns:
            True if the entity was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self, filters: Dict[str, Any] = None) -> int:
        """
        Count entities with optional filtering
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            
        Returns:
            Number of entities matching the criteria
        """
        pass