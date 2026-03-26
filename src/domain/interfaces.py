from abc import ABC, abstractmethod
from domain.entities import User

class AuthenticationService(ABC):
    @abstractmethod
    async def authenticate(self, token: str) -> User:
        """Проверяет токен и возвращает пользователя"""
        raise NotImplementedError