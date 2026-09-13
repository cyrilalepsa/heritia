from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TargetRadarFilter(BaseModel):
    structure_classes: List[str] = Field(default_factory=list)
    naf_codes: List[str] = Field(default_factory=list)


class SteppingStoneProject(BaseModel):
    id: str
    name: str
    target_segment: str
    mvp_scope: str
    estimated_mrr_per_client: float
    target_radar_filter: TargetRadarFilter = Field(default_factory=TargetRadarFilter)


class NsiProjectIn(BaseModel):
    project_id: str = Field(min_length=1, max_length=64)
    name: str
    category: str = ""
    target_audience: str = ""
    perimeter: str = ""
    maturity_score: int = Field(default=0, ge=0, le=100)
    status: str = "draft"
    technical_barriers: List[str] = Field(default_factory=list)
    core_features: List[str] = Field(default_factory=list)
    stepping_stone_projects: List[SteppingStoneProject] = Field(default_factory=list)


class NsiProjectOut(NsiProjectIn):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class NsiSignalOut(BaseModel):
    id: int
    title: str
    source: str
    impact_score: int
    opportunity_badge: str
    project_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    fast_track_kit: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class SignalAnalyzeRequest(BaseModel):
    signal_id: Optional[int] = None
    title: Optional[str] = None
    source: Optional[str] = None
    impact_score: int = Field(default=50, ge=0, le=100)
    project_id: Optional[str] = "heritia-core"


class FastTrackKit(BaseModel):
    project_id: str
    signal_title: str
    opportunity_badge: str
    target_audience: str
    perimeter: str
    neria_radar_filters: TargetRadarFilter
    recommended_actions: List[str]
    recommended_mvp: str
    export_label: str


class SignalAnalyzeResponse(BaseModel):
    signal: NsiSignalOut
    fast_track: FastTrackKit
