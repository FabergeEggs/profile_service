from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = Field(validation_alias="DATABASE_URL")
    
    # RedPanda
    redpanda_bootstrap_servers: str = Field(
        default="localhost:9092",
        validation_alias="REDPANDA_BOOTSTRAP_SERVERS"
    )
    redpanda_consumer_group: str = Field(
        default="profile-service-group",
        validation_alias="REDPANDA_CONSUMER_GROUP"
    )
    
    # Keycloak
    keycloak_url: str = Field(validation_alias="KEYCLOAK_URL")
    keycloak_realm: str = Field(validation_alias="KEYCLOAK_REALM")
    keycloak_client_id: str = Field(validation_alias="KEYCLOAK_CLIENT_ID")
    keycloak_client_secret: str = Field(validation_alias="KEYCLOAK_CLIENT_SECRET")
    
    # Media Service
    media_service_url: str = Field(validation_alias="MEDIA_SERVICE_URL")
    media_service_token: str = Field(
        default="",
        validation_alias="MEDIA_SERVICE_TOKEN"
    )
    
    # Service
    service_id: str = Field(
        default="profile-service",
        validation_alias="SERVICE_ID"
    )
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "populate_by_name": True,  # Позволяет использовать имена полей
        "case_sensitive": False
    }

settings = Settings()