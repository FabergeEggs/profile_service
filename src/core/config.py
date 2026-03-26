from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "myrealm"
    KEYCLOAK_CLIENT_ID: str = "myclient"
    KEYCLOAK_CLIENT_SECRET: str = "secret"          # если требуется для обмена кода
    KEYCLOAK_ALGORITHMS: list[str] = ["RS256"]
    
    class Config:
        env_file = ".env"

settings = Settings()