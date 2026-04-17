from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_db
from src.infrastructure.repositories.profile_repository import PostgresProfileRepository
from src.infrastructure.message_broker.producer import KafkaEventProducer
from src.infrastructure.clients.media_client import MediaServiceHTTPClient
from src.infrastructure.auth.keycloak import keycloak_auth
from src.application.usecases.profile_service import ProfileService
from uuid import UUID

# Singleton instances
_event_producer = KafkaEventProducer()
_media_client = MediaServiceHTTPClient()

async def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    """Dependency for ProfileService with real implementations"""
    repository = PostgresProfileRepository(db)
    return ProfileService(repository, _event_producer, _media_client)

async def get_current_user(token_data = Depends(keycloak_auth.verify_token)) -> UUID:
    """Extract current user ID from Keycloak token"""
    return keycloak_auth.get_user_id(token_data)