import json
from typing import Dict, Any
from uuid import UUID
from src.application.usecases.profile_service import ProfileService
from src.infrastructure.database.session import AsyncSessionLocal
from src.infrastructure.repositories.profile_repository import PostgresProfileRepository
from src.infrastructure.message_broker.producer import KafkaEventProducer
from src.infrastructure.clients.media_client import MediaServiceHTTPClient
from src.domain.exceptions import InvalidProfileDataError

# Shared instances
_event_producer = KafkaEventProducer()
_media_client = MediaServiceHTTPClient()

async def handle_user_registered(event_data: Dict[str, Any]) -> None:
    """Handle keycloak.user.registered event"""
    try:
        # Extract user data from event
        user_data = event_data.get("data", {})
        user_id = UUID(user_data.get("user_id"))
        username = user_data.get("username")
        email = user_data.get("email")
        
        if not all([user_id, username, email]):
            raise InvalidProfileDataError("Missing required user data")
        
        async with AsyncSessionLocal() as db:
            repository = PostgresProfileRepository(db)
            profile_service = ProfileService(repository, _event_producer, _media_client)
            
            # Create profile for new user
            profile = await profile_service.create_profile(user_id, username, email)
            await db.commit()
            
            print(f"Profile created for user: {user_id} (username: {username})")
            
    except InvalidProfileDataError as e:
        print(f"Invalid registration data: {e}")
    except Exception as e:
        print(f"Error creating profile: {e}")
        # Optionally send to dead letter queue