"""Response and request schemas. These are the OpenAPI contract the web client is generated from."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr
from pydantic import Field as PField


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = PField(min_length=12, max_length=256)
    tenant_name: str = PField(min_length=1, max_length=200)
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: str
    display_name: str


class TenantOut(BaseModel):
    id: UUID
    name: str
    slug: str


class SessionOut(BaseModel):
    user: UserOut
    tenant: TenantOut
    role: str
    csrf_token: str


class ModelVersionOut(BaseModel):
    id: UUID
    kind: str
    name: str
    pinned: bool
    config: dict[str, Any]
    metrics: dict[str, Any]
    created_at: datetime


class JobOut(BaseModel):
    id: UUID
    kind: str
    status: str
    queue: str
    attempts: int
    error: str | None = None
    created_at: datetime


class PageOut(BaseModel):
    number: int
    width: int
    height: int
    image_url: str
    quality: dict[str, float] | None = None
    ocr_words: list[OcrWordOut] = PField(default_factory=list)


class AlternativeOut(BaseModel):
    rank: int
    value: str | None
    probability: float


class CorrectionOut(BaseModel):
    old_value: str | None
    new_value: str | None
    created_at: datetime


class FieldOut(BaseModel):
    id: UUID
    name: str
    line_index: int | None
    value: str | None
    normalized_value: str | None
    raw_confidence: float | None
    calibrated_confidence: float | None
    grounded: bool
    boxes: list[list[float]]
    stability: float | None
    alternatives: list[AlternativeOut]
    corrections: list[CorrectionOut] = PField(default_factory=list)


class OcrWordOut(BaseModel):
    text: str
    box: list[float]
    score: float


class VerifierResultOut(BaseModel):
    rule: str
    passed: bool
    field_id: UUID | None
    detail: dict[str, Any] | None


class VerdictOut(BaseModel):
    decision: str
    reasons: list[dict[str, Any]]
    threshold: float | None


class ExtractionOut(BaseModel):
    id: UUID
    model_version: ModelVersionOut
    ocr_version: ModelVersionOut | None
    latency_ms: int | None
    fields: list[FieldOut]
    verifier_results: list[VerifierResultOut]
    verdict: VerdictOut | None
    created_at: datetime


class DocumentOut(BaseModel):
    id: UUID
    kind: str
    original_filename: str
    status: str
    page_count: int
    difficulty: float | None
    vendor_id: UUID | None
    created_at: datetime
    updated_at: datetime


class DocumentRowOut(DocumentOut):
    """A list row carries what the inbox shows (D-041 P2): thumbnail, vendor, verdict, counts."""

    thumbnail_url: str | None = None
    vendor_name: str | None = None
    decision: str | None = None
    reasons: list[dict[str, Any]] = PField(default_factory=list)
    field_count: int = 0
    grounded_fields: int = 0


class DocumentDetailOut(DocumentOut):
    pages: list[PageOut]
    extraction: ExtractionOut | None
    job: JobOut | None
    vendor_name: str | None = None
    approved: bool = False


class UploadAccepted(BaseModel):
    document: DocumentOut
    job: JobOut


class Paginated[T](BaseModel):
    items: list[T]
    total: int


class PlanOut(BaseModel):
    code: str
    name: str
    monthly_price_cents: int
    included_documents: int
    per_document_cents: int
    features: list[Any]


class JobCreate(BaseModel):
    kind: str
    payload: dict[str, Any] = PField(default_factory=dict)


class DatasetOut(BaseModel):
    id: UUID
    name: str
    kind: str
    sources: list[Any]
    split_policy: dict[str, Any]
    counts: dict[str, int]
    created_at: datetime


class EvalScoreOut(BaseModel):
    field_name: str | None
    vendor_id: UUID | None
    split: str
    metric: str
    value: float
    support: int | None


class ModelVersionDetailOut(ModelVersionOut):
    parent_id: UUID | None
    dataset_id: UUID | None
    job_id: UUID | None
    artifact_object_key: str | None
    card: str | None
    eval_summary: dict[str, Any] | None
    scores: list[EvalScoreOut]
    pinned_at: datetime | None


class VendorOut(BaseModel):
    id: UUID
    name: str
    documents: int
    corrections: int
    curve: list[dict[str, Any]]


class ProductionOut(BaseModel):
    pinned: dict[str, ModelVersionOut]
    documents: dict[str, int]
    jobs: dict[str, int]
    billing_provider: str
    open_signals: int
