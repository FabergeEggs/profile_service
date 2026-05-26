from uuid import UUID
from typing import Optional, Dict, Any
from src.domain.entities import Profile
from src.domain.interfaces import ProfileRepository, EventProducer
from src.domain.exceptions import ProfileNotFoundError, InvalidProfileDataError
from src import kafka_topics as topics


class ProfileService:

    def __init__(
        self,
        repository: ProfileRepository,
        event_producer: EventProducer,
    ):
        self.repository = repository
        self.event_producer = event_producer

    async def get_profile(self, user_id: UUID) -> Optional[Profile]:
        return await self.repository.get_by_user_id(user_id)

    async def create_profile(
        self,
        user_id: UUID,
        username: str,
        email: str,
        first_name: str = "",
        last_name: str = "",
        bio: str = "",
    ) -> Profile:
        existing = await self.repository.get_by_user_id(user_id)
        if existing:
            return existing

        profile = Profile(
            id=None,
            user_id=user_id,
            username=username,
            email=email,
            first_name=first_name or "",
            last_name=last_name or "",
            bio=bio or "",
        )
        return await self.repository.create(profile)

    async def update_profile(self, user_id: UUID, updates: Dict[str, Any]) -> Profile:
        profile = await self.repository.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundError(str(user_id))

        allowed_fields = {"first_name", "last_name", "bio", "username", "email"}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise InvalidProfileDataError(f"Invalid fields: {invalid_fields}")

        old_values = {
            k: getattr(profile, k)
            for k in updates
            if hasattr(profile, k) and getattr(profile, k) != updates[k]
        }

        profile.update(**updates)
        updated_profile = await self.repository.update(profile)

        if old_values:
            await self._send_profile_changed(
                user_id=updated_profile.user_id,
                profile=updated_profile,
                changes=updates,
            )

        return updated_profile

    async def _send_profile_changed(
        self,
        user_id: UUID,
        profile: Profile,
        changes: dict,
    ) -> None:
        if not profile.id:
            return

        profile_changes: Dict[str, Any] = {}

        if "first_name" in changes or "last_name" in changes:
            first = changes.get("first_name", profile.first_name) or ""
            last = changes.get("last_name", profile.last_name) or ""
            profile_changes["name"] = f"{first} {last}".strip()

        if "email" in changes:
            profile_changes["email"] = changes["email"]

        if "username" in changes:
            profile_changes["username"] = changes["username"]

        if "bio" in changes:
            profile_changes["bio"] = changes["bio"]

        if not profile_changes:
            return

        await self.event_producer.send_event(
            topic=topics.PROFILE_CHANGED,
            event_type=topics.PROFILE_CHANGED,
            data={
                "profile_id": str(profile.id),
                "user_id": str(user_id),
                "changes": profile_changes,
            },
        )

    async def delete_profile(self, user_id: UUID) -> bool:
        profile = await self.repository.get_by_user_id(user_id)
        if not profile:
            return False

        deleted = await self.repository.delete(user_id)
        if deleted:
            await self.event_producer.send_event(
                topic=topics.USER_DELETED,
                event_type=topics.USER_DELETED,
                data={"user_id": str(user_id)},
            )
        return deleted
