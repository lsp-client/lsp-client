from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LSP_CLIENT_",
        env_file=".env",
        extra="ignore",
    )

    disable_auto_installation: bool = False


settings = Settings()
