from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, marketplace, profil, recipes
from app.config import settings
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")

# CORS: localhost (dev) + https://heritia.neriacorp.com (prod)
_cors_origins = list(dict.fromkeys(settings.cors_origin_list))
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(profil.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(marketplace.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "HERITIA"}