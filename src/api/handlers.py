from fastapi import FastAPI
from uuid import UUID
from datetime import datetime, timezone

from src.api.dto import ProfileDTO, ProfileUpdateDTO

app = FastAPI(title="Profile Service API")

@app.get("/who_i_am")
def who_i_am():
    return {"message": "I am profile service!"}

# @app.get("/profile")
@app.get("/")
def get_profiles(skip: int = 0, limit: int = 10):  # query params
    return {
        "message": "Return List Of Users",
        "skip": skip,
        "limit": limit
    }

@app.get("/{id}", response_model=ProfileDTO)
def get_profile(id: UUID) -> ProfileDTO:
    return ProfileDTO(
        id=id,
        name="Your Name",
        email="user@example.com",
        description=None,
        created_at=datetime.now(tz=timezone.utc),
        is_active=True,
    )

@app.put("/{id}")
def update_profile(id: UUID, profile: ProfileUpdateDTO) -> dict:
    return {"message": "User Updated", "id": str(id), "patch": profile.model_dump(exclude_unset=True)}
