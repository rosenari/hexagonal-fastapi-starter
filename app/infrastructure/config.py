from typing import Optional

from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application settings
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    api_version: str = Field(default="v1", alias="API_VERSION")
    
    # Security settings
    secret_key: Optional[str] = Field(default=None, alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # Database settings
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    
    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Logging settings
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if info.data.get("environment") == "production" and not v:
            raise ValueError("SECRET_KEY must be set in production environment")
        return v
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if info.data.get("environment") == "production" and not v:
            raise ValueError("DATABASE_URL must be set in production environment")
        return v


settings = Settings()