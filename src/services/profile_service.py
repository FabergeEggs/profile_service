# services/profile_service.py
from domain.entities import User, Profile
from domain.repositories import ProfileRepository
from domain.interfaces import AuthenticationService
from domain.exceptions import ProfileNotFoundError

class ProfileService:
    """Use case: управление профилями пользователей"""
    
    def __init__(
        self,
        profile_repo: ProfileRepository,
        auth_service: AuthenticationService
    ):
        self.profile_repo = profile_repo
        self.auth_service = auth_service
    
    async def get_profile(self, user_id: str) -> Profile:
        """Получить профиль пользователя"""
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundError(f"Profile not found for user {user_id}")
        return profile
    
    async def create_or_update_profile(
        self, 
        user_id: str, 
        bio: str = None,
        avatar_url: str = None
    ) -> Profile:
        """Создать или обновить профиль"""
        profile = await self.profile_repo.get_by_user_id(user_id)
        
        if profile:
            # Обновляем существующий
            profile.bio = bio or profile.bio
            profile.avatar_url = avatar_url or profile.avatar_url
        else:
            # Создаём новый
            profile = Profile(
                user_id=user_id,
                bio=bio,
                avatar_url=avatar_url
            )
        
        await self.profile_repo.save(profile)
        return profile
    
    async def delete_profile(self, user_id: str) -> None:
        """Удалить профиль"""
        await self.profile_repo.delete(user_id)