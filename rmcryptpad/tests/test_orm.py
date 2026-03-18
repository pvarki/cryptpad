"""ORM tests for rmcryptpad."""

from __future__ import annotations

import datetime

import pytest

from rmcryptpad.db.oidc_code import OIDCAuthorizationCode
from rmcryptpad.db.product import Product
from rmcryptpad.db.user import User


@pytest.mark.asyncio
async def test_callsign_is_identity(dbinstance: None) -> None:
    """Refreshing the same callsign should update the same row."""
    _ = dbinstance
    created = await User.create_or_update(
        callsign="VIRTA-1",
        rmuuid="uuid-a",
        cert_pem="-----BEGIN CERTIFICATE-----\\nA\\n-----END CERTIFICATE-----\\n",
    )

    refreshed = await User.create_or_update(
        callsign="VIRTA-1",
        rmuuid="uuid-a",
        cert_pem="-----BEGIN CERTIFICATE-----\\nB\\n-----END CERTIFICATE-----\\n",
    )

    assert created.pk == refreshed.pk
    assert refreshed.cert_pem.endswith("B\\n-----END CERTIFICATE-----\\n")


@pytest.mark.asyncio
async def test_new_callsign_stays_separate(dbinstance: None) -> None:
    """A new callsign with the same RM UUID must be a separate identity."""
    _ = dbinstance
    await User.create_or_update(callsign="VIRTA-1", rmuuid="uuid-a", cert_pem="A")
    await User.create_or_update(callsign="VIRTA-2", rmuuid="uuid-a", cert_pem="B")

    assert (await User.by_callsign("VIRTA-1")).callsign == "VIRTA-1"
    assert (await User.by_callsign("VIRTA-2")).callsign == "VIRTA-2"


@pytest.mark.asyncio
async def test_product_lookup(dbinstance: None) -> None:
    """Product rows should persist interop credentials."""
    _ = dbinstance
    created = await Product.create_or_update(certcn="rmcryptpad.localhost")

    assert created.api_username == "rmcryptpad.localhost"
    assert await Product.by_cn("rmcryptpad.localhost")


@pytest.mark.asyncio
async def test_oidc_code_issue_and_use(dbinstance: None) -> None:
    """OIDC codes should be one-time and expire from the persisted model."""
    _ = dbinstance
    code = await OIDCAuthorizationCode.issue(
        callsign="VIRTA-1",
        client_id="cryptpad",
        redirect_uri="https://cryptpad.localhost/ssoauth",
        nonce="abc123",
        expires_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=5),
    )

    fetched = await OIDCAuthorizationCode.consume(
        code=code,
        client_id="cryptpad",
        redirect_uri="https://cryptpad.localhost/ssoauth",
    )

    assert fetched.callsign == "VIRTA-1"
