from abc import ABC, abstractmethod
from domain.entities import Profile

class ProfileRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Profile | None:
        raise NotImplementedError
    
    @abstractmethod
    async def save(self, profile: Profile) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, user_id: str) -> None:
        raise NotImplementedError