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
        """Use case: Get profile by user ID"""
        profile = await self.repository.get_by_user_id(user_id)
        if profile and profile.avatar_asset_id:
            try:
                fresh_url = await self.media_client.get_asset_download_url(profile.avatar_asset_id)
                if fresh_url:
                    profile.avatar_url = fresh_url
            except Exception:
                pass  # graceful degradation: show stale/no avatar rather than fail
        return profile

    async def create_profile(self, user_id: UUID, username: str, email: str,
                             first_name: str = "", last_name: str = "",
                             bio: str = "") -> Profile:
        """Use case: Create new profile"""
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

        allowed_fields = {'first_name', 'last_name', 'bio', 'username', 'email', 'avatar_url', 'avatar_asset_id'}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise InvalidProfileDataError(f"Invalid fields: {invalid_fields}")

        # When storing by asset_id, clear the stale direct URL to avoid confusion
        if updates.get('avatar_asset_id'):
            updates['avatar_url'] = None

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

    async def _send_profile_events(
        self,
        user_id: UUID,
        profile: Profile,
        changes: dict,
        old_values: dict
    ):
        # Publish name change if either name part was updated.
        # profile already has the new values after repository.update().
        if 'first_name' in changes or 'last_name' in changes:
            name = f"{profile.first_name} {profile.last_name}".strip()
            await self.event_producer.send_event(
                topic="user-events",
                event_type="user.profile.updated",
                data={
                    "user_id": str(user_id),
                    "name": name
                }
            )

        if 'email' in changes:
            await self.event_producer.send_event(
                topic="user-events",
                event_type="user.email.updated",
                data={
                    "user_id": str(user_id),
                    "email": changes['email']
                }
            )

        if 'avatar_url' in changes:
            await self.event_producer.send_event(
                topic="user-events",
                event_type="user.avatar.updated",
                data={
                    "user_id": str(user_id),
                    "avatar_link": changes['avatar_url']
                }
            )

    async def delete_profile(self, user_id: UUID) -> bool:
        """Use case: Delete profile"""
        profile = await self.repository.get_by_user_id(user_id)

        # Delete avatar from media service if exists
        if profile and profile.avatar_url:
            try:
                await self.media_client.delete_avatar(profile.avatar_url)
            except Exception as e:
                print(f"Failed to delete avatar: {e}")

        return await self.repository.delete(user_id)
