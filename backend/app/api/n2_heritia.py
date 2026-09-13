from __future__ import annotations

import json
from typing import Any, Dict

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import MASTER_KEY_HEADER, verify_master_key, verify_master_key_optional
from app.config import settings
from app.database import get_db
from app.schemas.n2_heritia import (
    GamificationXpRequest,
    GamificationXpResponse,
    RecipeGenerateRequest,
    RecipeGenerateResponse,
    ScanRequest,
    ScanResponse,
)
from app.services import n2_heritia, stripe_connect

router = APIRouter(prefix="/n2/heritia", tags=["n2-heritia"])


@router.post("/scan", response_model=ScanResponse, dependencies=[Depends(verify_master_key)])
def scan_inventory(payload: ScanRequest):
    try:
        return n2_heritia.analyze_scan(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/gamification/xp",
    response_model=GamificationXpResponse,
    dependencies=[Depends(verify_master_key)],
)
def update_gamification_xp(
    payload: GamificationXpRequest,
    db: Session = Depends(get_db),
):
    try:
        return n2_heritia.apply_gamification_xp(
            db,
            user_id=payload.user_id,
            xp_delta=payload.xp_delta,
            wallet_cents_delta=payload.wallet_cents_delta,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/recipes/generate",
    response_model=RecipeGenerateResponse,
    dependencies=[Depends(verify_master_key)],
)
def generate_recipes(payload: RecipeGenerateRequest):
    try:
        recipes = n2_heritia.generate_recipes(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RecipeGenerateResponse(recipes=recipes)


@router.post("/stripe/webhook")
async def stripe_checkout_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Stripe Checkout webhook — verified via stripe-signature in all environments.
    In local/staging only, X-Master-Key may be used to replay test payloads.
    """
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    master_key_ok = verify_master_key_optional(request.headers.get(MASTER_KEY_HEADER))

    if signature:
        if not settings.stripe_webhook_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe webhook secret is not configured",
            )
        try:
            stripe_connect.configure_stripe()
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.stripe_webhook_secret,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid Stripe payload") from exc
        except stripe.error.SignatureVerificationError as exc:
            raise HTTPException(status_code=400, detail="Invalid Stripe signature") from exc
    elif master_key_ok and settings.allow_master_key_webhook_bypass:
        try:
            event = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON test payload") from exc
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing stripe-signature or valid X-Master-Key (non-production only)",
        )

    result = stripe_connect.handle_webhook_event(db, event)
    return {"received": True, **result}


@router.get("/health")
def n2_heritia_health():
    return {
        "status": "ok",
        "module": "heritia",
        "master_key_configured": settings.master_key_configured,
    }
