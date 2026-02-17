from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import stripe

from .. import schemas
from ..core.config import settings
from ..db import get_db
from ..services.billing import (
    DEMO_DURATION_SEC,
    create_purchase,
    is_allowed_duration,
    list_billing_packages,
    list_user_purchases,
    price_for_duration,
)

router = APIRouter(prefix="/billing", tags=["billing"])
FAKE_USER_ID = "demo-user"


@router.get("/packages", response_model=list[schemas.BillingPackageOut])
def get_packages():
    return [schemas.BillingPackageOut(**item) for item in list_billing_packages()]


@router.get("/plans", response_model=list[schemas.BillingPackageOut])
def legacy_plans_alias():
    return [schemas.BillingPackageOut(**item) for item in list_billing_packages()]


@router.get("/purchases", response_model=list[schemas.PurchaseOut])
def get_purchases(db: Session = Depends(get_db)):
    items = list_user_purchases(db, FAKE_USER_ID)
    return [
        schemas.PurchaseOut(
            id=item.id,
            duration_sec=item.duration_sec,
            price_rub=item.price_rub,
            status=item.status,
            consumed=bool(item.consumed),
            checkout_url=None,
        )
        for item in items
    ]


@router.post("/purchases", response_model=schemas.PurchaseOut)
def create_billing_purchase(payload: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    if not is_allowed_duration(payload.duration_sec):
        raise HTTPException(status_code=400, detail="Unsupported duration")

    # Demo always доступен бесплатно.
    if payload.duration_sec == DEMO_DURATION_SEC:
        return schemas.PurchaseOut(
            id="demo",
            duration_sec=DEMO_DURATION_SEC,
            price_rub=0,
            status="demo",
            consumed=False,
            checkout_url=payload.success_url,
        )

    # Local mode: сразу выдаем оплаченный пакет для MVP без реального платежа.
    if settings.billing_provider == "local":
        purchase = create_purchase(
            db,
            user_id=FAKE_USER_ID,
            duration_sec=payload.duration_sec,
            status="paid",
            provider="local",
        )
        return schemas.PurchaseOut(
            id=purchase.id,
            duration_sec=purchase.duration_sec,
            price_rub=purchase.price_rub,
            status=purchase.status,
            consumed=bool(purchase.consumed),
            checkout_url=payload.success_url,
        )

    if settings.billing_provider != "stripe":
        raise HTTPException(status_code=400, detail="Unsupported billing provider")

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    amount_rub = price_for_duration(payload.duration_sec)
    if amount_rub <= 0:
        raise HTTPException(status_code=400, detail="Invalid duration or price")

    stripe.api_key = settings.stripe_secret_key
    session = stripe.checkout.Session.create(
        mode="payment",
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": "rub",
                    "unit_amount": amount_rub * 100,
                    "product_data": {
                        "name": f"Affirmation audio {payload.duration_sec // 60} min",
                    },
                },
            }
        ],
        metadata={
            "user_id": FAKE_USER_ID,
            "duration_sec": str(payload.duration_sec),
        },
    )

    purchase = create_purchase(
        db,
        user_id=FAKE_USER_ID,
        duration_sec=payload.duration_sec,
        status="pending",
        provider="stripe",
        provider_payment_id=session.id,
    )

    return schemas.PurchaseOut(
        id=purchase.id,
        duration_sec=purchase.duration_sec,
        price_rub=purchase.price_rub,
        status=purchase.status,
        consumed=bool(purchase.consumed),
        checkout_url=session.url,
    )
