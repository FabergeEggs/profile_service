from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.entities import Profile
from domain.repositories import ProfileRepository
from infrastructure.orm.models import ProfileModel

class SQLAlchemyProfileRepository(ProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_user_id(self, user_id: str) -> Profile | None:
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Profile(
            user_id=model.user_id,
            bio=model.bio,
            avatar_url=model.avatar_url,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    async def save(self, profile: Profile) -> None:
        model = ProfileModel(
            user_id=profile.user_id,
            bio=profile.bio,
            avatar_url=profile.avatar_url,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        await self.session.merge(model)
        await self.session.commit()
    
    async def delete(self, user_id: str) -> None:
        await self.session.execute(
            delete(ProfileModel).where(ProfileModel.user_id == user_id)
        )
        await self.session.commit()