"""
Unit tests for the authentication endpoints
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.api.v1.endpoints.auth import router as auth_router


@pytest.fixture
def mock_auth_service():
    """Mock auth service for testing endpoints"""
    return MagicMock(spec=AuthService)


@pytest.fixture
def test_app(mock_auth_service):
    """Create a test FastAPI app with the auth router"""
    app = FastAPI()
    
    # Override the dependency to return our mock auth service
    def get_auth_service():
        return mock_auth_service
    
    # Use the same router but override dependencies
    app.include_router(auth_router)
    
    # Override the dependency
    app.dependency_overrides = {
        # Replace the real auth service with our mock
        "get_auth_service": get_auth_service
    }
    
    return app


@pytest.fixture
def client(test_app):
    """Create a test client for the FastAPI app"""
    return TestClient(test_app)


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(
        id="user_123",
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        role=UserRole.STUDENT,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestAuthEndpoints:
    """Tests for authentication endpoints"""
    
    def test_register_user_success(self, client, mock_auth_service, sample_user):
        """Test successful user registration endpoint"""
        # Configure the mock service to return a user and token
        mock_auth_service.register_user.return_value = (sample_user, "confirmation_token_123")
        
        # Make the request to register a user
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Test User"
            }
        )
        
        # Check that the registration was successful
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["full_name"] == "Test User"
        assert data["user"]["role"] == UserRole.STUDENT
        assert "id" in data["user"]
        assert "password" not in data["user"]
        assert "hashed_password" not in data["user"]
        
        # Check that auth service was called correctly
        mock_auth_service.register_user.assert_called_once_with(
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
    
    def test_register_user_validation_error(self, client):
        """Test user registration with invalid data"""
        # Make the request with invalid data (missing password)
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User"
                # Missing password
            }
        )
        
        # Check that the request was rejected
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_register_user_email_exists(self, client, mock_auth_service):
        """Test user registration with existing email"""
        # Configure the mock service to raise an error
        mock_auth_service.register_user.side_effect = ValueError("Email is already registered")
        
        # Make the request
        response = client.post(
            "/auth/register",
            json={
                "email": "existing@example.com",
                "password": "password123",
                "full_name": "Test User"
            }
        )
        
        # Check that the registration failed
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"]
    
    def test_login_success(self, client, mock_auth_service, sample_user):
        """Test successful login endpoint"""
        # Configure the mock service
        mock_auth_service.authenticate_user.return_value = sample_user
        mock_auth_service.create_access_token.return_value = "jwt_token_123"
        
        # Make the login request
        response = client.post(
            "/auth/login",
            data={
                "username": "test@example.com",  # FastAPI OAuth form uses 'username'
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Check that login was successful
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "jwt_token_123"
        assert data["token_type"] == "bearer"
        
        # Check that auth service was called correctly
        mock_auth_service.authenticate_user.assert_called_once_with(
            email="test@example.com",
            password="password123"
        )
        mock_auth_service.create_access_token.assert_called_once()
    
    def test_login_invalid_credentials(self, client, mock_auth_service):
        """Test login with invalid credentials"""
        # Configure the mock service to return None (authentication failure)
        mock_auth_service.authenticate_user.return_value = None
        
        # Make the login request
        response = client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrong_password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Check that login failed
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Incorrect email or password" in data["detail"]
        
        # Check that auth service was called correctly
        mock_auth_service.authenticate_user.assert_called_once_with(
            email="test@example.com",
            password="wrong_password"
        )
        mock_auth_service.create_access_token.assert_not_called()
    
    def test_get_current_user(self, client, mock_auth_service, sample_user):
        """Test getting current user endpoint"""
        # Configure the mock service
        mock_auth_service.get_current_user.return_value = sample_user
        
        # Make the request with a mock token
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer mock_token_123"}
        )
        
        # Check that user data was returned
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["role"] == UserRole.STUDENT
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data
        
        # Check that auth service was called correctly
        mock_auth_service.get_current_user.assert_called_once_with("mock_token_123")
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        # Make the request without a token
        response = client.get("/auth/me")
        
        # Check that the request was rejected
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Not authenticated" in data["detail"]
    
    def test_confirm_email(self, client, mock_auth_service):
        """Test confirming email endpoint"""
        # Configure the mock service
        mock_auth_service.confirm_email.return_value = True
        
        # Make the request
        response = client.post(
            "/auth/confirm-email",
            json={"token": "confirmation_token_123"}
        )
        
        # Check that email was confirmed
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Email confirmed successfully"
        
        # Check that auth service was called correctly
        mock_auth_service.confirm_email.assert_called_once_with("confirmation_token_123")
    
    def test_confirm_email_invalid_token(self, client, mock_auth_service):
        """Test confirming email with invalid token"""
        # Configure the mock service
        mock_auth_service.confirm_email.return_value = False
        
        # Make the request
        response = client.post(
            "/auth/confirm-email",
            json={"token": "invalid_token"}
        )
        
        # Check that confirmation failed
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid confirmation token" in data["detail"]
        
        # Check that auth service was called correctly
        mock_auth_service.confirm_email.assert_called_once_with("invalid_token")
    
    def test_request_password_reset(self, client, mock_auth_service):
        """Test requesting password reset endpoint"""
        # Configure the mock service
        mock_auth_service.request_password_reset.return_value = "reset_token_123"
        
        # Make the request
        response = client.post(
            "/auth/request-password-reset",
            json={"email": "test@example.com"}
        )
        
        # Check that reset was requested
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password reset link sent to email"
        
        # Check that auth service was called correctly
        mock_auth_service.request_password_reset.assert_called_once_with("test@example.com")
    
    def test_request_password_reset_nonexistent_email(self, client, mock_auth_service):
        """Test requesting password reset for non-existent email"""
        # Configure the mock service
        mock_auth_service.request_password_reset.return_value = None
        
        # Make the request
        response = client.post(
            "/auth/request-password-reset",
            json={"email": "nonexistent@example.com"}
        )
        
        # Should still return 200 for security reasons (not revealing if email exists)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "If email exists, password reset link sent"
        
        # Check that auth service was called correctly
        mock_auth_service.request_password_reset.assert_called_once_with("nonexistent@example.com")
    
    def test_reset_password(self, client, mock_auth_service):
        """Test resetting password endpoint"""
        # Configure the mock service
        mock_auth_service.reset_password.return_value = True
        
        # Make the request
        response = client.post(
            "/auth/reset-password",
            json={
                "token": "reset_token_123",
                "new_password": "new_password123"
            }
        )
        
        # Check that password was reset
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password reset successfully"
        
        # Check that auth service was called correctly
        mock_auth_service.reset_password.assert_called_once_with(
            token="reset_token_123",
            new_password="new_password123"
        )
    
    def test_reset_password_invalid_token(self, client, mock_auth_service):
        """Test resetting password with invalid token"""
        # Configure the mock service
        mock_auth_service.reset_password.return_value = False
        
        # Make the request
        response = client.post(
            "/auth/reset-password",
            json={
                "token": "invalid_token",
                "new_password": "new_password123"
            }
        )
        
        # Check that reset failed
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid or expired password reset token" in data["detail"]
        
        # Check that auth service was called correctly
        mock_auth_service.reset_password.assert_called_once_with(
            token="invalid_token",
            new_password="new_password123"
        )
    
    def test_change_password(self, client, mock_auth_service, sample_user):
        """Test changing password endpoint"""
        # Configure the mock service
        mock_auth_service.get_current_user.return_value = sample_user
        mock_auth_service.change_password.return_value = True
        
        # Make the request
        response = client.post(
            "/auth/change-password",
            headers={"Authorization": "Bearer mock_token_123"},
            json={
                "current_password": "current_password",
                "new_password": "new_password123"
            }
        )
        
        # Check that password was changed
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"
        
        # Check that auth service was called correctly
        mock_auth_service.get_current_user.assert_called_once_with("mock_token_123")
        mock_auth_service.change_password.assert_called_once_with(
            user_id=sample_user.id,
            current_password="current_password",
            new_password="new_password123"
        )
    
    def test_change_password_incorrect_current(self, client, mock_auth_service, sample_user):
        """Test changing password with incorrect current password"""
        # Configure the mock service
        mock_auth_service.get_current_user.return_value = sample_user
        mock_auth_service.change_password.return_value = False
        
        # Make the request
        response = client.post(
            "/auth/change-password",
            headers={"Authorization": "Bearer mock_token_123"},
            json={
                "current_password": "wrong_password",
                "new_password": "new_password123"
            }
        )
        
        # Check that change failed
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Current password is incorrect" in data["detail"]