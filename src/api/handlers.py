from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from src.api.dto import ProfileResponseDTO, ProfileUpdateDTO, ErrorResponseDTO
from src.api.dependencies import get_profile_service, get_current_user
from src.application.usecases.profile_service import ProfileService
from src.domain.exceptions import ProfileNotFoundError, UnauthorizedAccessError, InvalidProfileDataError

router = APIRouter(prefix="/profile", tags=["profile"])

# Internal S2S router — not exposed via KrakenD, only reachable on Docker network
internal_router = APIRouter(prefix="/internal/profile", tags=["internal"])


@internal_router.get("/{user_id}", response_model=ProfileResponseDTO)
async def get_profile_internal(
    user_id: UUID,
    profile_service: ProfileService = Depends(get_profile_service),
):
    """S2S: read any profile without JWT. Only reachable inside Docker network."""
    try:
        profile = await profile_service.get_profile(user_id)
        if not profile:
            raise ProfileNotFoundError(str(user_id))
        return ProfileResponseDTO.model_validate(profile)
    except ProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{user_id}",
    response_model=ProfileResponseDTO,
    responses={404: {"model": ErrorResponseDTO},
               403: {"model": ErrorResponseDTO}}
)
async def get_profile(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get profile by user ID"""
    # Authorization
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own profile"
        )

    try:
        profile = await profile_service.get_profile(user_id)
        if not profile:
            raise ProfileNotFoundError(str(user_id))

        return ProfileResponseDTO.model_validate(profile)
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{user_id}",
    response_model=ProfileResponseDTO,
    responses={404: {"model": ErrorResponseDTO},
               400: {"model": ErrorResponseDTO}}
)
async def update_profile(
    user_id: UUID,
    updates: ProfileUpdateDTO,
    current_user_id: UUID = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update profile"""
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )

    try:
        # Filter out None values
        update_data = {k: v for k, v in updates.dict().items()
                       if v is not None}
        profile = await profile_service.update_profile(user_id, update_data)
        return ProfileResponseDTO.model_validate(profile)
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidProfileDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{user_id}",
    responses={404: {"model": ErrorResponseDTO},
               200: {"description": "Profile deleted"}}
)
async def delete_profile(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Delete profile"""
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own profile"
        )

    deleted = await profile_service.delete_profile(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return {"message": "Profile deleted successfully"}
