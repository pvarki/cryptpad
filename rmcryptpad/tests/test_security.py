"""Tests for mTLS trust boundaries."""

from __future__ import annotations

import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi import Request
from fastapi.testclient import TestClient

from rmcryptpad.web.application import get_app_no_init
from rmcryptpad.web.security import require_verified_mtls_header


def _build_cert_pem(common_name: str) -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(
            datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
        )
        .not_valid_after(
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30)
        )
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")


def _format_fingerprint_header(raw_fingerprint: str) -> str:
    return ":".join(
        raw_fingerprint[i : i + 2] for i in range(0, len(raw_fingerprint), 2)
    ).upper()


def test_missing_mtls_header_is_forbidden(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/users/created",
            json={
                "uuid": "uuid-a",
                "callsign": "VIRTA-1",
                "x509cert": _build_cert_pem("VIRTA-1"),
            },
        )
        assert response.status_code == 403


def test_forwarded_mtls_fingerprint_is_normalized(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    @app.get("/probe")
    async def probe(request: Request) -> dict[str, str | None]:
        require_verified_mtls_header(request)
        return {"fingerprint": getattr(request.state, "mtlsfingerprint", None)}

    with TestClient(app) as client:
        response = client.get(
            "/probe",
            headers={
                "X-ClientCert-DN": "CN=VIRTA-1,O=RM",
                "X-SSL-Client-Verify": "SUCCESS",
                "X-SSL-Client-Fingerprint": _format_fingerprint_header(
                    "aabbccddeeff00112233445566778899"
                ),
            },
        )

    assert response.status_code == 200
    assert response.json()["fingerprint"] == "aabbccddeeff00112233445566778899"


@pytest.mark.asyncio
async def test_unverified_proxy_header_is_forbidden(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/users/created",
            headers={
                "X-ClientCert-DN": "CN=rasenmaeher,O=RM",
                "X-SSL-Client-Verify": "FAILED",
            },
            json={
                "uuid": "uuid-a",
                "callsign": "VIRTA-1",
                "x509cert": _build_cert_pem("VIRTA-1"),
            },
        )
        assert response.status_code == 403
