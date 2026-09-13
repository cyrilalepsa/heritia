from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import verify_master_key
from app.database import get_db
from n2.nsi.models import NsiProject
from n2.nsi.schemas import NsiProjectIn, NsiProjectOut, NsiSignalOut, SignalAnalyzeRequest, SignalAnalyzeResponse
from n2.nsi.service import analyze_signal, list_projects, list_signals, upsert_project

router = APIRouter(prefix="/n2/nsi", tags=["n2-nsi"])


@router.get("/projects", response_model=List[NsiProjectOut])
def get_projects(db: Session = Depends(get_db)):
    """Liste tous les projets R&D NSI et leurs projets tremplins."""
    return list_projects(db)


@router.post(
    "/projects",
    response_model=NsiProjectOut,
    dependencies=[Depends(verify_master_key)],
)
def create_or_update_project(payload: NsiProjectIn, db: Session = Depends(get_db)):
    """Crée ou met à jour un projet R&D et ses déclinaisons tremplin."""
    return upsert_project(db, payload)


@router.get("/signals", response_model=List[NsiSignalOut])
def get_signals(
    project_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Récupère les signaux de veille et de convergence."""
    return list_signals(db, project_id=project_id)


@router.post(
    "/signals/analyze",
    response_model=SignalAnalyzeResponse,
    dependencies=[Depends(verify_master_key)],
)
def analyze_convergence_signal(payload: SignalAnalyzeRequest, db: Session = Depends(get_db)):
    """Analyse un signal et génère le kit Fast-Track (filtres NeriaRadar, actions Portail/Selys)."""
    try:
        return analyze_signal(db, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/health")
def nsi_health(db: Session = Depends(get_db)):
    count = db.query(NsiProject).count()
    return {"status": "ok", "module": "nsi", "projects_count": count}
