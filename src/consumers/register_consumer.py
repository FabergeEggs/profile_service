import logging
from typing import Dict, Any
from uuid import UUID

from src.application.usecases.profile_service import ProfileService
from src.infrastructure.database.session import AsyncSessionLocal
from src.infrastructure.repositories.profile_repository import PostgresProfileRepository
from src.infrastructure.message_broker.producer import get_event_producer
from src.domain.exceptions import InvalidProfileDataError

logger = logging.getLogger(__name__)


def _extract_user_payload(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """auth_service wraps fields in ``data``; support both shapes."""
    nested = event_data.get("data")
    if isinstance(nested, dict) and nested.get("user_id"):
        return nested
    return event_data


async def handle_user_registered(event_data: Dict[str, Any]) -> None:
    user_data = _extract_user_payload(event_data)
    user_id_raw = user_data.get("user_id")
    email = user_data.get("email")

    if not user_id_raw or not email:
        raise InvalidProfileDataError("Missing required user data: user_id and email")

    user_id = UUID(str(user_id_raw))
    first_name = user_data.get("first_name") or ""
    last_name = user_data.get("last_name") or ""
    bio = user_data.get("about") or ""

    async with AsyncSessionLocal() as db:
        try:
            repository = PostgresProfileRepository(db)
            profile_service = ProfileService(repository, get_event_producer())

            await profile_service.create_profile(
                user_id=user_id,
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                bio=bio,
            )
            await db.commit()
            logger.info("Profile created for user %s (email: %s)", user_id, email)
        except Exception as e:
            await db.rollback()
            logger.exception("Error creating profile for user %s: %s", user_id, e)
            raise
