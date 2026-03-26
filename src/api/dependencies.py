from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from domain.interfaces import AuthenticationService
from domain.exceptions import AuthenticationError
from domain.entities import User

security = HTTPBearer(auto_error=False)

def get_auth_service() -> AuthenticationService:
    # Фабрика – подстановка реальной реализации
    from infrastructure.auth.keycloak_service import KeycloakAuthService
    return KeycloakAuthService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await auth_service.authenticate(credentials.credentials)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )