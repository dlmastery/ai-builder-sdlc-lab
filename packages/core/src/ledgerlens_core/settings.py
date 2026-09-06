"""Runtime configuration. Everything comes from the environment; secrets have no defaults."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BillingProvider = Literal["fake", "stripe"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    object_store_endpoint: str = "http://localhost:9000"
    object_store_access_key: str = "ledgerlens"
    object_store_secret_key: SecretStr = SecretStr("ledgerlens-secret")
    object_store_bucket: str = "ledgerlens"

    secret_key: SecretStr = Field(min_length=32)
    session_ttl_seconds: int = 60 * 60 * 24 * 14

    stripe_secret_key: SecretStr | None = None
    stripe_webhook_secret: SecretStr | None = None

    log_level: str = "INFO"
    environment: Literal["local", "test", "ci", "production"] = "local"
    low_vram: bool = False

    @property
    def billing_provider(self) -> BillingProvider:
        if self.stripe_secret_key and self.stripe_secret_key.get_secret_value():
            return "stripe"
        return "fake"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
