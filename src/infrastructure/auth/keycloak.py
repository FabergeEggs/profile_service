from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from uuid import UUID
import os
import json
import jwt
import requests

security = HTTPBearer(auto_error=False)

class KeycloakAuth:
    def __init__(self):
        self.skip_auth = os.getenv("SKIP_AUTH", "true").lower() == "true"
        self.keycloak_url = os.getenv("KEYCLOAK_URL", "http://host.docker.internal:8082")
        self.realm = os.getenv("KEYCLOAK_REALM", "myrealm")
    
    def _get_public_key(self):
        url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/certs"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                raise Exception(f"Failed to get certs: {response.status_code}")
            jwks = response.json()
            for key in jwks.get("keys", []):
                if key.get("alg") == "RS256" or key.get("use") == "sig":
                    from jwt.algorithms import RSAAlgorithm
                    return RSAAlgorithm.from_jwt(json.dumps(key))
            raise Exception("No signing key found")
        except Exception as e:
            print(f"Error getting public key: {e}")
            raise
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        if self.skip_auth:
            return {"sub": "f16b9f8f-e006-45d3-a184-83bfa004f714"}
        
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = credentials.credentials
        
        try:
            public_key = self._get_public_key()
            payload = jwt.decode(token, public_key, algorithms=["RS256"], options={"verify_aud": False})
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    def get_user_id(self, token_data: Dict[str, Any]) -> UUID:
        if self.skip_auth:
            return UUID("f16b9f8f-e006-45d3-a184-83bfa004f714")
        user_id = token_data.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UUID(user_id)

keycloak_auth = KeycloakAuth()
