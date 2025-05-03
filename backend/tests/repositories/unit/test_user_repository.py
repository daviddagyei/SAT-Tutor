"""
Unit tests for the UserRepository implementation
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from app.repositories.user_repository import UserRepository
from app.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.database.models import UserModel
from app.models.user import User, UserRole


class TestSQLAlchemyUserRepository:
    """Tests for SQLAlchemyUserRepository implementation"""
    
    @pytest.fixture
    def user_model_instance(self):
        """Create a sample SQLAlchemy user model instance"""
        return UserModel(
            id="test_id_123",
            email="test@example.com",
            hashed_password="hashed_password_123",
            full_name="Test User",
            role=UserRole.STUDENT,
            profile_image_url=None,
            is_email_confirmed=True,
            email_confirmation_token=None,
            password_reset_token=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def user_domain_instance(self):
        """Create a sample user domain model instance"""
        return User(
            id="test_id_123",
            email="test@example.com",
            hashed_password="hashed_password_123",
            full_name="Test User",
            role=UserRole.STUDENT,
            is_email_confirmed=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def test_get_by_id(self, db_session, user_model_instance):
        """Test retrieving a user by ID"""
        # Add a user to the mock session
        db_session.add(user_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Retrieve the user
        user = repo.get_by_id("test_id_123")
        
        # Check that user was retrieved correctly
        assert user is not None
        assert user.id == "test_id_123"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.full_name == "Test User"
        assert user.role == UserRole.STUDENT
    
    def test_get_by_email(self, db_session, user_model_instance):
        """Test retrieving a user by email"""
        # Add a user to the mock session
        db_session.add(user_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Retrieve the user
        user = repo.get_by_email("test@example.com")
        
        # Check that user was retrieved correctly
        assert user is not None
        assert user.id == "test_id_123"
        assert user.email == "test@example.com"
    
    def test_get_by_email_not_found(self, db_session):
        """Test retrieving a non-existent user by email"""
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Try to retrieve a user that doesn't exist
        user = repo.get_by_email("nonexistent@example.com")
        
        # Check that no user was retrieved
        assert user is None
    
    def test_get_by_email_confirmation_token(self, db_session, user_model_instance):
        """Test retrieving a user by email confirmation token"""
        # Set confirmation token
        user_model_instance.email_confirmation_token = "confirm_123"
        db_session.add(user_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Retrieve the user
        user = repo.get_by_email_confirmation_token("confirm_123")
        
        # Check that user was retrieved correctly
        assert user is not None
        assert user.id == "test_id_123"
        assert user.email_confirmation_token == "confirm_123"
    
    def test_get_by_password_reset_token(self, db_session, user_model_instance):
        """Test retrieving a user by password reset token"""
        # Set reset token
        user_model_instance.password_reset_token = "reset_token_123"
        db_session.add(user_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Retrieve the user
        user = repo.get_by_password_reset_token("reset_token_123")
        
        # Check that user was retrieved correctly
        assert user is not None
        assert user.id == "test_id_123"
        assert user.password_reset_token == "reset_token_123"
    
    def test_create(self, db_session, user_domain_instance):
        """Test creating a new user"""
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Create a new user
        created_user = repo.create(user_domain_instance)
        
        # Check that user was created correctly
        assert created_user.id == user_domain_instance.id
        assert created_user.email == user_domain_instance.email
        assert created_user.full_name == user_domain_instance.full_name
        
        # Verify it's in the database
        db_user = db_session.query(UserModel).get(user_domain_instance.id)
        assert db_user is not None
        assert db_user.email == user_domain_instance.email
    
    def test_update(self, db_session, user_model_instance):
        """Test updating a user"""
        # Add a user to the session
        db_session.add(user_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Get the user
        user = repo.get_by_id("test_id_123")
        
        # Update the user
        user.full_name = "Updated Name"
        user.profile_image_url = "http://example.com/image.jpg"
        
        # Save changes
        updated_user = repo.update(user)
        
        # Check that user was updated correctly
        assert updated_user.full_name == "Updated Name"
        assert updated_user.profile_image_url == "http://example.com/image.jpg"
        
        # Verify changes in the database
        db_user = db_session.query(UserModel).get("test_id_123")
        assert db_user.full_name == "Updated Name"
        assert db_user.profile_image_url == "http://example.com/image.jpg"
    
    def test_delete(self, db_session, user_model_instance):
        """Test deleting a user"""
        # Add a user to the session
        db_session.add(user_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Delete the user
        result = repo.delete("test_id_123")
        
        # Check that deletion was successful
        assert result is True
        
        # Verify user no longer in database
        db_user = db_session.query(UserModel).get("test_id_123")
        assert db_user is None
    
    def test_confirm_email(self, db_session, user_model_instance):
        """Test confirming a user's email"""
        # Set confirmation token
        user_model_instance.email_confirmation_token = "confirm_token_123"
        user_model_instance.is_email_confirmed = False
        db_session.add(user_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Confirm email
        result = repo.confirm_email("confirm_token_123")
        
        # Check that confirmation was successful
        assert result is True
        
        # Verify user is confirmed and token is cleared
        db_user = db_session.query(UserModel).get("test_id_123")
        assert db_user.is_email_confirmed is True
        assert db_user.email_confirmation_token is None
    
    def test_update_password(self, db_session, user_model_instance):
        """Test updating a user's password"""
        # Add a user to the session
        db_session.add(user_model_instance)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Update password
        result = repo.update_password("test_id_123", "new_hashed_password")
        
        # Check that update was successful
        assert result is True
        
        # Verify password was changed
        db_user = db_session.query(UserModel).get("test_id_123")
        assert db_user.hashed_password == "new_hashed_password"
    
    def test_get_users_by_role(self, db_session, user_model_instance):
        """Test getting users by role"""
        # Add a user to the session
        db_session.add(user_model_instance)
        
        # Add another user with different role
        admin_user = UserModel(
            id="admin_id_123",
            email="admin@example.com",
            hashed_password="admin_password",
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_email_confirmed=True
        )
        db_session.add(admin_user)
        db_session.commit()
        
        # Create repository with the session
        repo = SQLAlchemyUserRepository(db_session)
        
        # Get students
        students = repo.get_users_by_role(UserRole.STUDENT.value)
        assert len(students) == 1
        assert students[0].email == "test@example.com"
        
        # Get admins
        admins = repo.get_users_by_role(UserRole.ADMIN.value)
        assert len(admins) == 1
        assert admins[0].email == "admin@example.com"