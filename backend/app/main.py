from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, marketplace, profil, recipes
from routes import heritia as heritia_routes
from routes import nsi as nsi_routes
from app.config import settings
from app.database import Base, SessionLocal, engine
from n2.nsi.seed import seed_nsi_defaults

Base.metadata.create_all(bind=engine)

with SessionLocal() as _db:
    seed_nsi_defaults(_db)

app = FastAPI(title=settings.app_name, version="1.0.0")

# CORS: localhost (dev) + https://heritia.neriacorp.com (prod via N2 Single Ingress)
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
app.include_router(heritia_routes.router, prefix="/api")
app.include_router(nsi_routes.router, prefix="/api")


@app.get("/api/n2/cockpit/registry")
def cockpit_registry():
    from n2.config_registry import COCKPIT_REGISTRY

    return {"modules": COCKPIT_REGISTRY}


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "HERITIA"}