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
