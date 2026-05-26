from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional
from src.domain.entities import Profile
from src.domain.interfaces import ProfileRepository
from src.infrastructure.database.models import ProfileModel


class PostgresProfileRepository(ProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[Profile]:
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, profile: Profile) -> Profile:
        model = ProfileModel(
            user_id=profile.user_id,
            username=profile.username,
            email=profile.email,
            first_name=profile.first_name,
            last_name=profile.last_name,
            bio=profile.bio,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, profile: Profile) -> Profile:
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.user_id == profile.user_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Profile not found for user: {profile.user_id}")

        model.username = profile.username
        model.email = profile.email
        model.first_name = profile.first_name
        model.last_name = profile.last_name
        model.bio = profile.bio

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False

        await self.session.delete(model)
        await self.session.flush()
        return True

    def _to_entity(self, model: ProfileModel) -> Profile:
        return Profile(
            id=model.id,
            user_id=model.user_id,
            username=model.username,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            bio=model.bio,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
