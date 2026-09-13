from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ScanRequest(BaseModel):
    user_id: Optional[int] = Field(default=None, ge=1)
    image_url: HttpUrl = Field(description="Cloudinary HTTPS URL (fridge or receipt)")
    scan_type: str = Field(default="fridge", pattern="^(fridge|receipt)$")


class DetectedIngredient(BaseModel):
    name: str
    quantity_estimate: Optional[str] = None
    expiry_date: Optional[date] = None
    expiry_hint: Optional[str] = None


class ScanResponse(BaseModel):
    scan_type: str
    image_url: str
    ingredients: List[DetectedIngredient]
    summary: str
    gamification: Optional["GamificationXpResponse"] = None


class GamificationXpResponse(BaseModel):
    user_id: int
    xp_total: int
    wallet_cents: int
    gold_badges_count: int
    ebook_unlocked: bool
    xp_awarded: int = 0
    wallet_cents_awarded: int = 0
    badges_unlocked: List[str] = Field(default_factory=list)
    firebase_synced: bool = False


class RecipeGenerateRequest(BaseModel):
    user_id: Optional[int] = Field(default=None, ge=1)
    ingredients: List[str] = Field(min_length=1)
    health_options: List[str] = Field(default_factory=list)
    servings: int = Field(default=2, ge=1, le=12)


class GeneratedRecipe(BaseModel):
    titre: str
    ingredients: str
    instructions: str


class RecipeGenerateResponse(BaseModel):
    recipes: List[GeneratedRecipe]
    gamification: Optional[GamificationXpResponse] = None


ScanResponse.model_rebuild()
