from __future__ import annotations

from pydantic import BaseModel, Field


class UserRecipeCreate(BaseModel):
    titre: str = Field(min_length=1, max_length=255)
    ingredients: str = Field(min_length=1)
    instructions: str = Field(min_length=1)


class UserRecipeOut(BaseModel):
    id: int
    user_id: int
    titre: str
    ingredients: str
    instructions: str
    admin_validated: bool

    class Config:
        from_attributes = True


class UserRecipeValidation(BaseModel):
    admin_validated: bool