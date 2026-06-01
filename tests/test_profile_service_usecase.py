from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from src.application.usecases.profile_service import ProfileService
from src.domain.entities import Profile
from src.domain.entities import Profile
from src.domain.exceptions import InvalidProfileDataError, ProfileNotFoundError


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def profile(user_id):
    return Profile(
        id=uuid4(),
        user_id=user_id,
        username="user@example.com",
        email="user@example.com",
        first_name="Ann",
        last_name="Bee",
    )


@pytest.fixture
def repository(profile):
    repo = AsyncMock()
    repo.get_by_user_id = AsyncMock(return_value=profile)
    repo.create = AsyncMock(return_value=profile)
    repo.update = AsyncMock(return_value=profile)
    repo.delete = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def event_producer():
    return AsyncMock()


@pytest.fixture
def service(repository, event_producer):
    return ProfileService(repository, event_producer)


@pytest.mark.asyncio
async def test_create_profile_is_idempotent(service, repository, profile, user_id):
    created = await service.create_profile(
        user_id=user_id,
        username=profile.email,
        email=profile.email,
    )
    assert created == profile
    repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_profile_sends_event(service, repository, event_producer, user_id):
    deleted = await service.delete_profile(user_id)

    assert deleted is True
    repository.delete.assert_awaited_once_with(user_id)
    event_producer.send_event.assert_awaited_once()
    kwargs = event_producer.send_event.await_args.kwargs
    assert kwargs["topic"] == "profile_service.user.deleted"
    assert kwargs["event_type"] == "profile_service.user.deleted"
    assert kwargs["data"]["user_id"] == str(user_id)


@pytest.mark.asyncio
async def test_delete_profile_returns_false_when_missing(service, repository, user_id):
    repository.get_by_user_id.return_value = None

    deleted = await service.delete_profile(user_id)

    assert deleted is False
    repository.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_profile_raises_if_not_found(service, repository, user_id):
    repository.get_by_user_id.return_value = None

    with pytest.raises(ProfileNotFoundError):
        await service.update_profile(user_id, {"first_name": "New"})


@pytest.mark.asyncio
async def test_create_profile_creates_when_missing(
    service, repository, user_id, profile
):
    repository.get_by_user_id.return_value = None
    repository.create.return_value = profile

    created = await service.create_profile(
        user_id=user_id,
        username="new@example.com",
        email="new@example.com",
        first_name="New",
    )

    assert created == profile
    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_profile_sends_profile_changed_event(
    service, repository, event_producer, user_id, profile
):
    updated = Profile(
        id=profile.id,
        user_id=user_id,
        username=profile.username,
        email=profile.email,
        first_name="Changed",
        last_name=profile.last_name,
    )
    repository.update.return_value = updated

    result = await service.update_profile(user_id, {"first_name": "Changed"})

    assert result.first_name == "Changed"
    event_producer.send_event.assert_awaited_once()
    kwargs = event_producer.send_event.await_args.kwargs
    assert kwargs["topic"] == "profile_service.profile.changed"
    assert kwargs["data"]["changes"]["name"] == "Changed Bee"


@pytest.mark.asyncio
async def test_update_profile_raises_on_invalid_fields(service, repository, user_id, profile):
    with pytest.raises(InvalidProfileDataError):
        await service.update_profile(user_id, {"role": "admin"})


@pytest.mark.asyncio
async def test_update_profile_skips_event_when_values_unchanged(
    service, repository, event_producer, user_id, profile
):
    await service.update_profile(user_id, {"first_name": profile.first_name})

    event_producer.send_event.assert_not_called()
