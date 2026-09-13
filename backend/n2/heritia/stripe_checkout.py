from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.ebook import EbookListing
from app.models.ebook_purchase import EbookPurchase
from app.models.user import User
from n2.heritia.firebase_wallet import grant_ebook_access, sync_user_wallet


def handle_checkout_session_completed(db: Session, session: Dict[str, Any]) -> Dict[str, Any]:
    metadata = session.get("metadata") or {}
    listing_id_raw = metadata.get("heritia_listing_id")
    buyer_id_raw = metadata.get("heritia_buyer_id") or metadata.get("heritia_user_id")

    if not listing_id_raw or not buyer_id_raw:
        return {
            "handled": False,
            "detail": "checkout.session.completed missing heritia metadata",
        }

    listing_id = int(listing_id_raw)
    buyer_id = int(buyer_id_raw)
    session_id = session.get("id") or ""

    listing = db.query(EbookListing).filter(EbookListing.id == listing_id).first()
    buyer = db.query(User).filter(User.id == buyer_id).first()
    if not listing or not buyer:
        return {"handled": False, "detail": "listing or buyer not found"}

    existing = (
        db.query(EbookPurchase)
        .filter(
            EbookPurchase.buyer_id == buyer_id,
            EbookPurchase.listing_id == listing_id,
        )
        .first()
    )
    if existing:
        return {
            "handled": True,
            "detail": "purchase already recorded",
            "purchase_id": existing.id,
        }

    purchase = EbookPurchase(
        buyer_id=buyer_id,
        listing_id=listing_id,
        stripe_checkout_session_id=session_id,
        stripe_payment_intent_id=session.get("payment_intent"),
        unlocked_at=datetime.utcnow(),
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    purchased_ids = [
        row.listing_id
        for row in db.query(EbookPurchase).filter(EbookPurchase.buyer_id == buyer_id).all()
    ]
    firebase_synced = grant_ebook_access(user_id=buyer_id, listing_id=listing_id)
    sync_user_wallet(
        user_id=buyer.id,
        xp_total=buyer.xp_total or 0,
        wallet_cents=buyer.wallet_cents or 0,
        gold_badges_count=buyer.gold_badges_count or 0,
        purchased_ebook_ids=purchased_ids,
    )

    return {
        "handled": True,
        "detail": "ebook access unlocked",
        "purchase_id": purchase.id,
        "buyer_id": buyer_id,
        "listing_id": listing_id,
        "firebase_synced": firebase_synced,
    }


def handle_webhook_event(db: Session, event: Dict[str, Any]) -> Dict[str, Any]:
    event_type = event.get("type")
    if event_type == "checkout.session.completed":
        session = (event.get("data") or {}).get("object") or {}
        result = handle_checkout_session_completed(db, session)
        return {"event_type": event_type, **result}

    return {"event_type": event_type, "handled": False, "detail": "ignored"}
