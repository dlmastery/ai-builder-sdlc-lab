"""Demo seed: one tenant, a finance lead and a clerk, plans, pinned stubs. Idempotent.

    uv run python -m ledgerlens_core.seed

Passwords are for the local demo only and are printed once so students can sign in.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_core.auth import hash_password
from ledgerlens_core.bootstrap import bootstrap
from ledgerlens_core.models import Membership, Tenant, User

DEMO_TENANT = {"name": "Meridian Instruments Ltd", "slug": "meridian"}
DEMO_PASSWORD = "show-your-work-2026"
DEMO_USERS: list[dict[str, str]] = [
    {"email": "lead@ledgerlens.demo", "display_name": "Ada Okafor", "role": "finance_lead"},
    {"email": "clerk@ledgerlens.demo", "display_name": "Sam Lindqvist", "role": "clerk"},
    {"email": "data@ledgerlens.demo", "display_name": "Priya Raman", "role": "data_lead"},
]


def seed(db: DbSession) -> Tenant:
    bootstrap(db)
    tenant = db.scalar(select(Tenant).where(Tenant.slug == DEMO_TENANT["slug"]))
    if tenant is None:
        tenant = Tenant(**DEMO_TENANT)
        db.add(tenant)
        db.flush()
    for spec in DEMO_USERS:
        user = db.scalar(select(User).where(User.email == spec["email"]))
        if user is None:
            user = User(
                email=spec["email"],
                display_name=spec["display_name"],
                password_hash=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
            db.flush()
        membership = db.scalar(
            select(Membership).where(
                Membership.user_id == user.id, Membership.tenant_id == tenant.id
            )
        )
        if membership is None:
            db.add(Membership(tenant_id=tenant.id, user_id=user.id, role=spec["role"]))
    db.flush()
    return tenant


def main() -> None:
    from ledgerlens_core.db import session_scope

    with session_scope() as db:
        tenant = seed(db)
    print(f"seeded tenant {tenant.name!r} ({tenant.slug})")
    for spec in DEMO_USERS:
        print(f"  {spec['email']}  role={spec['role']}  password={DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
