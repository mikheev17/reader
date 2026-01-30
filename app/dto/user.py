"""
User-related Data Transfer Objects.
"""

from pydantic import BaseModel, EmailStr


class UserSignupRequest(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str


class UserSigninRequest(BaseModel):
    """Schema for user authentication."""
    email: EmailStr
    password: str
