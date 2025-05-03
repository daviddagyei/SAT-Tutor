"""
Unit tests for the User model
"""
import pytest
from datetime import datetime

from app.models.user import User, UserRole


class TestUserModel:
    """Tests for the User model"""

    def test_init_with_required_values(self):
        """Test that User initializes correctly with required values"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password123",
            full_name="Test User"
        )
        
        # Check required fields
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password123"
        assert user.full_name == "Test User"
        
        # Check default values
        assert user.role == UserRole.STUDENT
        assert user.profile_image_url is None
        assert not user.is_email_confirmed
        assert user.email_confirmation_token is None
        assert user.password_reset_token is None

    def test_init_with_all_values(self):
        """Test that User initializes correctly with all values provided"""
        user = User(
            email="admin@example.com",
            hashed_password="admin_password",
            full_name="Admin User",
            role=UserRole.ADMIN,
            profile_image_url="http://example.com/image.jpg",
            is_email_confirmed=True,
            email_confirmation_token="confirm_token_123",
            password_reset_token="reset_token_456"
        )
        
        # Check all fields
        assert user.email == "admin@example.com"
        assert user.hashed_password == "admin_password"
        assert user.full_name == "Admin User"
        assert user.role == UserRole.ADMIN
        assert user.profile_image_url == "http://example.com/image.jpg"
        assert user.is_email_confirmed
        assert user.email_confirmation_token == "confirm_token_123"
        assert user.password_reset_token == "reset_token_456"

    def test_is_admin_property(self):
        """Test the is_admin property returns correct value based on role"""
        admin = User(
            email="admin@example.com",
            hashed_password="pwd",
            full_name="Admin",
            role=UserRole.ADMIN
        )
        
        student = User(
            email="student@example.com",
            hashed_password="pwd",
            full_name="Student",
            role=UserRole.STUDENT
        )
        
        tutor = User(
            email="tutor@example.com",
            hashed_password="pwd",
            full_name="Tutor",
            role=UserRole.TUTOR
        )
        
        assert admin.is_admin is True
        assert student.is_admin is False
        assert tutor.is_admin is False

    def test_update_password(self):
        """Test updating the password"""
        user = User(
            email="test@example.com",
            hashed_password="original_password",
            full_name="Test User",
            password_reset_token="reset_token"
        )
        
        # Update password
        user.update_password("new_password")
        
        # Check that password was updated and reset token was cleared
        assert user.hashed_password == "new_password"
        assert user.password_reset_token is None

    def test_set_password_reset_token(self):
        """Test setting a password reset token"""
        user = User(
            email="test@example.com",
            hashed_password="password",
            full_name="Test User"
        )
        
        # Set reset token
        user.set_password_reset_token("new_reset_token")
        
        # Check that token was set
        assert user.password_reset_token == "new_reset_token"