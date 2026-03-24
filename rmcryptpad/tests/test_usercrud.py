"""Tests for the rmcryptpad user CRUD contract."""

from __future__ import annotations

import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi.testclient import TestClient

from rmcryptpad.db.user import User
from rmcryptpad.web.application import get_app_no_init


def _rm_headers() -> dict[str, str]:
    return {"X-ClientCert-DN": "CN=rasenmaeher,O=RM", "X-SSL-Client-Verify": "SUCCESS"}


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


@pytest.mark.asyncio
async def test_user_created_and_updated_keep_callsign_identity(
    dbinstance: None,
) -> None:
    _ = dbinstance
    app = get_app_no_init()
    first_cert = _build_cert_pem("VIRTA-1")
    second_cert = _build_cert_pem("VIRTA-1-refresh")
    separate_cert = _build_cert_pem("VIRTA-2")

    with TestClient(app) as client:
        created = client.post(
            "/api/v1/users/created",
            headers=_rm_headers(),
            json={"uuid": "uuid-a", "callsign": "VIRTA-1", "x509cert": first_cert},
        )
        assert created.status_code == 200
        refreshed = client.put(
            "/api/v1/users/updated",
            headers=_rm_headers(),
            json={"uuid": "uuid-a", "callsign": "VIRTA-1", "x509cert": second_cert},
        )
        assert refreshed.status_code == 200
        separate = client.put(
            "/api/v1/users/updated",
            headers=_rm_headers(),
            json={"uuid": "uuid-a", "callsign": "VIRTA-2", "x509cert": separate_cert},
        )
        assert separate.status_code == 200

    first = await User.by_callsign("VIRTA-1")
    second = await User.by_callsign("VIRTA-2")

    assert first.cert_pem == second_cert
    assert first.pk is not None
    assert second.pk is not None
    assert first.pk != second.pk


@pytest.mark.asyncio
async def test_user_created_accepts_cfssl_escaped_certificate_payload(
    dbinstance: None,
) -> None:
    _ = dbinstance
    app = get_app_no_init()
    cert_pem = _build_cert_pem("VIRTA-CFSSL")
    escaped_cert_pem = cert_pem.replace("\n", "\\n")

    with TestClient(app) as client:
        created = client.post(
            "/api/v1/users/created",
            headers=_rm_headers(),
            json={
                "uuid": "uuid-cfssl",
                "callsign": "VIRTA-CFSSL",
                "x509cert": escaped_cert_pem,
            },
        )

    assert created.status_code == 200

    user = await User.by_callsign("VIRTA-CFSSL")
    assert user.cert_pem == cert_pem


@pytest.mark.asyncio
async def test_user_revoked_promoted_and_demoted_update_state(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()
    cert_pem = _build_cert_pem("VIRTA-ADMIN")

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/created",
                headers=_rm_headers(),
                json={
                    "uuid": "uuid-admin",
                    "callsign": "VIRTA-ADMIN",
                    "x509cert": cert_pem,
                },
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/v1/users/promoted",
                headers=_rm_headers(),
                json={
                    "uuid": "uuid-admin",
                    "callsign": "VIRTA-ADMIN",
                    "x509cert": cert_pem,
                },
            ).status_code
            == 200
        )

    promoted = await User.by_callsign("VIRTA-ADMIN")
    assert promoted.is_rmadmin is True

    with TestClient(app) as client:
        assert (
            client.post(
                "/api/v1/users/demoted",
                headers=_rm_headers(),
                json={
                    "uuid": "uuid-admin",
                    "callsign": "VIRTA-ADMIN",
                    "x509cert": cert_pem,
                },
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/v1/users/revoked",
                headers=_rm_headers(),
                json={
                    "uuid": "uuid-admin",
                    "callsign": "VIRTA-ADMIN",
                    "x509cert": cert_pem,
                },
            ).status_code
            == 200
        )

    revoked = await User.by_callsign("VIRTA-ADMIN", allow_inactive=True)
    assert revoked.is_rmadmin is False
    assert revoked.revoked is not None


@pytest.mark.asyncio
async def test_wrong_rm_cn_is_forbidden_on_rm_only_routes(dbinstance: None) -> None:
    _ = dbinstance
    app = get_app_no_init()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/users/created",
            headers={
                "X-ClientCert-DN": "CN=not-rasenmaeher,O=RM",
                "X-SSL-Client-Verify": "SUCCESS",
            },
            json={
                "uuid": "uuid-bad",
                "callsign": "VIRTA-BAD",
                "x509cert": _build_cert_pem("VIRTA-BAD"),
            },
        )
        assert response.status_code == 403
