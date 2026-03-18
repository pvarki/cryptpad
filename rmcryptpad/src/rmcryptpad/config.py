"""Application settings."""

from __future__ import annotations

from typing import ClassVar, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class RMCryptPadSettings(BaseSettings):
    """Runtime settings for rmcryptpad."""

    rmcn: str = "rasenmaeher"
    public_url: str = "https://cryptpad.localhost:8443"
    public_sandbox_url: str = "https://sandbox.cryptpad.localhost:8443"
    oidc_issuer: str = "https://rmcryptpad.localhost:8443"

    model_config = SettingsConfigDict(env_prefix="RMCRYPTPAD_", extra="ignore")

    _singleton: ClassVar[Optional["RMCryptPadSettings"]] = None

    @classmethod
    def singleton(cls) -> "RMCryptPadSettings":
        """Return a cached settings instance."""
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton
