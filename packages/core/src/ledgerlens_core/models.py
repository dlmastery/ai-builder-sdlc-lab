"""Domain model — every entity from spec §3, one table each.

Conventions: UUID primary keys; `tenant_id` on every tenant-owned row; timestamps in UTC;
JSONB for evidence payloads whose shape is owned by the ML package; database-enforced
invariants where they are cheap (one pinned version per kind, unique idempotency keys).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map: ClassVar[dict[Any, Any]] = {dict[str, Any]: JSONB, list[Any]: JSONB}


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _created_at() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


def _tenant_fk() -> Mapped[uuid.UUID]:
    return mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)


def _jsonb_object() -> Mapped[dict[str, Any]]:
    return mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))


def _jsonb_array() -> Mapped[list[Any]]:
    return mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))


def _str_default(length: int, value: str, *, index: bool = False) -> Mapped[str]:
    return mapped_column(
        String(length), nullable=False, default=value, server_default=value, index=index
    )


def _bool_false() -> Mapped[bool]:
    return mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))


def _int_zero() -> Mapped[int]:
    return mapped_column(Integer, nullable=False, default=0, server_default=text("0"))


# --- identity -----------------------------------------------------------------------------


class Role(enum.StrEnum):
    owner = "owner"
    finance_lead = "finance_lead"
    clerk = "clerk"
    data_lead = "data_lead"


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[uuid.UUID] = _uuid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    created_at: Mapped[datetime] = _created_at()


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = _uuid_pk()
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = _created_at()


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uq_membership"),)
    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID] = _tenant_fk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)


class Session(Base):
    """Server-side session; the cookie carries only the token whose hash is this row's id."""

    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # sha256(token)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = _tenant_fk()
    csrf_token: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = _created_at()


# --- documents ----------------------------------------------------------------------------


class DocumentStatus(enum.StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    needs_review = "needs_review"
    auto_approved = "auto_approved"
    approved = "approved"
    failed = "failed"


class Vendor(Base):
    __tablename__ = "vendors"
    __table_args__ = (UniqueConstraint("tenant_id", "normalized_name", name="uq_vendor_name"),)
    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID] = _tenant_fk()
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(300), nullable=False)
    created_at: Mapped[datetime] = _created_at()


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID] = _tenant_fk()
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    kind: Mapped[str] = _str_default(16, "unknown")
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = _str_default(24, DocumentStatus.uploaded.value, index=True)
    page_count: Mapped[int] = _int_zero()
    difficulty: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = _created_at()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    pages: Mapped[list[Page]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class Page(Base):
    __tablename__ = "pages"
    __table_args__ = (UniqueConstraint("document_id", "number", name="uq_page_number"),)
    id: Mapped[uuid.UUID] = _uuid_pk()
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = _tenant_fk()
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    ocr_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    quality: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    # hash of the normalised page image (not the uploaded file): the same page in a different
    # file is a duplicate the queue names (migration 0002)
    content_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)

    document: Mapped[Document] = relationship(back_populates="pages")


# --- extraction ---------------------------------------------------------------------------


class Extraction(Base):
    __tablename__ = "extractions"
    id: Mapped[uuid.UUID] = _uuid_pk()
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = _tenant_fk()
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("model_versions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ocr_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("model_versions.id", ondelete="RESTRICT"), nullable=True
    )
    status: Mapped[str] = _str_default(24, "completed")
    raw_output: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = _created_at()

    fields: Mapped[list[Field]] = relationship(
        back_populates="extraction", cascade="all, delete-orphan"
    )
    verifier_results: Mapped[list[VerifierResult]] = relationship(
        back_populates="extraction", cascade="all, delete-orphan"
    )
    verdict: Mapped[Verdict | None] = relationship(
        back_populates="extraction", uselist=False, cascade="all, delete-orphan"
    )


class Field(Base):
    __tablename__ = "fields"
    id: Mapped[uuid.UUID] = _uuid_pk()
    extraction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = _tenant_fk()
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    line_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    calibrated_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    grounded: Mapped[bool] = _bool_false()
    boxes: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    stability: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = _created_at()

    extraction: Mapped[Extraction] = relationship(back_populates="fields")
    alternatives: Mapped[list[Alternative]] = relationship(
        back_populates="field", cascade="all, delete-orphan", order_by="Alternative.rank"
    )


