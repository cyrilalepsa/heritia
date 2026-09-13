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


def _project_out(row: NsiProject) -> NsiProjectOut:
    return NsiProjectOut(
        id=row.id,
        project_id=row.project_id,
        name=row.name,
        category=row.category,
        maturity_score=row.maturity_score,
        status=row.status,
        technical_barriers=row.technical_barriers or [],
        core_features=row.core_features or [],
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
    stepping = []
    for item in payload.stepping_stone_projects:
        if hasattr(item, "model_dump"):
            stepping.append(item.model_dump())
        elif isinstance(item, dict):
            stepping.append(item)
        else:
            stepping.append(dict(item))

    if row is None:
        row = NsiProject(
            project_id=data["project_id"],
            name=data["name"],
            category=data["category"],
            maturity_score=data["maturity_score"],
            status=data["status"],
            technical_barriers=data["technical_barriers"],
            core_features=data["core_features"],
            stepping_stone_projects=stepping,
        )
        db.add(row)
    else:
        row.name = data["name"]
        row.category = data["category"]
        row.maturity_score = data["maturity_score"]
        row.status = data["status"]
        row.technical_barriers = data["technical_barriers"]
        row.core_features = data["core_features"]
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
    stepping = (project.stepping_stone_projects or [{}])[0] if project else {}
    radar = stepping.get("target_radar_filter") or {}
    filters = TargetRadarFilter(
        structure_classes=radar.get("structure_classes") or ["C2"],
        naf_codes=radar.get("naf_codes") or ["5610A", "5610B", "5621Z"],
    )
    return FastTrackKit(
        project_id=project_id,
        signal_title=signal_title,
        opportunity_badge=_opportunity_badge(impact_score),
        neria_radar_filters=filters,
        portal_actions=[
            "Publier l'outil de gestion de stock sur le Portail B2B",
            stepping.get("synergy_portal") or "Publication des outils de gestion de stock sur le Portail B2B.",
        ],
        selys_actions=[
            "Activer le flux surstocks → Ventes Privées Selys Marketplace",
            stepping.get("synergy_selys") or "Basculement des invendus vers Selys Marketplace.",
        ],
        recommended_mvp=stepping.get("mvp_scope") or "MVP PWA stock cuisine + alertes DLC.",
        export_label="Exporter les filtres vers NeriaRadar",
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
