"""FastAPI application factory for rmcryptpad."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from .. import __version__
from ..config import RMCryptPadSettings

LOGGER = logging.getLogger(__name__)


def get_app_no_init() -> FastAPI:
    """Return the application without logging bootstrap."""
    app = FastAPI(
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        title="RM CryptPad integration API",
        version=__version__,
    )

    @app.get("/healthcheck")
    async def healthcheck() -> dict[str, bool]:
        return {"healthy": True}

    return app


def get_app() -> FastAPI:
    """Return the application with logging initialized."""
    settings = RMCryptPadSettings.singleton()
    LOGGER.debug("Active config: %s", settings)
    return get_app_no_init()
