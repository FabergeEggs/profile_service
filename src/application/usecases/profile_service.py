from uuid import UUID
from typing import Optional, Dict, Any
from src.domain.entities import Profile
from src.domain.interfaces import ProfileRepository, EventProducer, MediaServiceClient
from src.domain.exceptions import ProfileNotFoundError, InvalidProfileDataError


class ProfileService:

    def __init__(
        self,
        repository: ProfileRepository,
        event_producer: EventProducer,
        media_client: MediaServiceClient
    ):
        self.repository = repository
        self.event_producer = event_producer
        self.media_client = media_client

    async def get_profile(self, user_id: UUID) -> Optional[Profile]:
        return await self.repository.get_by_user_id(user_id)

    async def create_profile(self, user_id: UUID, username: str, email: str,
                             first_name: str = "", last_name: str = "",
                             bio: str = "") -> Profile:
        profile = Profile(
            id=None,
            user_id=user_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            avatar_url=None
        )
        return await self.repository.create(profile)

    async def update_profile(self, user_id: UUID, updates: Dict[str, Any]) -> Profile:
        profile = await self.repository.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundError(str(user_id))

        allowed_fields = {'first_name', 'last_name', 'bio', 'username', 'email', 'avatar_url'}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise InvalidProfileDataError(f"Invalid fields: {invalid_fields}")

        old_values = {
            k: getattr(profile, k)
            for k in updates.keys()
            if hasattr(profile, k) and getattr(profile, k) != updates[k]
        }

        profile.update(**updates)
        updated_profile = await self.repository.update(profile)

        if old_values and self.event_producer:
            await self._send_profile_events(
                user_id=updated_profile.user_id,
                profile=updated_profile,
                changes=updates,
                old_values=old_values
            )

        return updated_profile

    async def delete_profile(self, user_id: UUID) -> bool:
        profile = await self.repository.get_by_user_id(user_id)

        if profile and profile.avatar_url:
            try:
                await self.media_client.delete_avatar(profile.avatar_url)
            except Exception as e:
                print(f"Failed to delete avatar: {e}")

        return await self.repository.delete(user_id)

    async def _send_profile_events(
        self,
        user_id: UUID,
        profile: Profile,
        changes: dict,
        old_values: dict
    ):
        if 'first_name' in changes:
            name = f"{changes['first_name']} {profile.last_name}".strip()
            await self.event_producer.send_event(
                topic="user-events",
                event_type="user.profile.updated",
                data={"user_id": str(user_id), "name": name}
            )

        if 'email' in changes:
            await self.event_producer.send_event(
                topic="user-events",
                event_type="user.email.updated",
                data={"user_id": str(user_id), "email": changes['email']}
            )

        elif 'last_name' in changes and 'first_name' not in changes:
            name = f"{profile.first_name} {changes['last_name']}".strip()
            await self.event_producer.send_event(
                topic="user-events",
                event_type="user.profile.updated",
                data={"user_id": str(user_id), "name": name}
            )
