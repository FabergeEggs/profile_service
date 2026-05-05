import json
from typing import Dict, Any
from uuid import UUID
from src.application.usecases.profile_service import ProfileService
from src.infrastructure.database.session import AsyncSessionLocal
from src.infrastructure.repositories.profile_repository import PostgresProfileRepository
from src.infrastructure.message_broker.producer import KafkaEventProducer
from src.infrastructure.clients.media_client import MediaServiceHTTPClient
from src.domain.exceptions import InvalidProfileDataError

_event_producer = KafkaEventProducer()
_media_client = MediaServiceHTTPClient()

async def handle_user_registered(event_data: Dict[str, Any]) -> None:
    try:
        user_data = event_data.get("data", {})
        user_id = UUID(user_data.get("user_id"))
        email = user_data.get("email")
        username = email
        first_name = user_data.get("first_name")
        last_name = user_data.get("last_name")
        about = user_data.get("about")  
        
        if not all([user_id, email]):
            raise InvalidProfileDataError("Missing required user data")
        
        async with AsyncSessionLocal() as db:
            repository = PostgresProfileRepository(db)
            profile_service = ProfileService(repository, _event_producer, _media_client)
            
            profile = await profile_service.create_profile(
                user_id=user_id,
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                bio=about
            )
            await db.commit()
            
            print(f"Profile created for user: {user_id} (email: {email})")
            
    except Exception as e:
        print(f"Error creating profile: {e}")