import hashlib
import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import stripe

from .. import schemas
from ..core.config import settings
from ..db import get_db
from ..services.billing import (
    DEMO_DURATION_SEC,
    create_purchase,
    create_training_order,
    is_allowed_duration,
    list_billing_packages,
    list_training_orders,
    list_training_plans,
    list_user_purchases,
    normalize_training_selection,
    price_for_duration,
)

router = APIRouter(prefix="/billing", tags=["billing"])
FAKE_USER_ID = "demo-user"


def _format_robokassa_sum(amount_rub: int) -> str:
    return f"{float(amount_rub):.2f}"


def _robokassa_payment_signature(login: str, out_sum: str, inv_id: str, password_1: str) -> str:
    raw = f"{login}:{out_sum}:{inv_id}:{password_1}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


@router.get("/packages", response_model=list[schemas.BillingPackageOut])
def get_packages():
    return [schemas.BillingPackageOut(**x) for x in list_billing_packages()]


@router.get("/plans", response_model=list[schemas.BillingPackageOut])
def legacy_plans_alias():
    return [schemas.BillingPackageOut(**x) for x in list_billing_packages()]


@router.get("/purchases", response_model=list[schemas.PurchaseOut])
def get_purchases(db: Session = Depends(get_db)):
    items = list_user_purchases(db, FAKE_USER_ID)
    return [
        schemas.PurchaseOut(
            id=i.id,
            duration_sec=i.duration_sec,
            price_rub=i.price_rub,
            status=i.status,
            consumed=bool(i.consumed),
            checkout_url=None,
        )
        for i in items
    ]


@router.post("/purchases", response_model=schemas.PurchaseOut)
def create_billing_purchase(payload: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    if not is_allowed_duration(payload.duration_sec):
        raise HTTPException(status_code=400, detail="Unsupported duration")

    if payload.duration_sec == DEMO_DURATION_SEC:
        return schemas.PurchaseOut(
            id="demo",
            duration_sec=DEMO_DURATION_SEC,
            price_rub=0,
            status="demo",
            consumed=False,
            checkout_url=payload.success_url,
        )

    if settings.billing_provider != "stripe":
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

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    amount_rub = price_for_duration(payload.duration_sec)
    if amount_rub <= 0:
        raise HTTPException(status_code=400, detail="Invalid duration/price")

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


@router.get("/training-plans", response_model=list[schemas.TrainingPlanOut])
def get_training_plans():
    return [schemas.TrainingPlanOut(**x) for x in list_training_plans()]


@router.get("/training-orders", response_model=list[schemas.TrainingOrderOut])
def get_training_orders(db: Session = Depends(get_db)):
    items = list_training_orders(db, FAKE_USER_ID)
    return [
        schemas.TrainingOrderOut(
            id=i.id,
            plan_code=i.plan_code,
            seats=i.seats,
            company_name=i.company_name,
            price_rub=i.price_rub,
            status=i.status,
            checkout_url=None,
        )
        for i in items
    ]


@router.post("/training-orders", response_model=schemas.TrainingOrderOut)
def create_training_checkout(payload: schemas.TrainingOrderCreate, db: Session = Depends(get_db)):
    plan, seats = normalize_training_selection(payload.plan_code, payload.seats)

    if settings.billing_provider == "local":
        order = create_training_order(
            db,
            user_id=FAKE_USER_ID,
            plan_code=plan["code"],
            seats=seats,
            company_name=payload.company_name,
            status="paid",
            provider="local",
        )
        return schemas.TrainingOrderOut(
            id=order.id,
            plan_code=order.plan_code,
            seats=order.seats,
            company_name=order.company_name,
            price_rub=order.price_rub,
            status=order.status,
            checkout_url=payload.success_url,
        )

    if settings.billing_provider != "robokassa":
        raise HTTPException(status_code=400, detail="Unsupported billing provider for training checkout")

    if not settings.robokassa_login or not settings.robokassa_password_1:
        raise HTTPException(status_code=500, detail="Robokassa is not configured")

    inv_id = str(uuid.uuid4().int % 10_000_000_000)

    order = create_training_order(
        db,
        user_id=FAKE_USER_ID,
        plan_code=plan["code"],
        seats=seats,
        company_name=payload.company_name,
        status="pending",
        provider="robokassa",
        provider_payment_id=inv_id,
    )

    out_sum = _format_robokassa_sum(order.price_rub)
    signature = _robokassa_payment_signature(
        login=settings.robokassa_login,
        out_sum=out_sum,
        inv_id=inv_id,
        password_1=settings.robokassa_password_1,
    )

    description = f"AIMPACT training: {order.plan_code}"
    query = {
        "MerchantLogin": settings.robokassa_login,
        "OutSum": out_sum,
        "InvId": inv_id,
        "Description": description,
        "SignatureValue": signature,
        "Culture": "ru",
    }
    if settings.robokassa_test_mode:
        query["IsTest"] = "1"

    checkout_url = f"{settings.robokassa_checkout_url}?{urlencode(query)}"

    return schemas.TrainingOrderOut(
        id=order.id,
        plan_code=order.plan_code,
        seats=order.seats,
        company_name=order.company_name,
        price_rub=order.price_rub,
        status=order.status,
        checkout_url=checkout_url,
    )
