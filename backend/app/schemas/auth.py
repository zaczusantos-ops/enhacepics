"""
ChurchPhoto Pro - Pydantic Schemas for Authentication & User Accounts
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class GoogleLoginRequest(BaseModel):
    """
    Credential JWT token received from Google Identity Services (GIS) on frontend.
    """
    credential: str = Field(..., description="Google ID Token JWT string")
    client_id: Optional[str] = Field(None, description="Google OAuth Client ID if specified")


class EmailLoginRequest(BaseModel):
    """
    Traditional email and password login.
    """
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=4, description="User password")


class EmailRegisterRequest(BaseModel):
    """
    New account registration.
    """
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=4, description="User password")
    name: str = Field(..., min_length=2, description="Volunteer / User Full Name")
    church_name: Optional[str] = Field("Igreja Local", description="Church or Media Team Name")


class UserProfile(BaseModel):
    """
    Public user profile information.
    """
    id: str = Field(..., description="Unique User ID")
    email: str = Field(..., description="User Email")
    name: str = Field(..., description="User Name")
    picture: Optional[str] = Field(None, description="Avatar image URL from Google or placeholder")
    provider: str = Field("google", description="Auth provider: 'google' or 'email'")
    church_name: Optional[str] = Field("Igreja Local", description="Church Name")
    role: str = Field("volunteer", description="Role: 'volunteer', 'leader', 'admin'")
    created_at: str = Field(..., description="ISO 8601 created date")
    photos_processed_count: int = Field(0, description="Total photos processed by this user")


class AuthResponse(BaseModel):
    """
    Standard response returned on successful login or registration.
    """
    success: bool
    token: str = Field(..., description="Application JWT bearer token")
    user: UserProfile
    message: Optional[str] = "Autenticação realizada com sucesso."
