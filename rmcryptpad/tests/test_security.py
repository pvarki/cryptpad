"""Tests for mTLS trust boundaries."""

from __future__ import annotations

import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi.testclient import TestClient

from rmcryptpad.web.application import get_app_no_init


def _build_cert_pem(common_name: str) -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")


def test_missing_mtls_header_is_forbidden(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/users/created",
            json={"uuid": "uuid-a", "callsign": "VIRTA-1", "x509cert": _build_cert_pem("VIRTA-1")},
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_unverified_proxy_header_is_forbidden(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/users/created",
            headers={"X-ClientCert-DN": "CN=rasenmaeher,O=RM", "X-SSL-Client-Verify": "FAILED"},
            json={"uuid": "uuid-a", "callsign": "VIRTA-1", "x509cert": _build_cert_pem("VIRTA-1")},
        )
        assert response.status_code == 403
