from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from n2.nsi.models import NsiProject, NsiSignal
from n2.nsi.schemas import NsiProjectIn
from n2.nsi.service import upsert_project

logger = logging.getLogger(__name__)

CANONICAL_PROJECT_IDS = (
    "heritia-core",
    "aevis-core",
    "selys-core",
    "selys-marketplace-core",
)

CANONICAL_PROJECTS: tuple[NsiProjectIn, ...] = (
    NsiProjectIn(
        project_id="heritia-core",
        name="Heritia",
        category="FoodTech & Gamification",
        target_audience="B2C — Particuliers",
        perimeter=(
            "Scan frigo et tickets de caisse personnels, génération de recettes anti-gaspillage, "
            "gamification XP et cagnotte N2 native, vente de livres de recettes digitaux."
        ),
        maturity_score=85,
        status="production_ready",
        technical_barriers=[
            "Précision de la reconnaissance d'image multi-ingrédients (frigo)",
            "Calcul en temps réel des valeurs nutritionnelles et dates de péremption",
            "Rétention utilisateur sur la saisie manuelle",
        ],
        core_features=[
            "Scan intelligent frigo & tickets de caisse (Cloudinary + IA N2)",
            "Génération de recettes anti-gaspillage sur-mesure",
            "Gamification complète N2 (XP, badges, cagnotte native)",
            "Vente de livres de recettes digitaux (Stripe Checkout N2)",
        ],
        stepping_stone_projects=[],
    ),
    NsiProjectIn(
        project_id="aevis-core",
        name="Aevis",
        category="Retail Tech & POS B2B",
        target_audience="B2B — Commerçants C2",
        perimeter=(
            "Terminal de caisse tactile autonome, gestion de stock et inventaire "
            "pour TPE / commerces de proximité."
        ),
        maturity_score=72,
        status="pilot",
        technical_barriers=[
            "Synchronisation stock temps réel multi-postes",
            "Compatibilité matérielle caisses tactiles hétérogènes",
            "Onboarding commerçant sans formation lourde",
        ],
        core_features=[
            "POS tactile autonome N2",
            "Inventaire et alertes stock commerçants [C2]",
            "Tableau de bord ventes et marges",
            "Export comptable et historique transactions",
        ],
        stepping_stone_projects=[],
    ),
    NsiProjectIn(
        project_id="selys-core",
        name="Selys",
        category="Services & Recrutement Direct",
        target_audience="Particulier ↔ Artisan / Pro",
        perimeter=(
            "Mise en relation service et recrutement direct (petits boulots, CDD, CDI). "
            "Direct-Pay : facturation et contrats directs hors flux NeriaCorp. "
            "Casier judiciaire à l'inscription, suppression immédiate post-validation (Zero-Retention)."
        ),
        maturity_score=68,
        status="pilot",
        technical_barriers=[
            "Workflow recrutement direct conforme (CDD/CDI/micro-jobs)",
            "Direct-Pay hors flux NeriaCorp avec traçabilité légale",
            "Zero-Retention casier judiciaire (collecte → validation → purge immédiate)",
        ],
        core_features=[
            "Matching particulier ↔ artisan / professionnel",
            "Recrutement direct (petits boulots, CDD, CDI)",
            "Direct-Pay : facturation et contrats directs",
            "Casier judiciaire Zero-Retention (purge post-validation)",
        ],
        stepping_stone_projects=[],
    ),
    NsiProjectIn(
        project_id="selys-marketplace-core",
        name="Selys Marketplace",
        category="Marketplace Locale & Ventes Privées",
        target_audience="Membres N2O & commerces locaux",
        perimeter=(
            "Vitrine locale géolocalisée (modèle Uber), commandes et livraison locale, "
            "Ventes Privées et Bons Plans membres N2O. Application autonome, distincte de Selys core."
        ),
        maturity_score=64,
        status="draft",
        technical_barriers=[
            "Référencement géolocalisé temps réel (style Uber)",
            "Logistique livraison locale multi-commerçants",
            "Gestion Ventes Privées / Bons Plans membres N2O",
        ],
        core_features=[
            "Vitrine locale géolocalisée",
            "Commandes et livraison locale",
            "Ventes Privées anti-gaspi / Bons Plans membres N2O",
            "Catalogue commerçants indépendant de Selys core",
        ],
        stepping_stone_projects=[],
    ),
)

CANONICAL_SIGNALS: tuple[dict, ...] = (
    {
        "title": "Adoption PWA anti-gaspillage grand public",
        "source": "veille.foodtech.fr",
        "impact_score": 76,
        "project_id": "heritia-core",
        "payload": {"theme": "b2c_adoption", "segment": "C1"},
    },
    {
        "title": "Demande POS tactile stock temps réel TPE",
        "source": "veille.retail.fr",
        "impact_score": 71,
        "project_id": "aevis-core",
        "payload": {"theme": "pos_stock", "segment": "C2"},
    },
    {
        "title": "Recrutement direct micro-jobs et conformité casier",
        "source": "veille.travail.fr",
        "impact_score": 69,
        "project_id": "selys-core",
        "payload": {"theme": "direct_hire", "segment": "pro_particulier"},
    },
    {
        "title": "Ventes privées locales et livraison hyper-proximité",
        "source": "veille.marketplace.fr",
        "impact_score": 67,
        "project_id": "selys-marketplace-core",
        "payload": {"theme": "local_marketplace", "segment": "N2O"},
    },
)

STALE_SIGNAL_TITLES = (
    "Demande B2B cockpit stock cuisine + marketplace invendus",
    "Hausse réglementaire anti-gaspillage restauration",
)


def _ensure_nsi_schema(db: Session) -> None:
    """Add missing columns on existing SQLite deployments (lightweight migration)."""
    from sqlalchemy import inspect, text

    bind = db.get_bind()
    inspector = inspect(bind)
    if "nsi_projects" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("nsi_projects")}
    if "target_audience" not in columns:
        db.execute(text("ALTER TABLE nsi_projects ADD COLUMN target_audience VARCHAR(255) DEFAULT ''"))
    if "perimeter" not in columns:
        db.execute(text("ALTER TABLE nsi_projects ADD COLUMN perimeter TEXT DEFAULT ''"))
    db.commit()


def seed_nsi_defaults(db: Session) -> None:
    """Reset and inject canonical NSI projects (100% autonomous, no cross-app bridging)."""
    _ensure_nsi_schema(db)
    for project in CANONICAL_PROJECTS:
        upsert_project(db, project)
        logger.info("NSI seed: refreshed project %s", project.project_id)

    stale_projects = (
        db.query(NsiProject)
        .filter(NsiProject.project_id.notin_(CANONICAL_PROJECT_IDS))
        .all()
    )
    for row in stale_projects:
        db.delete(row)
        logger.info("NSI seed: removed stale project %s", row.project_id)

    for title in STALE_SIGNAL_TITLES:
        stale_signals = db.query(NsiSignal).filter(NsiSignal.title == title).all()
        for signal in stale_signals:
            db.delete(signal)
            logger.info("NSI seed: removed stale signal %r", title)

    for item in CANONICAL_SIGNALS:
        found = (
            db.query(NsiSignal)
            .filter(NsiSignal.title == item["title"], NsiSignal.project_id == item["project_id"])
            .first()
        )
        if found:
            found.source = item["source"]
            found.impact_score = item["impact_score"]
            found.opportunity_badge = "opportunity" if item["impact_score"] >= 60 else "watch"
            found.payload = item["payload"]
            found.fast_track_kit = None
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
