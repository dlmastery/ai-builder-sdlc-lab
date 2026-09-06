"""Signals written by the maintain job, and their intents."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_api.deps import Principal, current_principal, get_db, require_csrf
from ledgerlens_api.schemas import Paginated
from ledgerlens_core.models import Signal

router = APIRouter(tags=["signals"])


class SignalOut(BaseModel):
    id: UUID
    kind: str
    scope: str | None
    evidence: dict[str, Any]
    intent_path: str | None
    status: str
    created_at: datetime


def _out(s: Signal) -> SignalOut:
    return SignalOut(
        id=s.id,
        kind=s.kind,
        scope=s.scope,
        evidence=s.evidence,
        intent_path=s.intent_path,
        status=s.status,
        created_at=s.created_at,
    )


@router.get("/signals", response_model=Paginated[SignalOut])
def list_signals(
    principal: Principal = Depends(current_principal), db: DbSession = Depends(get_db)
) -> Paginated[SignalOut]:
    rows = db.scalars(select(Signal).order_by(Signal.created_at.desc())).all()
    return Paginated(items=[_out(s) for s in rows], total=len(rows))


@router.post("/signals/{signal_id}/triage", response_model=SignalOut)
def triage(
    signal_id: UUID,
    principal: Principal = Depends(require_csrf),
    db: DbSession = Depends(get_db),
) -> SignalOut:
    """A human read the intent and took it into the loop; the signal stops being 'open'."""
    s = db.get(Signal, signal_id)
    if s is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "signal not found")
    s.status = "triaged"
    db.flush()
    return _out(s)
