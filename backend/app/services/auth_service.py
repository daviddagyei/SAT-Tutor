"""
Authentication service for user management and security
"""
import os
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

import jwt  # type: ignore
from passlib.context import CryptContext  # type: ignore

from ..models.user import User, UserRole
from ..models.profile import Profile
from ..repositories.user_repository import UserRepository


class AuthService:
    """
    Service for authentication and authorization functionality
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize the authentication service
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Get JWT settings from environment or use defaults
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    def register_user(self, email: str, password: str, full_name: str) -> Tuple[User, str]:
        """
        Register a new user
        
        Args:
            email: User's email address
            password: User's password (will be hashed)
            full_name: User's full name
            
        Returns:
            Tuple of (user, confirmation_token)
            
        Raises:
            ValueError: If the email is already registered
        """
        # Check if user already exists
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError(f"Email {email} is already registered")
            
        # Hash the password
        hashed_password = self.pwd_context.hash(password)
        
        # Generate email confirmation token
        confirmation_token = secrets.token_urlsafe(32)
        
        # Create new user
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=UserRole.STUDENT,  # Default role
            is_email_confirmed=False,
            email_confirmation_token=confirmation_token
        )
        
        # Save user to database
        created_user = self.user_repository.create(new_user)
        
        return created_user, confirmation_token
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
            
        # Verify password
        if not self.pwd_context.verify(password, user.hashed_password):
            return None
            
        return user
    
    def create_access_token(self, user_id: str, expires_delta: timedelta = None) -> str:
        """
        Create a JWT access token for a user
        
        Args:
            user_id: ID of the user
            expires_delta: Optional custom expiration time
            
        Returns:
            JWT token string
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)
            
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": user_id,
            "exp": expire
        }
        
        return jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """
        Get the current user from a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            User if token is valid, None otherwise
        """
        payload = self.verify_token(token)
        if not payload:
            return None
            
        user_id = payload.get("sub")
        if not user_id:
            return None
            
        return self.user_repository.get_by_id(user_id)
    
    def confirm_email(self, token: str) -> bool:
        """
        Confirm a user's email address using the confirmation token
        
        Args:
            token: Email confirmation token
            
        Returns:
            True if email confirmed successfully, False otherwise
        """
        return self.user_repository.confirm_email(token)
    
    def request_password_reset(self, email: str) -> Optional[str]:
        """
        Request a password reset and generate a reset token
        
        Args:
            email: User's email address
            
        Returns:
            Reset token if user exists, None otherwise
        """
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
            
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Set the token on the user
        user.set_password_reset_token(reset_token)
        
        # Update the user in the database
        self.user_repository.update(user)
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset a user's password using a reset token
        
        Args:
            token: Password reset token
            new_password: New password (will be hashed)
            
        Returns:
            True if password reset successfully, False otherwise
        """
        user = self.user_repository.get_by_password_reset_token(token)
        if not user:
            return False
            
        # Hash the new password
        hashed_password = self.pwd_context.hash(new_password)
        
        # Update the password and clear the reset token
        user.update_password(hashed_password)
        
        # Update the user in the database
        self.user_repository.update(user)
        
        return True
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change a user's password (requires current password)
        
        Args:
            user_id: ID of the user
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password changed successfully, False otherwise
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return False
            
        # Verify current password
        if not self.pwd_context.verify(current_password, user.hashed_password):
            return False
            
        # Hash and set the new password
        hashed_password = self.pwd_context.hash(new_password)
        user.update_password(hashed_password)
        
        # Update the user in the database
        self.user_repository.update(user)
        
        return True