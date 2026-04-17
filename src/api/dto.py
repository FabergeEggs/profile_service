from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class ProfileResponseDTO(BaseModel):
    """Response DTO for profile data"""
    id: UUID
    user_id: UUID
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProfileUpdateDTO(BaseModel):
    """Request DTO for profile update"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    
    class Config:
        extra = "forbid"  # Запрещаем лишние поля

class ProfileCreateDTO(BaseModel):
    """Request DTO for profile creation"""
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    class Config:
        extra = "forbid"

class ErrorResponseDTO(BaseModel):
    """Error response DTO"""
    error: str
    detail: Optional[str] = None
    status_code: int