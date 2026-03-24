"""Test helpers for rmcryptpad."""

from __future__ import annotations

import asyncio
import shutil
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from pytest_docker.plugin import Services


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session")
def docker_compose_file() -> str:
    """Point pytest-docker at the local test compose file."""
    return str(ROOT / "tests" / "docker-compose.yml")


@pytest.fixture(scope="session", autouse=True)
def session_env_config() -> Generator[None, None, None]:
    """Shared env defaults for rmcryptpad tests."""
    patch = pytest.MonkeyPatch()
    oidc_key_dir = ROOT / ".pytest-oidc"
    patch.setenv("RMCRYPTPAD_DATABASE_PASSWORD", "rmcryptpadtestpwd")
    patch.setenv("RMCRYPTPAD_DATABASE_USER", "rmcryptpad")
    patch.setenv("RMCRYPTPAD_DATABASE_DATABASE", "rmcryptpad")
    patch.setenv("RMCRYPTPAD_DATABASE_DRIVER", "postgresql+psycopg2")
    patch.setenv("RMCRYPTPAD_OIDC_KEY_DIR", str(oidc_key_dir))
    patch.setenv("RMCRYPTPAD_OIDC_ISSUER", "https://rmcryptpad.localhost:8443")
    patch.setenv("RMCRYPTPAD_OIDC_CLIENT_ID", "cryptpad")
    patch.setenv("RMCRYPTPAD_OIDC_CLIENT_SECRET", "cryptpad-secret")
    patch.setenv("RMCRYPTPAD_OIDC_CODE_TTL_SECONDS", "300")
    patch.setenv("RMCRYPTPAD_OIDC_TOKEN_TTL_SECONDS", "3600")
    yield None
    shutil.rmtree(oidc_key_dir, ignore_errors=True)
    patch.undo()


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def dbinstance(
    docker_ip: str,
    docker_services: Services,
    session_env_config: None,
) -> AsyncGenerator[None, None]:
    """Start the test database and initialize the schema."""
    _ = session_env_config
    patch = pytest.MonkeyPatch()
    try:
        patch.setenv("RMCRYPTPAD_DATABASE_HOST", docker_ip)
        patch.setenv(
            "RMCRYPTPAD_DATABASE_PORT", str(docker_services.port_for("postgres", 5432))
        )
        from rmcryptpad.config import (
            DBSettings,
        )  # pylint: disable=import-outside-toplevel
        from rmcryptpad.oidc.keys import (
            OIDCKeyManager,
        )  # pylint: disable=import-outside-toplevel
        from rmcryptpad.db.engine import (
            EngineWrapper,
        )  # pylint: disable=import-outside-toplevel

        DBSettings._singleton = None
        EngineWrapper._singleton = None
        OIDCKeyManager._singleton = None
        await asyncio.sleep(1.0)
        from rmcryptpad.db.dbinit import (
            drop_db,
            init_db,
        )  # pylint: disable=import-outside-toplevel

        await init_db()
        yield None
        await drop_db()
    finally:
        patch.undo()
