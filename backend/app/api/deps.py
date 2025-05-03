"""
API dependencies for dependency injection
"""
from typing import Generator, Optional

# Add type ignore comment to silence Pylance warning
from fastapi import Depends, HTTPException, status  # type: ignore
from fastapi.security import OAuth2PasswordBearer  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ..infrastructure.database.session import get_db_session
from ..infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from ..infrastructure.repositories.sqlalchemy_question_repository import SQLAlchemyQuestionRepository
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..repositories.question_repository import QuestionRepository
from ..services.auth_service import AuthService
from ..services.learning_service import LearningService

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    """
    Get a UserRepository instance with the current db session
    """
    return SQLAlchemyUserRepository(db)

def get_question_repository(db: Session = Depends(get_db_session)) -> QuestionRepository:
    """
    Get a QuestionRepository instance with the current db session
    """
    return SQLAlchemyQuestionRepository(db)

def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """
    Get an AuthService instance
    """
    return AuthService(user_repository)

def get_learning_service(
    question_repository: QuestionRepository = Depends(get_question_repository),
    user_repository: UserRepository = Depends(get_user_repository)
) -> LearningService:
    """
    Get a LearningService instance
    """
    return LearningService(question_repository, user_repository)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Get the current authenticated user based on the token
    """
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current user and verify that they are active (email confirmed)
    """
    if not current_user.is_email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not confirmed"
        )
    return current_user

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current user and verify that they are an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return current_user