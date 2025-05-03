"""
Unit tests for the AuthService
"""
import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt  # type: ignore

from app.models.user import User, UserRole
from app.services.auth_service import AuthService


class TestAuthService:
    """Tests for the AuthService"""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository for testing"""
        return MagicMock()
    
    @pytest.fixture
    def auth_service(self, mock_user_repository):
        """Create an AuthService instance for testing"""
        service = AuthService(mock_user_repository)
        # Override JWT settings for testing
        service.jwt_secret_key = "test_secret_key"
        service.jwt_algorithm = "HS256"
        service.access_token_expire_minutes = 30
        return service
    
    def test_register_user_success(self, auth_service, mock_user_repository):
        """Test successful user registration"""
        # Configure mock repository
        mock_user_repository.get_by_email.return_value = None
        
        # Set up the mock to return the created user
        def create_side_effect(user):
            return user
        mock_user_repository.create.side_effect = create_side_effect
        
        # Register a user
        user, token = auth_service.register_user(
            email="new_user@example.com",
            password="password123",
            full_name="New User"
        )
        
        # Check that repository methods were called correctly
        mock_user_repository.get_by_email.assert_called_once_with("new_user@example.com")
        mock_user_repository.create.assert_called_once()
        
        # Check that returned user has correct data
        assert user.email == "new_user@example.com"
        assert user.full_name == "New User"
        assert user.role == UserRole.STUDENT
        assert user.is_email_confirmed is False
        
        # Password should be hashed
        assert user.hashed_password != "password123"
        
        # Should have received a confirmation token
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_register_user_email_exists(self, auth_service, mock_user_repository):
        """Test user registration with existing email"""
        # Configure mock repository to return an existing user
        existing_user = User(
            email="existing@example.com",
            hashed_password="hashed_password",
            full_name="Existing User"
        )
        mock_user_repository.get_by_email.return_value = existing_user
        
        # Try to register with the same email
        with pytest.raises(ValueError) as exc_info:
            auth_service.register_user(
                email="existing@example.com",
                password="password123",
                full_name="New User"
            )
        
        # Check that the correct error was raised
        assert "is already registered" in str(exc_info.value)
        
        # Check that create was not called
        mock_user_repository.create.assert_not_called()
    
    def test_authenticate_user_success(self, auth_service, mock_user_repository):
        """Test successful user authentication"""
        # Create a user with a known password
        test_user = User(
            email="test@example.com",
            full_name="Test User"
        )
        # Set a hashed password that will validate with "password123"
        test_user.hashed_password = auth_service.pwd_context.hash("password123")
        
        # Configure mock repository
        mock_user_repository.get_by_email.return_value = test_user
        
        # Authenticate the user
        authenticated_user = auth_service.authenticate_user(
            email="test@example.com",
            password="password123"
        )
        
        # Check that the user was authenticated
        assert authenticated_user is not None
        assert authenticated_user.email == "test@example.com"
    
    def test_authenticate_user_wrong_password(self, auth_service, mock_user_repository):
        """Test user authentication with wrong password"""
        # Create a user with a known password
        test_user = User(
            email="test@example.com",
            full_name="Test User"
        )
        # Set a hashed password that will validate with "password123"
        test_user.hashed_password = auth_service.pwd_context.hash("password123")
        
        # Configure mock repository
        mock_user_repository.get_by_email.return_value = test_user
        
        # Try to authenticate with wrong password
        authenticated_user = auth_service.authenticate_user(
            email="test@example.com",
            password="wrong_password"
        )
        
        # Check that authentication failed
        assert authenticated_user is None
    
    def test_authenticate_user_nonexistent_email(self, auth_service, mock_user_repository):
        """Test user authentication with non-existent email"""
        # Configure mock repository
        mock_user_repository.get_by_email.return_value = None
        
        # Try to authenticate with non-existent email
        authenticated_user = auth_service.authenticate_user(
            email="nonexistent@example.com",
            password="password123"
        )
        
        # Check that authentication failed
        assert authenticated_user is None
    
    def test_create_access_token(self, auth_service):
        """Test creating a JWT access token"""
        # Create a token
        token = auth_service.create_access_token(
            user_id="user_id_123"
        )
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode the token and check its contents
        payload = jwt.decode(
            token,
            auth_service.jwt_secret_key,
            algorithms=[auth_service.jwt_algorithm]
        )
        
        # Check payload contents
        assert payload["sub"] == "user_id_123"
        assert "exp" in payload
        
        # The token should expire in the future
        expiry = datetime.fromtimestamp(payload["exp"])
        future_time = datetime.utcnow() + timedelta(minutes=29)  # Just under 30 minutes
        assert expiry > future_time
    
    def test_verify_token_valid(self, auth_service):
        """Test verifying a valid token"""
        # Create a token
        token = auth_service.create_access_token(
            user_id="user_id_123"
        )
        
        # Verify the token
        payload = auth_service.verify_token(token)
        
        # Check that token was verified
        assert payload is not None
        assert payload["sub"] == "user_id_123"
    
    def test_verify_token_invalid(self, auth_service):
        """Test verifying an invalid token"""
        # Try to verify an invalid token
        payload = auth_service.verify_token("invalid.token.string")
        
        # Check that verification failed
        assert payload is None
    
    def test_get_current_user(self, auth_service, mock_user_repository):
        """Test getting current user from token"""
        # Create a user
        test_user = User(
            id="user_id_123",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        
        # Configure mock repository
        mock_user_repository.get_by_id.return_value = test_user
        
        # Create a token for the user
        token = auth_service.create_access_token(
            user_id="user_id_123"
        )
        
        # Get the current user using the token
        current_user = auth_service.get_current_user(token)
        
        # Check that the user was retrieved
        assert current_user is not None
        assert current_user.id == "user_id_123"
        assert current_user.email == "test@example.com"
        
        # Check that repository method was called correctly
        mock_user_repository.get_by_id.assert_called_once_with("user_id_123")
    
    def test_confirm_email(self, auth_service, mock_user_repository):
        """Test confirming a user's email"""
        # Configure mock repository
        mock_user_repository.confirm_email.return_value = True
        
        # Confirm email
        result = auth_service.confirm_email("confirmation_token_123")
        
        # Check that confirmation was successful
        assert result is True
        
        # Check that repository method was called correctly
        mock_user_repository.confirm_email.assert_called_once_with("confirmation_token_123")
    
    def test_request_password_reset_success(self, auth_service, mock_user_repository):
        """Test requesting a password reset for an existing user"""
        # Create a user
        test_user = User(
            id="user_id_123",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        
        # Configure mock repository
        mock_user_repository.get_by_email.return_value = test_user
        mock_user_repository.update.return_value = test_user
        
        # Request password reset
        token = auth_service.request_password_reset("test@example.com")
        
        # Check that a token was generated
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Check that repository methods were called correctly
        mock_user_repository.get_by_email.assert_called_once_with("test@example.com")
        mock_user_repository.update.assert_called_once()
    
    def test_request_password_reset_nonexistent_email(self, auth_service, mock_user_repository):
        """Test requesting a password reset for a non-existent user"""
        # Configure mock repository
        mock_user_repository.get_by_email.return_value = None
        
        # Request password reset
        token = auth_service.request_password_reset("nonexistent@example.com")
        
        # Check that no token was generated
        assert token is None
        
        # Check that repository method was called correctly
        mock_user_repository.get_by_email.assert_called_once_with("nonexistent@example.com")
        mock_user_repository.update.assert_not_called()
    
    def test_reset_password_success(self, auth_service, mock_user_repository):
        """Test resetting a password with valid token"""
        # Create a user
        test_user = User(
            id="user_id_123",
            email="test@example.com",
            hashed_password="old_hashed_password",
            full_name="Test User",
            password_reset_token="reset_token_123"
        )
        
        # Configure mock repository
        mock_user_repository.get_by_password_reset_token.return_value = test_user
        mock_user_repository.update.return_value = test_user
        
        # Reset password
        result = auth_service.reset_password(
            token="reset_token_123",
            new_password="new_password123"
        )
        
        # Check that reset was successful
        assert result is True
        
        # Check that repository methods were called correctly
        mock_user_repository.get_by_password_reset_token.assert_called_once_with("reset_token_123")
        mock_user_repository.update.assert_called_once()
        
        # Check that user's password was updated
        updated_user = mock_user_repository.update.call_args[0][0]
        assert updated_user.hashed_password != "old_hashed_password"
        assert updated_user.hashed_password != "new_password123"  # Should be hashed
        assert updated_user.password_reset_token is None
    
    def test_reset_password_invalid_token(self, auth_service, mock_user_repository):
        """Test resetting a password with invalid token"""
        # Configure mock repository
        mock_user_repository.get_by_password_reset_token.return_value = None
        
        # Reset password
        result = auth_service.reset_password(
            token="invalid_token",
            new_password="new_password123"
        )
        
        # Check that reset failed
        assert result is False
        
        # Check that repository method was called correctly
        mock_user_repository.get_by_password_reset_token.assert_called_once_with("invalid_token")
        mock_user_repository.update.assert_not_called()
    
    def test_change_password_success(self, auth_service, mock_user_repository):
        """Test changing a user's password with correct current password"""
        # Create a user with a known password
        test_user = User(
            id="user_id_123",
            email="test@example.com",
            full_name="Test User"
        )
        # Set a hashed password that will validate with "current_password"
        test_user.hashed_password = auth_service.pwd_context.hash("current_password")
        
        # Configure mock repository
        mock_user_repository.get_by_id.return_value = test_user
        mock_user_repository.update.return_value = test_user
        
        # Change password
        result = auth_service.change_password(
            user_id="user_id_123",
            current_password="current_password",
            new_password="new_password123"
        )
        
        # Check that change was successful
        assert result is True
        
        # Check that repository methods were called correctly
        mock_user_repository.get_by_id.assert_called_once_with("user_id_123")
        mock_user_repository.update.assert_called_once()
        
        # Check that user's password was updated
        updated_user = mock_user_repository.update.call_args[0][0]
        assert updated_user.hashed_password != test_user.hashed_password
    
    def test_change_password_wrong_current_password(self, auth_service, mock_user_repository):
        """Test changing a user's password with incorrect current password"""
        # Create a user with a known password
        test_user = User(
            id="user_id_123",
            email="test@example.com",
            full_name="Test User"
        )
        # Set a hashed password that will validate with "current_password"
        test_user.hashed_password = auth_service.pwd_context.hash("current_password")
        
        # Configure mock repository
        mock_user_repository.get_by_id.return_value = test_user
        
        # Try to change password with wrong current password
        result = auth_service.change_password(
            user_id="user_id_123",
            current_password="wrong_password",
            new_password="new_password123"
        )
        
        # Check that change failed
        assert result is False
        
        # Check that repository method was called correctly
        mock_user_repository.get_by_id.assert_called_once_with("user_id_123")
        mock_user_repository.update.assert_not_called()