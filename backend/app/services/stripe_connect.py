"""Stripe Connect Express helpers — marketplace with 0% platform commission."""

from __future__ import annotations

from typing import Optional

import stripe
from sqlalchemy.orm import Session

from app.config import settings
from app.models.ebook import EbookListing
from app.models.user import User

# Commission plateforme HERITIA : 0%
APPLICATION_FEE_AMOUNT = 0


def _configure_stripe() -> None:
    if not settings.stripe_secret_key:
        raise RuntimeError("HERITIA_STRIPE_SECRET_KEY is not configured")
    stripe.api_key = settings.stripe_secret_key


def ensure_express_account(db: Session, user: User) -> str:
    """Create a Stripe Express account if the user does not already have one."""
    _configure_stripe()
    if user.stripe_account_id:
        return user.stripe_account_id

    account = stripe.Account.create(
        type="express",
        country="FR",
        email=user.email,
        capabilities={
            "card_payments": {"requested": True},
            "transfers": {"requested": True},
        },
        business_type="individual",
        metadata={"heritia_user_id": str(user.id)},
    )
    user.stripe_account_id = account["id"]
    db.commit()
    db.refresh(user)
    return user.stripe_account_id


def create_onboarding_link(db: Session, user: User) -> dict:
    """
    Create Stripe Express AccountLink for onboarding.
    Uses stripe.AccountLink.create as required by the HERITIA marketplace flow.
    """
    account_id = ensure_express_account(db, user)
    link = stripe.AccountLink.create(
        account=account_id,
        refresh_url=settings.stripe_refresh_url,
        return_url=settings.stripe_return_url,
        type="account_onboarding",
    )
    return {"account_id": account_id, "onboarding_url": link["url"]}


def create_destination_payment_intent(
    db: Session,
    *,
    listing: EbookListing,
    buyer: Optional[User] = None,
) -> dict:
    """
    Create a PaymentIntent for an ebook purchase.
    application_fee_amount is always 0 (0% commission).
    Funds go to the seller's Connect account via transfer_data.destination.
    """
    _configure_stripe()
    if not listing.active:
        raise ValueError("Ebook listing is not active")
    if not listing.stripe_account_id:
        raise ValueError("Seller Stripe account missing")

    metadata = {
        "heritia_listing_id": str(listing.id),
        "heritia_seller_id": str(listing.user_id),
    }
    if buyer:
        metadata["heritia_buyer_id"] = str(buyer.id)

    intent = stripe.PaymentIntent.create(
        amount=listing.price,
        currency="eur",
        application_fee_amount=APPLICATION_FEE_AMOUNT,
        transfer_data={"destination": listing.stripe_account_id},
        metadata=metadata,
        automatic_payment_methods={"enabled": True},
    )
    return {
        "client_secret": intent["client_secret"],
        "payment_intent_id": intent["id"],
        "application_fee_amount": APPLICATION_FEE_AMOUNT,
    }