from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.user import User
from n2.heritia.firebase_wallet import sync_user_wallet
from n2.heritia.schemas import GamificationXpResponse

XP_PER_SCAN = 25
WALLET_CENTS_PER_SCAN = 50
XP_PER_RECIPE = 15
WALLET_CENTS_PER_RECIPE = 25
XP_PER_BADGE = 100

BADGE_MILESTONES = {
    1: "badge_bronze_scan",
    2: "badge_silver_chef",
    3: "badge_gold_marketplace",
}


def _badges_unlocked(old_count: int, new_count: int) -> List[str]:
    unlocked = []
    for level, badge_id in BADGE_MILESTONES.items():
        if old_count < level <= new_count:
            unlocked.append(badge_id)
    return unlocked


def apply_event(
    db: Session,
    *,
    user_id: int,
    xp_delta: int,
    wallet_cents_delta: int,
) -> GamificationXpResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise LookupError("User not found")

    old_badges = user.gold_badges_count or 0
    user.xp_total = max(0, (user.xp_total or 0) + xp_delta)
    user.wallet_cents = max(0, (user.wallet_cents or 0) + wallet_cents_delta)

    badge_from_xp = user.xp_total // XP_PER_BADGE
    if badge_from_xp > user.gold_badges_count:
        user.gold_badges_count = badge_from_xp
    user.apply_gold_badge_rules()

    db.commit()
    db.refresh(user)

    badges_unlocked = _badges_unlocked(old_badges, user.gold_badges_count)
    firebase_synced = sync_user_wallet(
        user_id=user.id,
        xp_total=user.xp_total,
        wallet_cents=user.wallet_cents,
        gold_badges_count=user.gold_badges_count,
    )

    return GamificationXpResponse(
        user_id=user.id,
        xp_total=user.xp_total,
        wallet_cents=user.wallet_cents,
        gold_badges_count=user.gold_badges_count,
        ebook_unlocked=user.ebook_unlocked,
        xp_awarded=xp_delta,
        wallet_cents_awarded=wallet_cents_delta,
        badges_unlocked=badges_unlocked,
        firebase_synced=firebase_synced,
    )


def reward_scan(db: Session, user_id: int) -> GamificationXpResponse:
    return apply_event(
        db,
        user_id=user_id,
        xp_delta=XP_PER_SCAN,
        wallet_cents_delta=WALLET_CENTS_PER_SCAN,
    )


def reward_recipe(db: Session, user_id: int) -> GamificationXpResponse:
    return apply_event(
        db,
        user_id=user_id,
        xp_delta=XP_PER_RECIPE,
        wallet_cents_delta=WALLET_CENTS_PER_RECIPE,
    )


def generate_recipes_from_ingredients(
    ingredients: List[str],
    *,
    health_options: List[str],
    servings: int,
) -> List[dict]:
    cleaned = [" ".join(part.split()) for part in ingredients if part and part.strip()]
    if not cleaned:
        raise ValueError("At least one ingredient is required")

    joined = ", ".join(cleaned[:8])
    health_note = ""
    if health_options:
        health_note = " Options santé : {0}.".format(", ".join(health_options))

    instructions = (
        "1. Préparer {0}.\n2. Cuire à feu moyen.\n3. Servir {1} portion(s)."
    ).format(joined, servings)

    return [
        {
            "titre": "Poêlée Heritia anti-gaspillage",
            "ingredients": joined,
            "instructions": instructions + health_note,
        },
        {
            "titre": "Assiette express Heritia",
            "ingredients": joined,
            "instructions": "Réchauffer les ingrédients 8 min, assaisonner et servir." + health_note,
        },
    ]
