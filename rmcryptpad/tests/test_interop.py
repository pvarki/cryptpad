"""Tests for CryptPad interop contract endpoints."""

from __future__ import annotations

import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi.testclient import TestClient

from rmcryptpad.db.product import Product
from rmcryptpad.web.application import get_app_no_init


def _rm_headers() -> dict[str, str]:
    return {"X-ClientCert-DN": "CN=rasenmaeher,O=RM", "X-SSL-Client-Verify": "SUCCESS"}


def _product_headers(certcn: str) -> dict[str, str]:
    return {"X-ClientCert-DN": f"CN={certcn},O=RM", "X-SSL-Client-Verify": "SUCCESS"}


def _payload(certcn: str) -> dict[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, certcn)])
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
    return {"certcn": certcn, "x509cert": cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")}


@pytest.mark.asyncio
async def test_interop_add_and_authz_return_product_credentials(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post("/api/v1/interop/add", headers=_rm_headers(), json=_payload("cryptpad.localhost"))
        assert response.status_code == 200

        authz = client.get("/api/v1/interop/authz", headers=_product_headers("cryptpad.localhost"))
        assert authz.status_code == 200
        payload = authz.json()
        assert payload["type"] == "basic"
        assert payload["username"] == "cryptpad.localhost"
        assert payload["password"]

    product = await Product.by_cn("cryptpad.localhost")
    assert product.certcn == "cryptpad.localhost"
