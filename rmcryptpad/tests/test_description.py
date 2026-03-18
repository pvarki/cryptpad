"""Tests for CryptPad descriptions and instructions."""

from __future__ import annotations

import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi.testclient import TestClient

from rmcryptpad.web.application import get_app_no_init


def _rm_headers() -> dict[str, str]:
    return {"X-ClientCert-DN": "CN=rasenmaeher,O=RM"}


def _user_payload(callsign: str) -> dict[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, callsign)])
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
    return {
        "uuid": f"uuid-{callsign}",
        "callsign": callsign,
        "x509cert": cert.public_bytes(serialization.Encoding.PEM).decode("utf-8"),
    }


def test_description_routes_return_cryptpad_metadata(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        v1 = client.get("/api/v1/description/en", headers=_rm_headers())
        assert v1.status_code == 200
        assert v1.json()["shortname"] == "cryptpad"

        v2 = client.get("/api/v2/description/en", headers=_rm_headers())
        assert v2.status_code == 200
        payload = v2.json()
        assert payload["shortname"] == "cryptpad"
        assert payload["component"]["ref"] == "/ui/cryptpad/remoteEntry.js"


def test_instructions_route_returns_product_guidance(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post("/api/v1/instructions/en", headers=_rm_headers(), json=_user_payload("VIRTA-1"))
        assert response.status_code == 200
        payload = response.json()
        assert payload["language"] == "en"
        assert payload["instructions"]


def test_healthcheck_is_available(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.get("/api/v1/healthcheck")
        assert response.status_code == 200
        assert response.json()["healthy"] is True
