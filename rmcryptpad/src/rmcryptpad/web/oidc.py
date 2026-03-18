"""OIDC provider routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from ..oidc import OIDCProvider
from .security import require_verified_mtls_header

router = APIRouter()


@router.get("/.well-known/openid-configuration")
async def discovery() -> JSONResponse:
    return JSONResponse(OIDCProvider().discovery_document())


@router.get("/oidc/jwks.json")
async def jwks() -> JSONResponse:
    return JSONResponse(OIDCProvider().jwks_document())


@router.get("/oidc/authorize", dependencies=[Depends(require_verified_mtls_header)])
async def authorize(request: Request):
    return await OIDCProvider().authorize(request)


@router.post("/oidc/token")
async def token(request: Request) -> JSONResponse:
    return JSONResponse(await OIDCProvider().token(request))


@router.get("/oidc/userinfo")
async def userinfo(request: Request) -> JSONResponse:
    return JSONResponse(await OIDCProvider().userinfo(request))
