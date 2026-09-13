from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    user_id: Optional[int] = None
    image_base64: Optional[str] = Field(default=None, description="Base64 image (fridge or receipt)")
    image_url: Optional[str] = None
    scan_type: str = Field(default="fridge", pattern="^(fridge|receipt)$")


class ScanItem(BaseModel):
    label: str
    quantity: Optional[str] = None
    expiry_hint: Optional[str] = None


class ScanResponse(BaseModel):
    scan_type: str
    items: List[ScanItem]
    summary: str


class GamificationXpRequest(BaseModel):
    user_id: int = Field(ge=1)
    xp_delta: int = Field(description="XP gained or lost")
    wallet_cents_delta: int = Field(
        default=0,
        description="Cagnotte adjustment in cents (can be negative)",
    )
    reason: Optional[str] = None


class GamificationXpResponse(BaseModel):
    user_id: int
    xp_total: int
    wallet_cents: int
    gold_badges_count: int
    ebook_unlocked: bool


class RecipeGenerateRequest(BaseModel):
    user_id: Optional[int] = None
    ingredients: List[str] = Field(min_length=1)
    health_options: List[str] = Field(default_factory=list)
    servings: int = Field(default=2, ge=1, le=12)


class GeneratedRecipe(BaseModel):
    titre: str
    ingredients: str
    instructions: str


class RecipeGenerateResponse(BaseModel):
    recipes: List[GeneratedRecipe]
