"""
Authentication API endpoints
"""
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from pydantic import BaseModel, EmailStr, Field  # type: ignore

from ....services.auth_service import AuthService
from ...deps import get_auth_service, get_current_user
from ....models.user import User

router = APIRouter()

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=3)

class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    full_name: str
    is_email_confirmed: bool

class Token(BaseModel):
    """Schema for access token"""
    access_token: str
    token_type: str
    user: UserResponse

class PasswordReset(BaseModel):
    """Schema for password reset"""
    email: EmailStr

class NewPassword(BaseModel):
    """Schema for setting a new password"""
    token: str
    password: str = Field(..., min_length=8)

class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8)

@router.post("/register", response_model=Dict[str, Any])
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    """
    try:
        user, confirmation_token = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # In a real app, you would send an email with the confirmation link
        # For this example, we'll just return the token
        return {
            "message": "User registered successfully. Please check your email to confirm your account.",
            # Only for demo purposes, don't expose tokens in production!
            "confirmation_token": confirmation_token
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = auth_service.authenticate_user(
        email=form_data.username,  # username field contains email in OAuth2 form
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(user_id=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_email_confirmed=user.is_email_confirmed
        )
    }

@router.get("/confirm-email/{token}", response_model=Dict[str, str])
async def confirm_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Confirm a user's email address with a confirmation token
    """
    if not auth_service.confirm_email(token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    return {"message": "Email confirmed successfully"}

@router.post("/request-password-reset", response_model=Dict[str, str])
async def request_password_reset(
    reset_data: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Request a password reset email
    """
    reset_token = auth_service.request_password_reset(email=reset_data.email)
    
    if reset_token:
        # In a real app, you would send an email with the reset link
        # For this example, we'll just return the token
        return {
            "message": "Password reset email sent. Please check your email.",
            # Only for demo purposes, don't expose tokens in production!
            "reset_token": reset_token
        }
    
    # Always return a success message even if email not found (security best practice)
    return {"message": "Password reset email sent if account exists. Please check your email."}

@router.post("/reset-password", response_model=Dict[str, str])
async def reset_password(
    password_data: NewPassword,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Reset password with a reset token
    """
    if not auth_service.reset_password(token=password_data.token, new_password=password_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    return {"message": "Password reset successful"}

@router.post("/change-password", response_model=Dict[str, str])
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change password for the current user
    """
    if not auth_service.change_password(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_email_confirmed=current_user.is_email_confirmed
    )