class Alternative(Base):
    __tablename__ = "alternatives"
    id: Mapped[uuid.UUID] = _uuid_pk()
    field_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    probability: Mapped[float] = mapped_column(Float, nullable=False)

    field: Mapped[Field] = relationship(back_populates="alternatives")


class VerifierResult(Base):
    __tablename__ = "verifier_results"
    id: Mapped[uuid.UUID] = _uuid_pk()
    extraction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("fields.id", ondelete="CASCADE"), nullable=True
    )
    rule: Mapped[str] = mapped_column(String(64), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    detail: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    extraction: Mapped[Extraction] = relationship(back_populates="verifier_results")


class Verdict(Base):
    __tablename__ = "verdicts"
    id: Mapped[uuid.UUID] = _uuid_pk()
    extraction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    decision: Mapped[str] = mapped_column(String(24), nullable=False)
    reasons: Mapped[list[Any]] = _jsonb_array()
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = _created_at()

    extraction: Mapped[Extraction] = relationship(back_populates="verdict")


class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[uuid.UUID] = _uuid_pk()
    extraction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = _tenant_fk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = _created_at()


class Correction(Base):
    __tablename__ = "corrections"
    id: Mapped[uuid.UUID] = _uuid_pk()
    field_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = _tenant_fk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    region: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = _created_at()


# --- modeling -----------------------------------------------------------------------------


class ModelKind(enum.StrEnum):
    extractor = "extractor"
    ocr = "ocr"
    calibrator = "calibrator"
    threshold = "threshold"
    difficulty = "difficulty"
    baseline = "baseline"


class Dataset(Base):
    __tablename__ = "datasets"
    id: Mapped[uuid.UUID] = _uuid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    sources: Mapped[list[Any]] = _jsonb_array()
    split_policy: Mapped[dict[str, Any]] = _jsonb_object()
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = _created_at()


class DatasetItem(Base):
    __tablename__ = "dataset_items"
    id: Mapped[uuid.UUID] = _uuid_pk()
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    external_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    split: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    licence: Mapped[str] = mapped_column(String(64), nullable=False)
    labels: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    kind: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    queue: Mapped[str] = _str_default(16, "cpu")
    status: Mapped[str] = _str_default(16, "queued", index=True)
    attempts: Mapped[int] = _int_zero()
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    logs_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = _created_at()
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ModelVersion(Base):
    __tablename__ = "model_versions"
    __table_args__ = (
        Index(
            "uq_model_versions_one_pinned_per_kind",
            "kind",
            unique=True,
            postgresql_where=text("pinned"),
        ),
    )
    id: Mapped[uuid.UUID] = _uuid_pk()
    kind: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True
    )
    artifact_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    card_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    config: Mapped[dict[str, Any]] = _jsonb_object()
    metrics: Mapped[dict[str, Any]] = _jsonb_object()
    pinned: Mapped[bool] = _bool_false()
    pinned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pinned_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = _created_at()


class EvalReport(Base):
    __tablename__ = "eval_reports"
    id: Mapped[uuid.UUID] = _uuid_pk()
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[dict[str, Any]] = _jsonb_object()
    created_at: Mapped[datetime] = _created_at()


class EvalScore(Base):
    __tablename__ = "eval_scores"
    id: Mapped[uuid.UUID] = _uuid_pk()
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True
    )
    split: Mapped[str] = mapped_column(String(16), nullable=False)
    metric: Mapped[str] = mapped_column(String(48), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    support: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Signal(Base):
    __tablename__ = "signals"
    id: Mapped[uuid.UUID] = _uuid_pk()
    kind: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    scope: Mapped[str | None] = mapped_column(String(200), nullable=True)
    evidence: Mapped[dict[str, Any]] = _jsonb_object()
    intent_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = _str_default(16, "open", index=True)
    created_at: Mapped[datetime] = _created_at()


# --- billing ------------------------------------------------------------------------------


class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[uuid.UUID] = _uuid_pk()
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    monthly_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    included_documents: Mapped[int] = mapped_column(Integer, nullable=False)
    per_document_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    features: Mapped[list[Any]] = _jsonb_array()
    provider_price_id: Mapped[str | None] = mapped_column(String(128), nullable=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False
    )
    provider: Mapped[str] = _str_default(16, "fake")
    provider_customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_subscription_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = _str_default(24, "active")
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = _created_at()
