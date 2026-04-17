from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from uuid import UUID
from src.domain.entities import Profile

class ProfileRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[Profile]:
        pass
    
    @abstractmethod
    async def create(self, profile: Profile) -> Profile:
        pass
    
    @abstractmethod
    async def update(self, profile: Profile) -> Profile:
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass

class EventProducer(ABC):
    @abstractmethod
    async def send_event(self, event_type: str, data: Dict[str, Any]) -> None:
        pass

class MediaServiceClient(ABC):
    @abstractmethod
    async def delete_avatar(self, avatar_url: str) -> bool:
        pass