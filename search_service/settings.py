from pathlib import Path

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    SERVICE_TOKEN: str

    RABBITMQ_URL: AnyUrl

    MONGODB_URL: AnyUrl
    MONGO_DB_NAME: str
    MONGODB_COLLECTION: str

    LOG_FILE: str

    @property
    def log_file_path(self) -> Path:
        return BASE_DIR / self.LOG_FILE

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        frozen=True
    )
