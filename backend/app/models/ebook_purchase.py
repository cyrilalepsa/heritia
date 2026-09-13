from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EbookPurchase(Base):
    __tablename__ = "ebook_purchases"
    __table_args__ = (UniqueConstraint("buyer_id", "listing_id", name="uq_ebook_purchase_buyer_listing"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("ebook_listings.id"), nullable=False, index=True)
    stripe_checkout_session_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    buyer = relationship("User", backref="ebook_purchases")
    listing = relationship("EbookListing", backref="purchases")
