"""Pricing → checkout. Stripe in test mode when keys exist; otherwise FakeBilling, which completes
immediately and is labelled as such everywhere (spec §2 · Pricing)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_api.deps import Principal, current_principal, get_db, require_csrf
from ledgerlens_api.schemas import PlanOut
from ledgerlens_core.models import Plan, Subscription
from ledgerlens_core.settings import get_settings

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: str
    success_url: str | None = None
    cancel_url: str | None = None


class CheckoutOut(BaseModel):
    provider: str
    checkout_url: str


class SubscriptionOut(BaseModel):
    plan: PlanOut
    provider: str
    status: str
    current_period_end: datetime | None


def _plan_out(p: Plan) -> PlanOut:
    return PlanOut(
        code=p.code,
        name=p.name,
        monthly_price_cents=p.monthly_price_cents,
        included_documents=p.included_documents,
        per_document_cents=p.per_document_cents,
        features=p.features,
    )


def _stripe_checkout(plan: Plan, body: CheckoutRequest, tenant_id: str) -> str:
    import stripe

    s = get_settings()
    assert s.stripe_secret_key is not None
    stripe.api_key = s.stripe_secret_key.get_secret_value()
    line: dict[str, Any] = (
        {"price": plan.provider_price_id, "quantity": 1}
        if plan.provider_price_id
        else {
            "price_data": {
                "currency": "usd",
                "unit_amount": plan.monthly_price_cents,
                "recurring": {"interval": "month"},
                "product_data": {"name": f"Ledgerlens {plan.name}"},
            },
            "quantity": 1,
        }
    )
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[line],
        success_url=body.success_url or "http://localhost:3000/production?billing=success",
        cancel_url=body.cancel_url or "http://localhost:3000/pricing?billing=cancelled",
        client_reference_id=tenant_id,
        metadata={"plan": plan.code, "tenant_id": tenant_id},
    )
    return str(session.url)


@router.post("/checkout", response_model=CheckoutOut)
def checkout(
    body: CheckoutRequest,
    principal: Principal = Depends(require_csrf),
    db: DbSession = Depends(get_db),
) -> CheckoutOut:
    plan = db.scalar(select(Plan).where(Plan.code == body.plan))
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "plan not found")
    provider = get_settings().billing_provider
    sub = db.scalar(select(Subscription).where(Subscription.tenant_id == principal.tenant_id))
    if provider == "stripe":
        url = _stripe_checkout(plan, body, str(principal.tenant_id))
        if sub is None:
            db.add(
                Subscription(
                    tenant_id=principal.tenant_id,
                    plan_id=plan.id,
                    provider="stripe",
                    status="pending",
                )
            )
        else:
            sub.plan_id, sub.provider, sub.status = plan.id, "stripe", "pending"
        db.flush()
        return CheckoutOut(provider="stripe", checkout_url=url)
    # FakeBilling: complete immediately, clearly labelled
    period_end = datetime.now(UTC) + timedelta(days=30)
    if sub is None:
        db.add(
            Subscription(
                tenant_id=principal.tenant_id,
                plan_id=plan.id,
                provider="fake",
                provider_customer_id=f"fake_cus_{principal.tenant.slug}",
                provider_subscription_id=f"fake_sub_{plan.code}",
                status="active",
                current_period_end=period_end,
            )
        )
    else:
        sub.plan_id, sub.provider, sub.status, sub.current_period_end = (
            plan.id,
            "fake",
            "active",
            period_end,
        )
    db.flush()
    return CheckoutOut(provider="fake", checkout_url=f"/billing/fake?plan={plan.code}")


@router.get("/subscription", response_model=SubscriptionOut | None)
def subscription(
    principal: Principal = Depends(current_principal), db: DbSession = Depends(get_db)
) -> SubscriptionOut | None:
    sub = db.scalar(select(Subscription).where(Subscription.tenant_id == principal.tenant_id))
    if sub is None:
        return None
    plan = db.get(Plan, sub.plan_id)
    assert plan is not None
    return SubscriptionOut(
        plan=_plan_out(plan),
        provider=sub.provider,
        status=sub.status,
        current_period_end=sub.current_period_end,
    )
