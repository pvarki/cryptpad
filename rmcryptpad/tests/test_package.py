from rmcryptpad import __version__
from rmcryptpad.config import RMCryptPadSettings


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_settings_defaults() -> None:
    settings = RMCryptPadSettings.singleton()
    assert settings.rmcn == "rasenmaeher"
    assert settings.public_url == "https://cryptpad.localhost:8443"
    assert settings.public_sandbox_url == "https://sandbox.cryptpad.localhost:8443"
    assert settings.oidc_issuer == "https://rmcryptpad.localhost:8443"
