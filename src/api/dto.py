from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class ProfileDTO(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    description: Optional[str] = None
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class ProfileCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    description: Optional[str] = Field(default=None, max_length=500)


class ProfileUpdateDTO(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None


# Backward-compat with current handlers import (`from src.api.dto import User`)
User = ProfileUpdateDTO

