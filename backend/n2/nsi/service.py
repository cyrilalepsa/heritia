from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from n2.nsi.models import NsiProject, NsiSignal
from n2.nsi.schemas import (
    FastTrackKit,
    NsiProjectIn,
    NsiProjectOut,
    NsiSignalOut,
    SignalAnalyzeRequest,
    SignalAnalyzeResponse,
    TargetRadarFilter,
)

PROJECT_FAST_TRACK_PROFILES: dict[str, dict] = {
    "heritia-core": {
        "target_audience": "B2C — Particuliers",
        "perimeter": "Scan perso, recettes, gamification XP, livres digitaux (100% autonome)",
        "neria_radar_filters": TargetRadarFilter(structure_classes=["C1"], naf_codes=[]),
        "recommended_actions": [
            "Optimiser le funnel scan frigo → recette → livre digital",
            "Renforcer la rétention gamification (XP, badges, cagnotte N2 native)",
            "Itérer sur la précision OCR multi-ingrédients Cloudinary",
        ],
        "recommended_mvp": "PWA B2C : scan frigo + génération recettes + boutique ebooks Stripe.",
        "export_label": "Exporter filtres B2C vers NeriaRadar",
    },
    "aevis-core": {
        "target_audience": "B2B — Commerçants C2",
        "perimeter": "POS tactile, stock et inventaire commerçants (100% autonome)",
        "neria_radar_filters": TargetRadarFilter(
            structure_classes=["C2"],
            naf_codes=["4711D", "4719B", "4778C"],
        ),
        "recommended_actions": [
            "Déployer le pilote POS tactile sur un panel TPE C2",
            "Valider les alertes stock temps réel multi-postes",
            "Préparer l'export comptable et l'onboarding commerçant",
        ],
        "recommended_mvp": "PWA POS tactile + inventaire + alertes stock pour commerçants C2.",
        "export_label": "Exporter filtres commerçants C2 vers NeriaRadar",
    },
    "selys-core": {
        "target_audience": "Particuliers, Artisans/Pros & Membres N2O",
        "perimeter": (
            "Écosystème unifié Selys : volet Service/Recrutement (Direct-Pay, Zero-Retention) "
            "+ volet Marketplace (vitrine locale, Click & Collect, Ventes Privées N2O)"
        ),
        "neria_radar_filters": TargetRadarFilter(
            structure_classes=["C2", "C3"],
            naf_codes=["8121Z", "8122Z", "8130Z", "4711D", "5610A", "5610B"],
        ),
        "recommended_actions": [
            "Volet Service : finaliser recrutement direct (micro-jobs, CDD, CDI) et Direct-Pay",
            "Volet Service : auditer la purge Zero-Retention du casier judiciaire",
            "Volet Marketplace : lancer vitrine géolocalisée et Click & Collect sur zone pilote",
            "Volet Marketplace : activer Ventes Privées / Bons Plans membres N2O",
        ],
        "recommended_mvp": (
            "Plateforme Selys unifiée : matching + recrutement + marketplace locale + Ventes Privées N2O."
        ),
        "export_label": "Exporter filtres écosystème Selys vers NeriaRadar",
    },
}


def _serialize_modules(modules) -> list:
    serialized = []
    for item in modules or []:
        if hasattr(item, "model_dump"):
            serialized.append(item.model_dump())
        elif isinstance(item, dict):
            serialized.append(item)
    return serialized


def _project_out(row: NsiProject) -> NsiProjectOut:
    return NsiProjectOut(
        id=row.id,
        project_id=row.project_id,
        name=row.name,
        category=row.category,
        target_audience=getattr(row, "target_audience", "") or "",
        perimeter=getattr(row, "perimeter", "") or "",
        maturity_score=row.maturity_score,
        status=row.status,
        technical_barriers=row.technical_barriers or [],
        core_features=row.core_features or [],
        integrated_modules=getattr(row, "integrated_modules", None) or [],
        stepping_stone_projects=row.stepping_stone_projects or [],
        created_at=row.created_at.isoformat() if row.created_at else None,
        updated_at=row.updated_at.isoformat() if row.updated_at else None,
    )


def _signal_out(row: NsiSignal) -> NsiSignalOut:
    return NsiSignalOut(
        id=row.id,
        title=row.title,
        source=row.source,
        impact_score=row.impact_score,
        opportunity_badge=row.opportunity_badge,
        project_id=row.project_id,
        payload=row.payload or {},
        fast_track_kit=row.fast_track_kit,
        created_at=row.created_at.isoformat() if row.created_at else None,
    )


