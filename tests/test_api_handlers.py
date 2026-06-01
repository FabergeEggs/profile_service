from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.dependencies import get_current_user, get_profile_service
from src.api.handlers import router
from src.domain.entities import Profile
from src.domain.exceptions import InvalidProfileDataError, ProfileNotFoundError


def _profile(user_id):
    return Profile(
        id=uuid4(),
        user_id=user_id,
        username="alice",
        email="alice@example.com",
        first_name="Ann",
        last_name="Bee",
    )


def test_get_profile_returns_403_for_other_user() -> None:
    user_id = uuid4()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: uuid4()
    app.dependency_overrides[get_profile_service] = lambda: AsyncMock()

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(f"/profile/{user_id}")

    assert response.status_code == 403


def test_get_profile_returns_200_for_owner() -> None:
    user_id = uuid4()
    profile = _profile(user_id)
    service = AsyncMock()
    service.get_profile.return_value = profile

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_profile_service] = lambda: service

    client = TestClient(app)
    response = client.get(f"/profile/{user_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Ann Bee"


def test_get_profile_returns_404_when_missing() -> None:
    user_id = uuid4()
    service = AsyncMock()
    service.get_profile.return_value = None

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_profile_service] = lambda: service

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(f"/profile/{user_id}")

    assert response.status_code == 404


def test_update_profile_returns_400_on_invalid_data() -> None:
    user_id = uuid4()
    service = AsyncMock()
    service.update_profile.side_effect = InvalidProfileDataError("bad field")

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_profile_service] = lambda: service

    client = TestClient(app, raise_server_exceptions=False)
    response = client.put(
        f"/profile/{user_id}",
        json={"first_name": "New", "last_name": "Name"},
    )

    assert response.status_code == 400


def test_delete_profile_returns_404_when_missing() -> None:
    user_id = uuid4()
    service = AsyncMock()
    service.delete_profile.return_value = False

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_profile_service] = lambda: service

    client = TestClient(app, raise_server_exceptions=False)
    response = client.delete(f"/profile/{user_id}")

    assert response.status_code == 404


def test_delete_profile_returns_200_when_deleted() -> None:
    user_id = uuid4()
    service = AsyncMock()
    service.delete_profile.return_value = True

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_profile_service] = lambda: service

    client = TestClient(app)
    response = client.delete(f"/profile/{user_id}")

    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()
