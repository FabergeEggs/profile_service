from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.profile_repository import PostgresProfileRepository
from src.infrastructure.message_broker.producer import get_event_producer
from src.infrastructure.auth.keycloak import keycloak_auth
from src.application.usecases.profile_service import ProfileService
from uuid import UUID


async def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    repository = PostgresProfileRepository(db)
    return ProfileService(repository, get_event_producer())


async def get_current_user(token_data=Depends(keycloak_auth.verify_token)) -> UUID:
    return keycloak_auth.get_user_id(token_data)
