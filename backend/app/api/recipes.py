from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.recipe import UserRecipe
from app.models.user import User
from app.schemas.recipe import UserRecipeCreate, UserRecipeOut, UserRecipeValidation

router = APIRouter(prefix="/recettes", tags=["recettes"])


@router.get("", response_model=List[UserRecipeOut])
def list_my_recipes(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(UserRecipe)
        .filter(UserRecipe.user_id == user.id)
        .order_by(UserRecipe.created_at.desc())
        .all()
    )


@router.post("", response_model=UserRecipeOut)
def create_recipe(
    payload: UserRecipeCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = UserRecipe(
        user_id=user.id,
        titre=payload.titre,
        ingredients=payload.ingredients,
        instructions=payload.instructions,
        admin_validated=False,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.patch("/{recipe_id}/validate", response_model=UserRecipeOut)
def validate_recipe(
    recipe_id: int,
    payload: UserRecipeValidation,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin validation endpoint (authz to be refined later)."""
    recipe = db.query(UserRecipe).filter(UserRecipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.admin_validated = payload.admin_validated
    db.commit()
    db.refresh(recipe)
    return recipe