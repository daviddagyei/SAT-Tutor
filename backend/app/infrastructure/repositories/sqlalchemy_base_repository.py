"""
Base SQLAlchemy repository implementation
"""
from typing import TypeVar, Generic, List, Dict, Any, Optional, Type
from sqlalchemy.orm import Session  # type: ignore

from ...models.base import BaseModel
from ...repositories.base_repository import Repository

T = TypeVar('T', bound=BaseModel)
M = TypeVar('M')  # SQLAlchemy model type


class SQLAlchemyRepository(Generic[T, M], Repository[T]):
    """
    Base SQLAlchemy implementation of the Repository pattern
    """
    
    def __init__(self, session: Session, model_class: Type[M], domain_class: Type[T]):
        """
        Initialize the repository with session and model class
        
        Args:
            session: SQLAlchemy session
            model_class: SQLAlchemy model class
            domain_class: Domain model class
        """
        self.session = session
        self.model_class = model_class
        self.domain_class = domain_class
    
    def get_by_id(self, id: str) -> Optional[T]:
        """
        Get an entity by its ID
        
        Args:
            id: The unique identifier of the entity
            
        Returns:
            The domain entity if found, None otherwise
        """
        db_obj = self.session.query(self.model_class).get(id)
        if not db_obj:
            return None
            
        return self._to_domain(db_obj)
    
    def list(self, filters: Dict[str, Any] = None, 
             page: int = 1, page_size: int = 20) -> List[T]:
        """
        List entities with optional filtering and pagination
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            List of domain entities matching the criteria
        """
        # Start with a base query
        query = self.session.query(self.model_class)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
        
        # Apply pagination
        query = query.limit(page_size).offset((page - 1) * page_size)
        
        # Convert to domain entities
        return [self._to_domain(db_obj) for db_obj in query.all()]
    
    def create(self, entity: T) -> T:
        """
        Create a new entity
        
        Args:
            entity: The domain entity to create
            
        Returns:
            The created domain entity with any auto-generated fields populated
        """
        db_obj = self._to_db_obj(entity)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        
        return self._to_domain(db_obj)
    
    def update(self, entity: T) -> T:
        """
        Update an existing entity
        
        Args:
            entity: The domain entity to update
            
        Returns:
            The updated domain entity
        """
        db_obj = self.session.query(self.model_class).get(entity.id)
        if not db_obj:
            raise ValueError(f"Entity with ID {entity.id} not found")
            
        # Update fields from entity to db_obj
        self._update_db_obj(db_obj, entity)
        
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        
        return self._to_domain(db_obj)
    
    def delete(self, id: str) -> bool:
        """
        Delete an entity by its ID
        
        Args:
            id: The unique identifier of the entity
            
        Returns:
            True if the entity was deleted, False otherwise
        """
        db_obj = self.session.query(self.model_class).get(id)
        if not db_obj:
            return False
            
        self.session.delete(db_obj)
        self.session.commit()
        
        return True
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """
        Count entities with optional filtering
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            
        Returns:
            Number of entities matching the criteria
        """
        # Start with a base query
        query = self.session.query(self.model_class)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
        
        return query.count()
    
    def _to_domain(self, db_obj: M) -> T:
        """
        Convert a database object to a domain entity
        To be implemented by subclasses
        
        Args:
            db_obj: Database model instance
            
        Returns:
            Domain entity
        """
        raise NotImplementedError("Subclasses must implement _to_domain")
    
    def _to_db_obj(self, entity: T) -> M:
        """
        Convert a domain entity to a database object
        To be implemented by subclasses
        
        Args:
            entity: Domain entity
            
        Returns:
            Database model instance
        """
        raise NotImplementedError("Subclasses must implement _to_db_obj")
    
    def _update_db_obj(self, db_obj: M, entity: T) -> None:
        """
        Update a database object from a domain entity
        To be implemented by subclasses
        
        Args:
            db_obj: Database model instance to update
            entity: Domain entity with updated values
        """
        raise NotImplementedError("Subclasses must implement _update_db_obj")