from __future__ import annotations

import os

os.environ.setdefault("N2_MASTER_KEY", "test-nsi-master-key")
os.environ.setdefault("HERITIA_ENVIRONMENT", "development")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from n2.nsi.seed import CANONICAL_PROJECT_IDS, seed_nsi_defaults

Base.metadata.create_all(bind=engine)

client = TestClient(app)
MASTER_HEADERS = {"X-Master-Key": "test-nsi-master-key"}


@pytest.fixture(autouse=True)
def _seed_db():
    db = SessionLocal()
    seed_nsi_defaults(db)
    db.close()


def test_projects_lists_four_canonical_projects():
    response = client.get("/api/n2/nsi/projects")
    assert response.status_code == 200
    data = response.json()
    project_ids = {item["project_id"] for item in data}
    assert project_ids == set(CANONICAL_PROJECT_IDS)


def test_heritia_core_is_autonomous_b2c():
    response = client.get("/api/n2/nsi/projects")
    heritia = next(item for item in response.json() if item["project_id"] == "heritia-core")
    assert heritia["maturity_score"] == 85
    assert heritia["target_audience"] == "B2C — Particuliers"
    assert heritia["stepping_stone_projects"] == []
    assert "Selys" not in heritia["perimeter"]
    assert "Aevis" not in heritia["perimeter"]


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


def test_signals_analyze_generates_autonomous_fast_track():
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
    fast_track = body["fast_track"]
    assert fast_track["project_id"] == "heritia-core"
    assert fast_track["neria_radar_filters"]["structure_classes"] == ["C1"]
    assert fast_track["target_audience"] == "B2C — Particuliers"
    assert "recommended_actions" in fast_track
    assert "portal_actions" not in fast_track
    assert "selys_actions" not in fast_track
    assert all("Selys" not in action for action in fast_track["recommended_actions"])


def test_selys_and_marketplace_are_separate_projects():
    response = client.get("/api/n2/nsi/projects")
    data = {item["project_id"]: item for item in response.json()}
    assert "selys-core" in data
    assert "selys-marketplace-core" in data
    assert data["selys-core"]["name"] == "Selys"
    assert data["selys-marketplace-core"]["name"] == "Selys Marketplace"
    assert data["selys-core"]["project_id"] != data["selys-marketplace-core"]["project_id"]


def test_cockpit_registry_contains_nsi():
    response = client.get("/api/n2/cockpit/registry")
    assert response.status_code == 200
    modules = response.json()["modules"]
    assert any(item["id"] == "nsi" for item in modules)
