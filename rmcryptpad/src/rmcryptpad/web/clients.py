"""Client data routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ..config import RMCryptPadSettings
from ..db.user import User
from ..schema import ClientDataPayload, ClientDataResponse, UserCRUDRequest
from .security import require_mtls_header, require_rm_caller

router = APIRouter(dependencies=[Depends(require_mtls_header)])
router_admin = APIRouter(dependencies=[Depends(require_mtls_header)])


async def _build_client_data(user: UserCRUDRequest, request: Request) -> ClientDataResponse:
    require_rm_caller(request)
    await User.create_or_update(callsign=user.callsign, rmuuid=user.uuid, cert_pem=user.x509cert)
    settings = RMCryptPadSettings.singleton()
    return ClientDataResponse(
        data=ClientDataPayload(
            url=settings.public_url,
            sandbox_url=settings.public_sandbox_url,
            docs_url=settings.docs_url,
            oidc_issuer=settings.oidc_issuer,
        )
    )


@router.post("/clients/data", response_model=ClientDataResponse)
async def client_data(user: UserCRUDRequest, request: Request) -> ClientDataResponse:
    return await _build_client_data(user, request)


@router_admin.post("/admin/clients/data", response_model=ClientDataResponse)
async def admin_client_data(user: UserCRUDRequest, request: Request) -> ClientDataResponse:
    return await _build_client_data(user, request)
