from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: str
    username: str
    email: Optional[str] = None
    roles: list[str] = field(default_factory=list)

@dataclass
class Profile:
    user_id: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)