from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User, normalize_plan_type
from app.schemas.user import GoldBadgeUpdate, UserOut, UserProfileUpdate

router = APIRouter(prefix="/profil", tags=["profil"])


def _user_out(user: User) -> UserOut:
    plan = normalize_plan_type(user.plan_type)
    return UserOut(
        id=user.id,
        nom=user.nom,
        prenom=user.prenom,
        ville=user.ville,
        email=user.email,
        plan_type=plan,
        health_options=user.health_options or [],
        referral_credits=user.referral_credits,
        referrals_this_year=user.referrals_this_year or 0,
        referral_free_years_claimed=user.referral_free_years_claimed or 0,
        referral_progress=user.referral_progress(),
        gold_badges_count=user.gold_badges_count,
        ebook_unlocked=user.ebook_unlocked,
        stripe_account_id=user.stripe_account_id,
        stripe_subscription_id=user.stripe_subscription_id,
        monthly_health_surcharge_cents=user.monthly_health_surcharge_cents(),
    )


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return _user_out(user)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        payload.validate_domain()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if payload.nom is not None:
        user.nom = payload.nom
    if payload.prenom is not None:
        user.prenom = payload.prenom
    if payload.ville is not None:
        user.ville = payload.ville
    if payload.plan_type is not None:
        user.plan_type = payload.plan_type
    if payload.health_options is not None:
        user.health_options = payload.health_options

    db.commit()
    db.refresh(user)
    return _user_out(user)


@router.patch("/me/gold-badges", response_model=UserOut)
def update_gold_badges(
    payload: GoldBadgeUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.gold_badges_count = payload.gold_badges_count
    user.apply_gold_badge_rules()
    db.commit()
    db.refresh(user)
    return _user_out(user)