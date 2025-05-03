"""
User repository interface for user data access operations
"""
from typing import Optional, List, Dict, Any

from .base_repository import Repository
from ..models.user import User


class UserRepository(Repository[User]):
    """
    Repository interface for User entity with specialized methods
    """
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by their email address
        
        Args:
            email: The email address to search for
            
        Returns:
            The user if found, None otherwise
        """
        pass
    
    def get_by_email_confirmation_token(self, token: str) -> Optional[User]:
        """
        Find a user by their email confirmation token
        
        Args:
            token: The email confirmation token
            
        Returns:
            The user if found, None otherwise
        """
        pass
    
    def get_by_password_reset_token(self, token: str) -> Optional[User]:
        """
        Find a user by their password reset token
        
        Args:
            token: The password reset token
            
        Returns:
            The user if found, None otherwise
        """
        pass
    
    def confirm_email(self, token: str) -> bool:
        """
        Confirm a user's email using their confirmation token
        
        Args:
            token: The email confirmation token
            
        Returns:
            True if the email was confirmed, False otherwise
        """
        pass
    
    def update_password(self, user_id: str, new_password_hash: str) -> bool:
        """
        Update a user's password
        
        Args:
            user_id: The ID of the user
            new_password_hash: The new hashed password
            
        Returns:
            True if the password was updated, False otherwise
        """
        pass
    
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
        pass