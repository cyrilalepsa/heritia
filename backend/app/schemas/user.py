from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import HEALTH_OPTIONS, PLAN_TYPES, normalize_plan_type


class UserProfileUpdate(BaseModel):
    nom: Optional[str] = Field(default=None, min_length=1, max_length=120)
    prenom: Optional[str] = Field(default=None, min_length=1, max_length=120)
    ville: Optional[str] = Field(default=None, min_length=1, max_length=120)
    plan_type: Optional[str] = None
    health_options: Optional[List[str]] = None

    def validate_domain(self) -> None:
        if self.plan_type is not None:
            normalized = normalize_plan_type(self.plan_type)
            if normalized not in PLAN_TYPES:
                raise ValueError("plan_type must be one of {0}".format(PLAN_TYPES))
            self.plan_type = normalized
        if self.health_options is not None:
            invalid = set(self.health_options) - set(HEALTH_OPTIONS)
            if invalid:
                raise ValueError("Invalid health_options: {0}".format(sorted(invalid)))


class GoldBadgeUpdate(BaseModel):
    gold_badges_count: int = Field(ge=0)


class ReferralProgressOut(BaseModel):
    referrals_this_year: int
    target: int
    free_years_claimed: int
    max_free_years: int
    can_earn_more: bool
    next_year_free_eligible: bool
    requires_premium: bool = True
    label: str = "6 parrainages Premium souscrits = 1 An Offert (Renouvelable 3 fois)"
    status_template: str = "{current}/6 filleuls Premium convertis cette année"


class UserOut(BaseModel):
    id: int
    nom: str
    prenom: str
    ville: str
    email: EmailStr
    plan_type: str
    health_options: List[str]
    referral_credits: int
    referrals_this_year: int = 0
    referral_free_years_claimed: int = 0
    referral_progress: Optional[ReferralProgressOut] = None
    gold_badges_count: int
    ebook_unlocked: bool
    stripe_account_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    monthly_health_surcharge_cents: int = 0

    class Config:
        from_attributes = True