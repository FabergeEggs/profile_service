import httpx
from typing import Optional
from src.domain.interfaces import MediaServiceClient
from src.core.config import settings

class MediaServiceHTTPClient(MediaServiceClient):
    def __init__(self):
        self.base_url = settings.media_service_url
        self.service_token = settings.media_service_token

    async def delete_avatar(self, avatar_url: str) -> bool:
        async with httpx.AsyncClient() as client:
            avatar_id = avatar_url.split("/")[-1]
            response = await client.delete(
                f"{self.base_url}/avatar/{avatar_id}",
                headers={"x-service-token": self.service_token}
            )
            return response.status_code in (200, 204)

    async def get_asset_download_url(self, asset_id: str) -> Optional[str]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/assets/{asset_id}",
                headers={"x-service-token": self.service_token}
            )
            if response.status_code == 200:
                body = response.json()
                return body.get("download", {}).get("url")
            return None