"""Product description routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ..config import RMCryptPadSettings
from ..schema import ProductComponent, ProductDescription, ProductDescriptionExtended
from .security import require_mtls_header, require_rm_caller

router = APIRouter(dependencies=[Depends(require_mtls_header)])
router_v2 = APIRouter(dependencies=[Depends(require_mtls_header)])


def _description_text(language: str) -> str:
    if language == "fi":
        return "Turvallinen yhteiskirjoittaminen ja tiedostojen jakaminen"
    return "Secure collaborative document editing and sharing"


@router.get("/description/{language}", response_model=ProductDescription)
async def return_product_description(language: str, request: Request) -> ProductDescription:
    require_rm_caller(request)
    return ProductDescription(
        shortname="cryptpad",
        title="CryptPad",
        icon=None,
        description=_description_text(language),
        language=language,
    )


@router_v2.get("/description/{language}", response_model=ProductDescriptionExtended)
async def return_product_description_extended(language: str, request: Request) -> ProductDescriptionExtended:
    require_rm_caller(request)
    settings = RMCryptPadSettings.singleton()
    return ProductDescriptionExtended(
        shortname="cryptpad",
        title="CryptPad",
        icon=None,
        description=_description_text(language),
        language=language,
        docs=settings.docs_url,
        component=ProductComponent(type="component", ref="/ui/cryptpad/remoteEntry.js"),
    )
