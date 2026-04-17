from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

@dataclass
class Event:
    event_id: UUID
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]

@dataclass
class ProfileChangedEvent(Event):
    def __init__(self, profile_id: UUID, user_id: UUID, changes: Dict[str, Any]):
        super().__init__(
            event_id=UUID(int=0),  # будет сгенерирован при отправке
            event_type="profile_service.profile.changed",
            timestamp=datetime.utcnow(),
            data={
                "profile_id": str(profile_id),
                "user_id": str(user_id),
                "changes": changes,
                "service_id": "profile-service"
            }
        )

@dataclass
class UserRegisteredEvent(Event):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(
            event_id=UUID(int=0),
            event_type="keycloak.user.registered",
            timestamp=datetime.utcnow(),
            data=data
        )