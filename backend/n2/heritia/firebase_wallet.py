from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)
_firestore_client = None


def _firebase_configured() -> bool:
    return bool(getattr(settings, "firebase_project_id", None))


def _get_firestore():
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client
    if not _firebase_configured():
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        logger.warning("firebase-admin not installed — skipping Firebase sync")
        return None

    if not firebase_admin._apps:
        cred_json = getattr(settings, "firebase_credentials_json", "") or ""
        if cred_json.strip():
            cred = credentials.Certificate(json.loads(cred_json))
            firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})
        else:
            firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})

    _firestore_client = firestore.client()
    return _firestore_client


def sync_user_wallet(
    *,
    user_id: int,
    xp_total: int,
    wallet_cents: int,
    gold_badges_count: int,
    purchased_ebook_ids: Optional[List[int]] = None,
) -> bool:
    """Push Heritia wallet state to Firestore users/heritia_{id}."""
    db = _get_firestore()
    if db is None:
        return False

    doc_ref = db.collection("heritia_users").document(str(user_id))
    payload: Dict[str, Any] = {
        "xp_total": xp_total,
        "wallet_cents": wallet_cents,
        "gold_badges_count": gold_badges_count,
        "app": "HERITIA",
    }
    if purchased_ebook_ids is not None:
        payload["purchased_ebook_ids"] = purchased_ebook_ids

    doc_ref.set(payload, merge=True)
    return True


def grant_ebook_access(*, user_id: int, listing_id: int) -> bool:
    db = _get_firestore()
    if db is None:
        return False

    doc_ref = db.collection("heritia_users").document(str(user_id))
    snapshot = doc_ref.get()
    existing = snapshot.to_dict() if snapshot.exists else {}
    purchased = list(existing.get("purchased_ebook_ids") or [])
    if listing_id not in purchased:
        purchased.append(listing_id)
    doc_ref.set({"purchased_ebook_ids": purchased}, merge=True)
    return True
