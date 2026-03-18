"""Lightweight mTLS header helpers."""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from ..config import RMCryptPadSettings

CLIENT_DN_HEADER = "X-ClientCert-DN"
CLIENT_FINGERPRINT_HEADER = "X-SSL-Client-Fingerprint"


def extract_cn(distinguished_name: str) -> str | None:
    """Extract the CN component from a distinguished name string."""
    for part in distinguished_name.split(","):
        key, sep, value = part.partition("=")
        if key.strip().upper() == "CN" and sep:
            return value.strip()
    return None


def require_mtls_header(request: Request) -> str:
    """Require a forwarded client certificate DN header."""
    dn = request.headers.get(CLIENT_DN_HEADER)
    if not dn:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing client certificate header")
    request.state.mtlsdn = {"DN": dn, "CN": extract_cn(dn) or dn.strip()}
    request.state.mtlsfingerprint = request.headers.get(CLIENT_FINGERPRINT_HEADER)
    return dn


def get_client_cn(request: Request) -> str:
    """Return the forwarded client CN."""
    dn = require_mtls_header(request)
    cn = extract_cn(dn)
    return cn or dn.strip()


def require_rm_caller(request: Request) -> None:
    """Ensure the caller is the Rasenmaeher control plane."""
    if get_client_cn(request) != RMCryptPadSettings.singleton().rmcn:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
