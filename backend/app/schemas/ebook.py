from __future__ import annotations

from pydantic import BaseModel, Field


class EbookListingCreate(BaseModel):
    title: str = Field(default="Mon e-book HERITIA", min_length=1, max_length=255)
    price: int = Field(gt=0, description="Price in cents")
    active: bool = False


class EbookListingOut(BaseModel):
    id: int
    user_id: int
    title: str
    price: int
    active: bool
    stripe_account_id: str

    class Config:
        from_attributes = True


class StripeOnboardingResponse(BaseModel):
    account_id: str
    onboarding_url: str


class PaymentIntentCreate(BaseModel):
    ebook_listing_id: int


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    application_fee_amount: int = 0