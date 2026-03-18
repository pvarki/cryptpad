"""Tests for CryptPad interop contract endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from rmcryptpad.db.product import Product
from rmcryptpad.web.application import get_app_no_init


def _rm_headers() -> dict[str, str]:
    return {"X-ClientCert-DN": "CN=rasenmaeher,O=RM"}


def _product_headers(certcn: str) -> dict[str, str]:
    return {"X-ClientCert-DN": f"CN={certcn},O=RM"}


@pytest.mark.asyncio
async def test_interop_add_and_authz_return_product_credentials(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/interop/add",
            headers=_rm_headers(),
            json={
                "certcn": "cryptpad.localhost",
                "x509cert": "-----BEGIN CERTIFICATE-----\nINTEROP\n-----END CERTIFICATE-----\n",
            },
        )
        assert response.status_code == 200

        authz = client.get("/api/v1/interop/authz", headers=_product_headers("cryptpad.localhost"))
        assert authz.status_code == 200
        payload = authz.json()
        assert payload["type"] == "basic"
        assert payload["username"] == "cryptpad.localhost"
        assert payload["password"]

    product = await Product.by_cn("cryptpad.localhost")
    assert product.certcn == "cryptpad.localhost"
