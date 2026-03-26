from fastapi import APIRouter, Depends
from api.dependencies import get_current_user
from services.profile_service import ProfileService
from domain.entities import User

router = APIRouter()

def get_profile_service(
    session: AsyncSession = Depends(get_db),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> ProfileService:
    repo = SQLAlchemyProfileRepository(session)
    return ProfileService(repo, auth_service)

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    profile = await profile_service.get_profile(current_user.id)
    return profile

@router.post("/profile")
async def update_profile(
    bio: str = None,
    avatar_url: str = None,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    profile = await profile_service.create_or_update_profile(
        user_id=current_user.id,
        bio=bio,
        avatar_url=avatar_url
    )
    return profile