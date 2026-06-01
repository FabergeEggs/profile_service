import pytest
from pydantic import ValidationError

from src.api.dto import ProfileCreateDTO, ProfileUpdateDTO


def test_profile_create_dto_valid():
    dto = ProfileCreateDTO(username="alice", email="alice@example.com")
    assert dto.username == "alice"
    assert dto.email == "alice@example.com"


def test_profile_create_dto_invalid_email():
    with pytest.raises(ValidationError):
        ProfileCreateDTO(username="alice", email="not-an-email")


def test_profile_update_dto_forbids_extra_fields():
    with pytest.raises(ValidationError):
        ProfileUpdateDTO(first_name="Alice", unknown_field="x")


def test_profile_response_dto_computes_display_name():
    from datetime import datetime, timezone
    from uuid import uuid4

    from src.api.dto import ProfileResponseDTO

    dto = ProfileResponseDTO(
        id=uuid4(),
        user_id=uuid4(),
        username="alice",
        email="alice@example.com",
        first_name="Ann",
        last_name="Bee",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert dto.display_name == "Ann Bee"
