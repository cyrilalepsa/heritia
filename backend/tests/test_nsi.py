from __future__ import annotations

import os

os.environ.setdefault("N2_MASTER_KEY", "test-nsi-master-key")
os.environ.setdefault("HERITIA_ENVIRONMENT", "development")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from n2.nsi.seed import seed_nsi_defaults

Base.metadata.create_all(bind=engine)

client = TestClient(app)
MASTER_HEADERS = {"X-Master-Key": "test-nsi-master-key"}


@pytest.fixture(autouse=True)
def _seed_db():
    db = SessionLocal()
    seed_nsi_defaults(db)
    db.close()


def test_projects_lists_seeded_heritia_core():
    response = client.get("/api/n2/nsi/projects")
    assert response.status_code == 200
    data = response.json()
    assert any(item["project_id"] == "heritia-core" for item in data)
    heritia = next(item for item in data if item["project_id"] == "heritia-core")
    assert heritia["maturity_score"] == 85
    assert len(heritia["stepping_stone_projects"]) >= 1


def test_post_projects_rejects_missing_master_key():
    response = client.post(
        "/api/n2/nsi/projects",
        json={"project_id": "tmp", "name": "Tmp"},
    )
    assert response.status_code == 401
    assert "X-Master-Key" in response.json()["detail"]


def test_post_projects_accepts_valid_master_key():
    response = client.post(
        "/api/n2/nsi/projects",
        json={
            "project_id": "heritia-core",
            "name": "Heritia Updated",
            "category": "FoodTech",
            "maturity_score": 86,
        },
        headers=MASTER_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["maturity_score"] == 86


def test_signals_analyze_requires_master_key():
    response = client.post(
        "/api/n2/nsi/signals/analyze",
        json={"title": "Test signal", "project_id": "heritia-core"},
    )
    assert response.status_code == 401


def test_signals_analyze_generates_fast_track():
    response = client.post(
        "/api/n2/nsi/signals/analyze",
        json={
            "title": "Signal test Fast-Track",
            "project_id": "heritia-core",
            "impact_score": 84,
        },
        headers=MASTER_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["fast_track"]["project_id"] == "heritia-core"
    assert body["fast_track"]["neria_radar_filters"]["structure_classes"] == ["C2"]


def test_cockpit_registry_contains_nsi():
    response = client.get("/api/n2/cockpit/registry")
    assert response.status_code == 200
    modules = response.json()["modules"]
    assert any(item["id"] == "nsi" for item in modules)
