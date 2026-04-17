import httpx
from typing import Optional
from src.domain.interfaces import MediaServiceClient
from src.core.config import settings

class MediaServiceHTTPClient(MediaServiceClient):
    def __init__(self):
        self.base_url = settings.media_service_url
    
    async def delete_avatar(self, avatar_url: str) -> bool:
        async with httpx.AsyncClient() as client:
            # Извлекаем ID аватара из URL
            avatar_id = avatar_url.split("/")[-1]
            response = await client.delete(
                f"{self.base_url}/avatar/{avatar_id}"
            )
            return response.status_code == 200