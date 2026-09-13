from __future__ import annotations

import json

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import MASTER_KEY_HEADER, verify_master_key, verify_master_key_optional
from app.config import settings
from app.database import get_db
from app.services import stripe_connect
from n2.heritia.cloudinary_scan import analyze_cloudinary_scan
from n2.heritia.gamification import generate_recipes_from_ingredients, reward_recipe, reward_scan
from n2.heritia.schemas import (
    GeneratedRecipe,
    RecipeGenerateRequest,
    RecipeGenerateResponse,
    ScanRequest,
    ScanResponse,
)
from n2.heritia.stripe_checkout import handle_webhook_event

router = APIRouter(prefix="/n2/heritia", tags=["n2-heritia"])


@router.post("/scan", response_model=ScanResponse, dependencies=[Depends(verify_master_key)])
def scan_image(payload: ScanRequest, db: Session = Depends(get_db)):
    """
    Webhook N2 — analyse d'image Cloudinary (frigo ou ticket de caisse).
    Déclenche XP + cagnotte Firebase si user_id est fourni.
    """
    try:
        result = analyze_cloudinary_scan(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if payload.user_id:
        try:
            result.gamification = reward_scan(db, payload.user_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return result


@router.post(
    "/recipes/generate",
    response_model=RecipeGenerateResponse,
    dependencies=[Depends(verify_master_key)],
)
def generate_recipes(payload: RecipeGenerateRequest, db: Session = Depends(get_db)):
    try:
        raw = generate_recipes_from_ingredients(
            payload.ingredients,
            health_options=payload.health_options,
            servings=payload.servings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    recipes = [GeneratedRecipe(**item) for item in raw]
    gamification = None
    if payload.user_id:
        try:
            gamification = reward_recipe(db, payload.user_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return RecipeGenerateResponse(recipes=recipes, gamification=gamification)


@router.post("/stripe/webhook")
async def stripe_ebook_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook Stripe Checkout — débloque l'accès aux livres numériques achetés.
    Production : stripe-signature obligatoire.
    Dev/staging : X-Master-Key autorisé pour rejouer des payloads de test.
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

    result = handle_webhook_event(db, event)
    return {"received": True, **result}


@router.get("/health")
def heritia_module_health():
    return {
        "status": "ok",
        "module": "heritia",
        "master_key_configured": settings.master_key_configured,
        "cloudinary_configured": settings.cloudinary_configured,
        "firebase_configured": settings.firebase_configured,
    }
