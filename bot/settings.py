from pathlib import Path

from pydantic import HttpUrl, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    TOKEN: str

    SERVICE_TOKEN: str

    RABBITMQ_URL: AnyUrl

    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int

    SEARCH_SERVICE_URL: HttpUrl

    LOG_FILE: str

    @property
    def log_file_path(self) -> Path:
        return BASE_DIR / self.LOG_FILE

    @property
    def redis_url(self) -> str:
        return (
            f"redis://:{self.REDIS_PASSWORD}@"
            f"{self.REDIS_HOST}:{self.REDIS_PORT}"
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        frozen=True
    )
