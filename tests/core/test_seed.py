"""`make seed` creates the demo tenant, two users, plans and pinned stubs — idempotently."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select

pytestmark = pytest.mark.db


def test_seed_is_idempotent_and_creates_demo_accounts(db_session) -> None:  # type: ignore[no-untyped-def]
    from ledgerlens_core.models import Membership, ModelVersion, Plan, Tenant, User
    from ledgerlens_core.seed import DEMO_PASSWORD, DEMO_USERS, seed

    seed(db_session)
    seed(db_session)

    assert db_session.scalar(select(func.count()).select_from(Tenant)) == 1
    assert db_session.scalar(select(func.count()).select_from(User)) == len(DEMO_USERS)
    assert db_session.scalar(select(func.count()).select_from(Plan)) == 3
    pinned_kinds = set(
        db_session.scalars(select(ModelVersion.kind).where(ModelVersion.pinned.is_(True)))
    )
    assert pinned_kinds == {"extractor", "ocr", "calibrator", "threshold"}

    roles = dict(db_session.execute(select(User.email, Membership.role).join(Membership)).all())
    assert roles["lead@ledgerlens.demo"] == "finance_lead"
    assert roles["clerk@ledgerlens.demo"] == "clerk"
    assert len(DEMO_PASSWORD) >= 12