def list_projects(db: Session) -> List[NsiProjectOut]:
    rows = db.query(NsiProject).order_by(NsiProject.maturity_score.desc()).all()
    return [_project_out(row) for row in rows]


def upsert_project(db: Session, payload: NsiProjectIn) -> NsiProjectOut:
    row = db.query(NsiProject).filter(NsiProject.project_id == payload.project_id).first()
    data = payload.model_dump()
    stepping = _serialize_modules(payload.stepping_stone_projects)
    integrated = _serialize_modules(payload.integrated_modules)

    if row is None:
        row = NsiProject(
            project_id=data["project_id"],
            name=data["name"],
            category=data["category"],
            target_audience=data.get("target_audience", ""),
            perimeter=data.get("perimeter", ""),
            maturity_score=data["maturity_score"],
            status=data["status"],
            technical_barriers=data["technical_barriers"],
            core_features=data["core_features"],
            integrated_modules=integrated,
            stepping_stone_projects=stepping,
        )
        db.add(row)
    else:
        row.name = data["name"]
        row.category = data["category"]
        row.target_audience = data.get("target_audience", "")
        row.perimeter = data.get("perimeter", "")
        row.maturity_score = data["maturity_score"]
        row.status = data["status"]
        row.technical_barriers = data["technical_barriers"]
        row.core_features = data["core_features"]
        row.integrated_modules = integrated
        row.stepping_stone_projects = stepping

    db.commit()
    db.refresh(row)
    return _project_out(row)


def list_signals(db: Session, project_id: Optional[str] = None) -> List[NsiSignalOut]:
    query = db.query(NsiSignal)
    if project_id:
        query = query.filter(NsiSignal.project_id == project_id)
    rows = query.order_by(NsiSignal.impact_score.desc(), NsiSignal.created_at.desc()).all()
    return [_signal_out(row) for row in rows]


def _opportunity_badge(impact_score: int) -> str:
    if impact_score >= 80:
        return "fast_track"
    if impact_score >= 60:
        return "opportunity"
    return "watch"


def build_fast_track_kit(db: Session, *, project_id: str, signal_title: str, impact_score: int) -> FastTrackKit:
    project = db.query(NsiProject).filter(NsiProject.project_id == project_id).first()
    profile = PROJECT_FAST_TRACK_PROFILES.get(project_id, PROJECT_FAST_TRACK_PROFILES["heritia-core"])

    target_audience = profile["target_audience"]
    perimeter = profile["perimeter"]
    if project:
        if getattr(project, "target_audience", ""):
            target_audience = project.target_audience
        if getattr(project, "perimeter", ""):
            perimeter = project.perimeter

    return FastTrackKit(
        project_id=project_id,
        signal_title=signal_title,
        opportunity_badge=_opportunity_badge(impact_score),
        target_audience=target_audience,
        perimeter=perimeter,
        neria_radar_filters=profile["neria_radar_filters"],
        recommended_actions=profile["recommended_actions"],
        recommended_mvp=profile["recommended_mvp"],
        export_label=profile["export_label"],
    )


def analyze_signal(db: Session, payload: SignalAnalyzeRequest) -> SignalAnalyzeResponse:
    project_id = payload.project_id or "heritia-core"
    title = payload.title or "Signal de convergence"
    source = payload.source or "nsi.manual"

    signal = None
    if payload.signal_id:
        signal = db.query(NsiSignal).filter(NsiSignal.id == payload.signal_id).first()
        if not signal:
            raise LookupError("Signal not found")
        title = signal.title
        source = signal.source
        project_id = signal.project_id or project_id
        payload.impact_score = signal.impact_score

    fast_track = build_fast_track_kit(
        db,
        project_id=project_id,
        signal_title=title,
        impact_score=payload.impact_score,
    )

    if signal is None:
        signal = NsiSignal(
            title=title,
            source=source,
            impact_score=payload.impact_score,
            opportunity_badge=_opportunity_badge(payload.impact_score),
            project_id=project_id,
            payload={"analyzed": True},
        )
        db.add(signal)
    else:
        signal.opportunity_badge = _opportunity_badge(payload.impact_score)

    signal.fast_track_kit = fast_track.model_dump()
    db.commit()
    db.refresh(signal)

    return SignalAnalyzeResponse(signal=_signal_out(signal), fast_track=fast_track)
