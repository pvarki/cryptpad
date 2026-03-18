"""Instructions routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ..db.user import User
from ..schema import InstructionsResponse, UserCRUDRequest
from .security import require_mtls_header, require_rm_caller

router = APIRouter(dependencies=[Depends(require_mtls_header)])


@router.post("/instructions/{language}", response_model=InstructionsResponse)
async def user_instructions(user: UserCRUDRequest, request: Request, language: str) -> InstructionsResponse:
    """Return product guidance for the current callsign."""
    require_rm_caller(request)
    await User.create_or_update(callsign=user.callsign, rmuuid=user.uuid, cert_pem=user.x509cert)
    return InstructionsResponse(
        callsign=user.callsign,
        language=language,
        instructions="Open CryptPad through the Deploy App mTLS host and keep the certificate-backed account in sync.",
    )
