"""Pydantic models for rmcryptpad contract routes."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OperationResultResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Generic contract response."""

    model_config = ConfigDict(extra="forbid")

    success: bool = True
    error: str | None = None


class UserCRUDRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Product user lifecycle request."""

    model_config = ConfigDict(extra="forbid")

    uuid: str
    callsign: str
    x509cert: str


class ProductAddRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Interop product registration request."""

    model_config = ConfigDict(extra="forbid")

    certcn: str
    x509cert: str


class ProductAuthzResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Interop authz response."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["basic"] = "basic"
    username: str
    password: str


class ProductDescription(BaseModel):  # pylint: disable=too-few-public-methods
    """Product description contract."""

    model_config = ConfigDict(extra="forbid")

    shortname: str
    title: str
    icon: str | None
    description: str
    language: str


class ProductComponent(BaseModel):  # pylint: disable=too-few-public-methods
    """Component metadata."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["link", "markdown", "component"]
    ref: str


class ProductDescriptionExtended(BaseModel):  # pylint: disable=too-few-public-methods
    """Extended product description contract."""

    model_config = ConfigDict(extra="forbid")

    shortname: str
    title: str
    icon: str | None
    description: str
    language: str
    docs: str
    component: ProductComponent


class InstructionsResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Instructions payload."""

    model_config = ConfigDict(extra="forbid")

    callsign: str
    instructions: str
    language: str


class ClientDataPayload(BaseModel):  # pylint: disable=too-few-public-methods
    """Client data payload."""

    model_config = ConfigDict(extra="forbid")

    url: str
    sandbox_url: str
    docs_url: str
    oidc_issuer: str


class ClientDataResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """Nested client data response."""

    model_config = ConfigDict(extra="forbid")

    data: ClientDataPayload
