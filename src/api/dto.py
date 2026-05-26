from pydantic import BaseModel, Field, computed_field
from uuid import UUID
from datetime import datetime
from typing import Optional

from src.domain.display_name import build_display_name


class ProfileResponseDTO(BaseModel):
    """Response DTO for profile data"""
    id: UUID
    user_id: UUID
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def display_name(self) -> str:
        return build_display_name(
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            email=self.email,
        )

    class Config:
        from_attributes = True


class ProfileUpdateDTO(BaseModel):
    """Request DTO for profile update"""
    first_name: str
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    
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