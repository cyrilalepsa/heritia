from __future__ import annotations

import base64
import re
from typing import List

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.n2_heritia import (
    GeneratedRecipe,
    GamificationXpResponse,
    RecipeGenerateRequest,
    ScanItem,
    ScanRequest,
    ScanResponse,
)


def analyze_scan(payload: ScanRequest) -> ScanResponse:
    """Lightweight scan stub — replace with vision/OCR provider when wired."""
    if payload.image_base64:
        try:
            base64.b64decode(payload.image_base64, validate=True)
        except Exception as exc:
            raise ValueError("Invalid image_base64 payload") from exc

    if payload.scan_type == "receipt":
        items = [
            ScanItem(label="Tomates", quantity="500 g"),
            ScanItem(label="Pâtes", quantity="1 paquet"),
            ScanItem(label="Fromage râpé", quantity="200 g"),
        ]
        summary = "Ticket analysé — 3 produits détectés pour le stock Heritia."
    else:
        items = [
            ScanItem(label="Lait", quantity="1 L", expiry_hint="J+3"),
            ScanItem(label="Oeufs", quantity="6", expiry_hint="J+7"),
            ScanItem(label="Épinards", quantity="250 g", expiry_hint="J+2"),
        ]
        summary = "Frigo analysé — 3 produits avec alertes anti-gaspillage."

    return ScanResponse(scan_type=payload.scan_type, items=items, summary=summary)


def apply_gamification_xp(db: Session, *, user_id: int, xp_delta: int, wallet_cents_delta: int) -> GamificationXpResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise LookupError("User not found")

    user.xp_total = max(0, (user.xp_total or 0) + xp_delta)
    user.wallet_cents = max(0, (user.wallet_cents or 0) + wallet_cents_delta)

    # Simple XP ladder: every 100 XP grants one gold badge (capped at existing rules).
    badge_from_xp = user.xp_total // 100
    if badge_from_xp > user.gold_badges_count:
        user.gold_badges_count = badge_from_xp
    user.apply_gold_badge_rules()

    db.commit()
    db.refresh(user)
    return GamificationXpResponse(
        user_id=user.id,
        xp_total=user.xp_total,
        wallet_cents=user.wallet_cents,
        gold_badges_count=user.gold_badges_count,
        ebook_unlocked=user.ebook_unlocked,
    )


def _normalize_ingredient(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def generate_recipes(payload: RecipeGenerateRequest) -> List[GeneratedRecipe]:
    ingredients = [_normalize_ingredient(item) for item in payload.ingredients if item.strip()]
    if not ingredients:
        raise ValueError("At least one ingredient is required")

    joined = ", ".join(ingredients[:6])
    health_note = ""
    if payload.health_options:
        health_note = " Options santé : {0}.".format(", ".join(payload.health_options))

    base_instructions = (
        "1. Préparer et assaisonner les ingrédients ({0}).\n"
        "2. Cuire à feu moyen en respectant les textures.\n"
        "3. Servir {1} portion(s)."
    ).format(joined, payload.servings)

    return [
        GeneratedRecipe(
            titre="Poêlée Heritia anti-gaspillage",
            ingredients=joined,
            instructions=base_instructions + health_note,
        ),
        GeneratedRecipe(
            titre="Assiette express Heritia",
            ingredients=joined,
            instructions=(
                "Mixer rapidement les restes, réchauffer 8 minutes, "
                "ajuster l'assaisonnement et servir."
            )
            + health_note,
        ),
    ]
