"""
SQLAlchemy implementation of the User repository
"""
from typing import Optional, List
from sqlalchemy.orm import Session  # type: ignore

from ...models.user import User, UserRole
from ...repositories.user_repository import UserRepository
from ..database.models import UserModel
from .sqlalchemy_base_repository import SQLAlchemyRepository


class SQLAlchemyUserRepository(SQLAlchemyRepository[User, UserModel], UserRepository):
    """
    SQLAlchemy implementation of the User repository
    """
    
    def __init__(self, session: Session):
        """
        Initialize the repository with session
        
        Args:
            session: SQLAlchemy session
        """
        super().__init__(session, UserModel, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by their email address
        
        Args:
            email: The email address to search for
            
        Returns:
            The user if found, None otherwise
        """
        db_user = self.session.query(UserModel).filter(UserModel.email == email).first()
        if not db_user:
            return None
            
        return self._to_domain(db_user)
    
    def get_by_email_confirmation_token(self, token: str) -> Optional[User]:
        """
        Find a user by their email confirmation token
        
        Args:
            token: The email confirmation token
            
        Returns:
            The user if found, None otherwise
        """
        db_user = self.session.query(UserModel).filter(
            UserModel.email_confirmation_token == token
        ).first()
        
        if not db_user:
            return None
            
        return self._to_domain(db_user)
    
    def get_by_password_reset_token(self, token: str) -> Optional[User]:
        """
        Find a user by their password reset token
        
        Args:
            token: The password reset token
            
        Returns:
            The user if found, None otherwise
        """
        db_user = self.session.query(UserModel).filter(
            UserModel.password_reset_token == token
        ).first()
        
        if not db_user:
            return None
            
        return self._to_domain(db_user)
    
    def confirm_email(self, token: str) -> bool:
        """
        Confirm a user's email using their confirmation token
        
        Args:
            token: The email confirmation token
            
        Returns:
            True if the email was confirmed, False otherwise
        """
        db_user = self.session.query(UserModel).filter(
            UserModel.email_confirmation_token == token
        ).first()
        
        if not db_user:
            return False
            
        db_user.is_email_confirmed = True
        db_user.email_confirmation_token = None
        self.session.commit()
        
        return True
    
    def update_password(self, user_id: str, new_password_hash: str) -> bool:
        """
        Update a user's password
        
        Args:
            user_id: The ID of the user
            new_password_hash: The new hashed password
            
        Returns:
            True if the password was updated, False otherwise
        """
        db_user = self.session.query(UserModel).get(user_id)
        if not db_user:
            return False
            
        db_user.hashed_password = new_password_hash
        db_user.password_reset_token = None
        self.session.commit()
        
        return True
    
    def get_users_by_role(self, role: str, page: int = 1, page_size: int = 20) -> List[User]:
        """
        Get users with a specific role
        
        Args:
            role: The role to filter by
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            List of users with the specified role
        """
        query = self.session.query(UserModel).filter(UserModel.role == role)
        query = query.limit(page_size).offset((page - 1) * page_size)
        
        return [self._to_domain(db_user) for db_user in query.all()]
    
    def _to_domain(self, db_obj: UserModel) -> User:
        """
        Convert a database user to a domain user
        
        Args:
            db_obj: Database user model instance
            
        Returns:
            Domain user entity
        """
        return User(
            email=db_obj.email,
            hashed_password=db_obj.hashed_password,
            full_name=db_obj.full_name,
            role=db_obj.role,
            profile_image_url=db_obj.profile_image_url,
            is_email_confirmed=db_obj.is_email_confirmed,
            email_confirmation_token=db_obj.email_confirmation_token,
            password_reset_token=db_obj.password_reset_token,
            id=db_obj.id,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at
        )
    
    def _to_db_obj(self, entity: User) -> UserModel:
        """
        Convert a domain user to a database user
        
        Args:
            entity: Domain user entity
            
        Returns:
            Database user model instance
        """
        return UserModel(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            full_name=entity.full_name,
            role=entity.role,
            profile_image_url=entity.profile_image_url,
            is_email_confirmed=entity.is_email_confirmed,
            email_confirmation_token=entity.email_confirmation_token,
            password_reset_token=entity.password_reset_token,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _update_db_obj(self, db_obj: UserModel, entity: User) -> None:
        """
        Update a database user from a domain user
        
        Args:
            db_obj: Database user model instance to update
            entity: Domain user entity with updated values
        """
        db_obj.email = entity.email
        db_obj.hashed_password = entity.hashed_password
        db_obj.full_name = entity.full_name
        db_obj.role = entity.role
        db_obj.profile_image_url = entity.profile_image_url
        db_obj.is_email_confirmed = entity.is_email_confirmed
        db_obj.email_confirmation_token = entity.email_confirmation_token
        db_obj.password_reset_token = entity.password_reset_token
        db_obj.updated_at = entity.updated_at