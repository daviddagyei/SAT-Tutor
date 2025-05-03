"""
User model for authentication and user management
"""
from enum import Enum
from typing import Optional

from .base import BaseModel


class UserRole(Enum):
    """Enumeration of possible user roles"""
    STUDENT = "student"
    TUTOR = "tutor" 
    ADMIN = "admin"


class User(BaseModel):
    """
    User entity representing students, tutors, and administrators
    """
    
    def __init__(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole = UserRole.STUDENT,
        profile_image_url: Optional[str] = None,
        is_email_confirmed: bool = False,
        email_confirmation_token: Optional[str] = None,
        password_reset_token: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a new user
        
        Args:
            email: User's email address (unique)
            hashed_password: Securely hashed password
            full_name: User's full name
            role: User's role (student, tutor, admin)
            profile_image_url: URL to user's profile image
            is_email_confirmed: Whether email has been confirmed
            email_confirmation_token: Token for email confirmation
            password_reset_token: Token for password reset
        """
        super().__init__(**kwargs)
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.profile_image_url = profile_image_url
        self.is_email_confirmed = is_email_confirmed
        self.email_confirmation_token = email_confirmation_token
        self.password_reset_token = password_reset_token
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_tutor(self) -> bool:
        """Check if user has tutor role"""
        return self.role == UserRole.TUTOR
    
    def reset_email_confirmation(self, token: str) -> None:
        """Set a new email confirmation token"""
        self.is_email_confirmed = False
        self.email_confirmation_token = token
    
    def confirm_email(self) -> None:
        """Mark email as confirmed and clear confirmation token"""
        self.is_email_confirmed = True
        self.email_confirmation_token = None
    
    def set_password_reset_token(self, token: str) -> None:
        """Set password reset token"""
        self.password_reset_token = token
    
    def clear_password_reset_token(self) -> None:
        """Clear password reset token after use"""
        self.password_reset_token = None
        
    def update_password(self, new_hashed_password: str) -> None:
        """Update password with new hashed value"""
        self.hashed_password = new_hashed_password
        self.clear_password_reset_token()
        self.update()