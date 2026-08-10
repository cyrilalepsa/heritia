from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.ebook import EbookListing
from app.models.user import User
from app.schemas.ebook import (
    EbookListingCreate,
    EbookListingOut,
    PaymentIntentCreate,
    PaymentIntentResponse,
    StripeOnboardingResponse,
)
from app.services import stripe_connect

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.post("/stripe/onboarding", response_model=StripeOnboardingResponse)
def stripe_onboarding(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.ebook_unlocked:
        raise HTTPException(
            status_code=403,
            detail="Ebook marketplace locked. Earn 3 gold badges to unlock.",
        )
    try:
        result = stripe_connect.create_onboarding_link(db, user)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return StripeOnboardingResponse(**result)


@router.post("/ebooks", response_model=EbookListingOut)
def create_ebook_listing(
    payload: EbookListingCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.ebook_unlocked:
        raise HTTPException(status_code=403, detail="Ebook marketplace locked")
    if not user.stripe_account_id:
        raise HTTPException(
            status_code=400,
            detail="Complete Stripe Express onboarding first",
        )
    listing = EbookListing(
        user_id=user.id,
        title=payload.title,
        price=payload.price,
        active=payload.active,
        stripe_account_id=user.stripe_account_id,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/ebooks", response_model=List[EbookListingOut])
def list_active_ebooks(db: Session = Depends(get_db)):
    return db.query(EbookListing).filter(EbookListing.active.is_(True)).all()


@router.get("/ebooks/mine", response_model=List[EbookListingOut])
def list_my_ebooks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(EbookListing).filter(EbookListing.user_id == user.id).all()


@router.post("/checkout", response_model=PaymentIntentResponse)
def create_checkout(
    payload: PaymentIntentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    listing = db.query(EbookListing).filter(EbookListing.id == payload.ebook_listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    try:
        result = stripe_connect.create_destination_payment_intent(db, listing=listing, buyer=user)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PaymentIntentResponse(**result)