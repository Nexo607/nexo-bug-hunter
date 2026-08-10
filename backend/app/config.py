from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    app_name: str = "nexo-bug-hunter"
    version: str = "1.1.0"
    database_url: str = "sqlite:///./nexo.db"
    secret_key: str = "change-me"
    jwt_secret: str = "change-me"
    cors_origins: List[str] = ["http://localhost:5173"]
    request_timeout: float = 10.0
    max_concurrency: int = 4
    max_requests_per_scan: int = 100
    rate_limit_per_minute: int = 60
    max_target_length: int = 2048
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, value):
        if isinstance(value, str):
            return [x.strip() for x in value.split(",") if x.strip()]
        return value

settings = Settings()
