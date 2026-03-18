"""ORM tests for rmcryptpad."""

from __future__ import annotations

import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from rmcryptpad.db.errors import Deleted
from rmcryptpad.db.oidc_code import OIDCAuthorizationCode
from rmcryptpad.db.product import Product
from rmcryptpad.db.user import User, fingerprint_pem


def _build_test_cert_pem(common_name: str = "virta.example.local") -> tuple[str, str]:
    """Create a deterministic-ish PEM certificate for fingerprint tests."""
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
    pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    return pem, cert.fingerprint(hashes.SHA1()).hex()


def _build_test_cert_only(common_name: str) -> str:
    """Create a PEM certificate for ORM persistence tests."""
    cert_pem, _ = _build_test_cert_pem(common_name)
    return cert_pem


@pytest.mark.asyncio
async def test_callsign_is_identity(dbinstance: None) -> None:
    """Refreshing the same callsign should update the same row."""
    _ = dbinstance
    first_cert = _build_test_cert_only("VIRTA-1")
    second_cert = _build_test_cert_only("VIRTA-1-refresh")
    created = await User.create_or_update(
        callsign="VIRTA-1",
        rmuuid="uuid-a",
        cert_pem=first_cert,
    )

    refreshed = await User.create_or_update(
        callsign="VIRTA-1",
        rmuuid="uuid-a",
        cert_pem=second_cert,
    )

    assert created.pk == refreshed.pk
    assert refreshed.cert_pem == second_cert


@pytest.mark.asyncio
async def test_user_admin_state_is_preserved_when_not_explicitly_changed(dbinstance: None) -> None:
    """Existing admin state should survive a normal callsign refresh."""
    _ = dbinstance
    first_cert = _build_test_cert_only("VIRTA-ADMIN")
    second_cert = _build_test_cert_only("VIRTA-ADMIN-REFRESH")
    created = await User.create_or_update(
        callsign="VIRTA-ADMIN",
        rmuuid="uuid-admin",
        cert_pem=first_cert,
        is_rmadmin=True,
    )

    refreshed = await User.create_or_update(
        callsign="VIRTA-ADMIN",
        rmuuid="uuid-admin",
        cert_pem=second_cert,
    )

    assert created.is_rmadmin is True
    assert refreshed.is_rmadmin is True


@pytest.mark.asyncio
async def test_user_admin_state_changes_when_requested(dbinstance: None) -> None:
    """Explicit admin changes should still be applied."""
    _ = dbinstance
    first_cert = _build_test_cert_only("VIRTA-ADMIN-2")
    second_cert = _build_test_cert_only("VIRTA-ADMIN-2-REFRESH")
    await User.create_or_update(
        callsign="VIRTA-ADMIN-2",
        rmuuid="uuid-admin-2",
        cert_pem=first_cert,
        is_rmadmin=True,
    )

    refreshed = await User.create_or_update(
        callsign="VIRTA-ADMIN-2",
        rmuuid="uuid-admin-2",
        cert_pem=second_cert,
        is_rmadmin=False,
    )

    assert refreshed.is_rmadmin is False


@pytest.mark.asyncio
async def test_cert_fingerprint_matches_certificate_bytes(dbinstance: None) -> None:
    """Stored certificate fingerprints should match the actual certificate fingerprint."""
    _ = dbinstance
    cert_pem, expected_fingerprint = _build_test_cert_pem()

    assert fingerprint_pem(cert_pem) == expected_fingerprint


@pytest.mark.asyncio
async def test_new_callsign_stays_separate(dbinstance: None) -> None:
    """A new callsign with the same RM UUID must be a separate identity."""
    _ = dbinstance
    await User.create_or_update(
        callsign="VIRTA-1",
        rmuuid="uuid-a",
        cert_pem=_build_test_cert_only("VIRTA-1"),
    )
    await User.create_or_update(
        callsign="VIRTA-2",
        rmuuid="uuid-a",
        cert_pem=_build_test_cert_only("VIRTA-2"),
    )

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


@pytest.mark.asyncio
async def test_oidc_code_second_consume_fails(dbinstance: None) -> None:
    """A consumed OIDC code must not be reusable."""
    _ = dbinstance
    code = await OIDCAuthorizationCode.issue(
        callsign="VIRTA-REUSE",
        client_id="cryptpad",
        redirect_uri="https://cryptpad.localhost/ssoauth",
        nonce="reuse",
        expires_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=5),
    )

    _first = await OIDCAuthorizationCode.consume(
        code=code,
        client_id="cryptpad",
        redirect_uri="https://cryptpad.localhost/ssoauth",
    )

    with pytest.raises(Deleted):
        await OIDCAuthorizationCode.consume(
            code=code,
            client_id="cryptpad",
            redirect_uri="https://cryptpad.localhost/ssoauth",
        )


@pytest.mark.asyncio
async def test_oidc_code_expired_fails(dbinstance: None) -> None:
    """Expired OIDC codes must be rejected."""
    _ = dbinstance
    code = await OIDCAuthorizationCode.issue(
        callsign="VIRTA-EXP",
        client_id="cryptpad",
        redirect_uri="https://cryptpad.localhost/ssoauth",
        nonce="exp",
        expires_at=datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=5),
    )

    with pytest.raises(Deleted):
        await OIDCAuthorizationCode.consume(
            code=code,
            client_id="cryptpad",
            redirect_uri="https://cryptpad.localhost/ssoauth",
        )
