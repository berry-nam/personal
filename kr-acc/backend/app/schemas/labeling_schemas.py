"""Pydantic schemas for the labeling tool API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Auth ──────────────────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    email: str
    display_name: str
    password: str = Field(min_length=6)
    invite_code: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "LabelingUserOut"


class LabelingUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str
    role: str
    created_at: datetime


# ── Tasks ─────────────────────────────────────────────────────────────────────


class TaskSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query_id: str
    query_text: str
    query_metadata: dict
    status: str
    assigned_to: int | None
    assigned_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    result_count: int = 0
    label_count: int = 0


class TaskResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    company_metadata: dict | None
    rank_position: int | None


class RubricScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    criterion_id: int
    criterion_name: str = ""
    score: str
    note: str | None


class LabelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    result_id: int
    labeler_id: int
    overall_rating: int
    rank_position: int | None
    justification: str | None
    rubric_scores: list[RubricScoreOut] = []


class TaskDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query_id: str
    query_text: str
    query_metadata: dict
    status: str
    assigned_to: int | None
    results: list[TaskResultOut] = []
    labels: list[LabelOut] = []


class TaskListResponse(BaseModel):
    items: list[TaskSummaryOut]
    total: int
    page: int
    size: int
    pages: int


# ── Labels (submit) ──────────────────────────────────────────────────────────


class RubricScoreInput(BaseModel):
    criterion_id: int
    score: str = Field(pattern=r"^(yes|partially|no|na)$")
    note: str | None = None


class LabelInput(BaseModel):
    result_id: int
    overall_rating: int = Field(ge=1, le=5)
    rank_position: int | None = None
    justification: str | None = None
    rubric_scores: list[RubricScoreInput] = []


class SubmitLabelsRequest(BaseModel):
    labels: list[LabelInput]


# ── Rubric ────────────────────────────────────────────────────────────────────


class RubricCriterionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    weight: int
    criteria_type: str
    display_order: int
    is_active: bool


class RubricCriterionCreate(BaseModel):
    name: str
    description: str | None = None
    weight: int = Field(default=3, ge=1, le=5)
    criteria_type: str = "other"
    display_order: int = 0


# ── Admin ─────────────────────────────────────────────────────────────────────


class TaskResultInput(BaseModel):
    company_name: str
    company_metadata: dict | None = None
    rank_position: int | None = None


class AddResultsRequest(BaseModel):
    results: list[TaskResultInput]


class AddCompanyRequest(BaseModel):
    company_name: str
    company_metadata: dict | None = None


class BatchResultsRequest(BaseModel):
    """Bulk add results: map of query_id → list of results."""
    tasks: dict[str, list[TaskResultInput]]


class ProgressOut(BaseModel):
    total_tasks: int
    pending: int
    assigned: int
    completed: int
    reviewed: int
    per_labeler: list[dict]


class ExportEntry(BaseModel):
    query_id: str
    query_text: str
    query_metadata: dict
    results: list[dict]
