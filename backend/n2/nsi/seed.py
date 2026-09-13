from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from n2.nsi.models import NsiProject, NsiSignal
from n2.nsi.schemas import NsiProjectIn, SteppingStoneProject, TargetRadarFilter
from n2.nsi.service import upsert_project

logger = logging.getLogger(__name__)

HERITIA_CORE_SEED = NsiProjectIn(
    project_id="heritia-core",
    name="Heritia",
    category="FoodTech & Gamification",
    maturity_score=85,
    status="ready_for_stepping_stone",
    technical_barriers=[
        "Précision de la reconnaissance d'image multi-ingrédients (frigo)",
        "Calcul en temps réel des valeurs nutritionnelles et DLC",
        "Rétention utilisateur sur la saisie manuelle",
    ],
    core_features=[
        "Scan intelligent frigo & tickets de caisse (Cloudinary + IA N2)",
        "Génération de recettes anti-gaspillage sur-mesure",
        "Gamification complète N2 (XP, badges, cagnotte native)",
        "Vente de livres de recettes digitaux (Stripe Checkout N2)",
    ],
    stepping_stone_projects=[
        SteppingStoneProject(
            id="heritia-b2b-restau",
            name="Heritia Pro - Cockpit Anti-Gaspi Restauration",
            target_segment="C2 - TPE / Commerce de proximité (Restaurateurs, Métiers de bouche)",
            mvp_scope=(
                "PWA simplifiée de gestion de stock en cuisine avec alerte DLC et publication "
                "automatique des surstocks en Ventes Privées sur Selys Marketplace."
            ),
            estimated_mrr_per_client=49.0,
            synergy_portal="Publication des outils de gestion de stock sur le Portail B2B.",
            synergy_selys="Basculement des invendus vers Selys Marketplace (ventes privées anti-gaspi).",
            target_radar_filter=TargetRadarFilter(
                structure_classes=["C2"],
                naf_codes=["5610A", "5610B", "5621Z"],
            ),
        )
    ],
)

DEFAULT_SIGNALS = [
    {
        "title": "Hausse réglementaire anti-gaspillage restauration",
        "source": "veille.reglementaire.fr",
        "impact_score": 78,
        "project_id": "heritia-core",
        "payload": {"theme": "anti_gaspi", "sector": "restauration"},
    },
    {
        "title": "Demande B2B cockpit stock cuisine + marketplace invendus",
        "source": "nsi.convergence",
        "impact_score": 82,
        "project_id": "heritia-core",
        "payload": {"theme": "b2b_stepping_stone", "segment": "C2"},
    },
]


def seed_nsi_defaults(db: Session) -> None:
    """Inject Heritia R&D project and baseline signals if missing (N2 native DB only)."""
    existing = db.query(NsiProject).filter(NsiProject.project_id == "heritia-core").first()
    if existing is None:
        upsert_project(db, HERITIA_CORE_SEED)
        logger.info("NSI seed: injected project heritia-core")
    else:
        logger.info("NSI seed: heritia-core already present")

    for item in DEFAULT_SIGNALS:
        found = (
            db.query(NsiSignal)
            .filter(NsiSignal.title == item["title"], NsiSignal.project_id == item["project_id"])
            .first()
        )
        if found:
            continue
        db.add(
            NsiSignal(
                title=item["title"],
                source=item["source"],
                impact_score=item["impact_score"],
                opportunity_badge="opportunity" if item["impact_score"] >= 60 else "watch",
                project_id=item["project_id"],
                payload=item["payload"],
            )
        )
    db.commit()
