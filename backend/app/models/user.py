from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

PLAN_TYPES = (
    "standard_monthly",
    "standard_annual",
    "premium_monthly",
    "premium_annual",
)
# Legacy ids still accepted then normalized
LEGACY_PLAN_MAP = {
    "standard_19": "standard_monthly",
    "standard_29": "premium_monthly",
    "premium_29": "premium_monthly",
    "premium_39": "premium_monthly",
}

HEALTH_OPTIONS = ("diabete", "cholesterol", "perte_poids")
HEALTH_OPTION_SURCHARGE_CENTS = 700  # +7€/mois

REFERRALS_PER_FREE_YEAR = 6
MAX_REFERRAL_FREE_YEARS = 3
# A referral is valid only when the invitee subscribes to Premium
# (premium_monthly 29€ or premium_annual 149€).
REFERRAL_REQUIRES_PREMIUM = True


def normalize_plan_type(plan_type: str) -> str:
    if plan_type in PLAN_TYPES:
        return plan_type
    return LEGACY_PLAN_MAP.get(plan_type, "standard_monthly")


def is_premium_plan(plan_type: str) -> bool:
    return normalize_plan_type(plan_type).startswith("premium_")


def counts_as_valid_referral(invitee_plan_type: str) -> bool:
    """Only Premium subscriptions validate a referral credit."""
    if not REFERRAL_REQUIRES_PREMIUM:
        return True
    return is_premium_plan(invitee_plan_type)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String(120), nullable=False)
    prenom: Mapped[str] = mapped_column(String(120), nullable=False)
    ville: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(32), default="email")

    plan_type: Mapped[str] = mapped_column(String(32), default="standard_monthly")
    health_options: Mapped[list] = mapped_column(JSON, default=lambda: [])
    referral_credits: Mapped[int] = mapped_column(Integer, default=0)
    referrals_this_year: Mapped[int] = mapped_column(Integer, default=0)
    referral_free_years_claimed: Mapped[int] = mapped_column(Integer, default=0)

    gold_badges_count: Mapped[int] = mapped_column(Integer, default=0)
    ebook_unlocked: Mapped[bool] = mapped_column(Boolean, default=False)

    stripe_account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    recipes = relationship("UserRecipe", back_populates="user", cascade="all, delete-orphan")
    ebook_listings = relationship("EbookListing", back_populates="user", cascade="all, delete-orphan")

    def apply_gold_badge_rules(self) -> None:
        if self.gold_badges_count >= 3:
            self.ebook_unlocked = True

    def is_premium(self) -> bool:
        return normalize_plan_type(self.plan_type).startswith("premium_")

    def is_annual(self) -> bool:
        return normalize_plan_type(self.plan_type).endswith("_annual")

    def monthly_health_surcharge_cents(self) -> int:
        if self.is_premium():
            return 0
        options = self.health_options or []
        return len(options) * HEALTH_OPTION_SURCHARGE_CENTS

    def referral_progress(self) -> dict:
        """6 Premium referrals/year = 1 free year, renewable up to 3 times."""
        claimed = min(self.referral_free_years_claimed or 0, MAX_REFERRAL_FREE_YEARS)
        count = max(0, self.referrals_this_year or 0)
        can_earn_more = claimed < MAX_REFERRAL_FREE_YEARS
        return {
            "referrals_this_year": count,
            "target": REFERRALS_PER_FREE_YEAR,
            "free_years_claimed": claimed,
            "max_free_years": MAX_REFERRAL_FREE_YEARS,
            "can_earn_more": can_earn_more,
            "requires_premium": REFERRAL_REQUIRES_PREMIUM,
            "next_year_free_eligible": can_earn_more and count >= REFERRALS_PER_FREE_YEAR,
            "label": "6 parrainages Premium souscrits = 1 An Offert (Renouvelable 3 fois)",
            "status_template": "{current}/6 filleuls Premium convertis cette année",
        }

    def register_premium_referral(self, invitee_plan_type: str) -> bool:
        """
        Increment yearly referral counter only if invitee subscribed to Premium.
        When target is reached and free years remain, claim one free year.
        """
        if not counts_as_valid_referral(invitee_plan_type):
            return False
        if (self.referral_free_years_claimed or 0) >= MAX_REFERRAL_FREE_YEARS:
            return False
        self.referrals_this_year = (self.referrals_this_year or 0) + 1
        self.referral_credits = (self.referral_credits or 0) + 1
        if self.referrals_this_year >= REFERRALS_PER_FREE_YEAR:
            self.referral_free_years_claimed = (self.referral_free_years_claimed or 0) + 1
            self.referrals_this_year = 0
        return True