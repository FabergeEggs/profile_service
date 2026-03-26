import httpx
from jose import jwt
from jose.exceptions import JWTError
from core.config import settings
from domain.entities import User
from domain.interfaces import AuthenticationService
from domain.exceptions import AuthenticationError

class KeycloakAuthService(AuthenticationService):
    def __init__(self):
        self.server_url = settings.KEYCLOAK_SERVER_URL
        self.realm = settings.KEYCLOAK_REALM
        self.client_id = settings.KEYCLOAK_CLIENT_ID
        self._public_key = None

    async def _get_public_key(self) -> str:
        if self._public_key:
            return self._public_key
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/certs"
            )
            resp.raise_for_status()
            data = resp.json()
            self._public_key = data["keys"][0]["x5c"][0]
            return self._public_key

    async def authenticate(self, token: str) -> User:
        try:
            public_key = await self._get_public_key()
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=f"{self.server_url}/realms/{self.realm}"
            )
        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {e}")
        except Exception as e:
            raise AuthenticationError(f"Token verification failed: {e}")

        user_id = payload.get("sub")
        username = payload.get("preferred_username")
        email = payload.get("email")
        roles = payload.get("realm_access", {}).get("roles", [])

        if not user_id or not username:
            raise AuthenticationError("Invalid token payload")

        return User(id=user_id, username=username, email=email, roles=roles)