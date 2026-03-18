"""Application settings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Optional


@dataclass(slots=True)
class RMCryptPadSettings:
    """Runtime settings for rmcryptpad."""

    rmcn: str = "rasenmaeher"
    public_url: str = "https://cryptpad.localhost:8443"
    public_sandbox_url: str = "https://sandbox.cryptpad.localhost:8443"
    oidc_issuer: str = "https://rmcryptpad.localhost:8443"

    _singleton: ClassVar[Optional["RMCryptPadSettings"]] = None

    @classmethod
    def singleton(cls) -> "RMCryptPadSettings":
        """Return a cached settings instance."""
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton
