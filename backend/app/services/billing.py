from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from .. import models

DEMO_DURATION_SEC = 30
PAID_PACKAGES_RUB = {
    120: 190,
    180: 290,
    240: 390,
    300: 450,
}
MAX_TEXT_CHARS = 24000

TRAINING_INDIVIDUAL_CODE = "individual"
TRAINING_PLANS = [
    {
        "code": TRAINING_INDIVIDUAL_CODE,
        "title": "Individual access",
        "max_seats": 1,
        "price_rub": 2990,
    },
    {
        "code": "team_5",
        "title": "Company up to 5 seats",
        "max_seats": 5,
        "price_rub": 10000,
    },
    {
        "code": "team_10",
        "title": "Company up to 10 seats",
        "max_seats": 10,
        "price_rub": 20000,
    },
    {
        "code": "team_50",
        "title": "Company up to 50 seats",
        "max_seats": 50,
        "price_rub": 30000,
    },
    {
        "code": "team_100",
        "title": "Company up to 100 seats",
        "max_seats": 100,
        "price_rub": 50000,
    },
]


def _individual_training_plan() -> dict:
    for plan in TRAINING_PLANS:
        if plan["code"] == TRAINING_INDIVIDUAL_CODE:
            return plan
    raise RuntimeError("Individual training plan is not configured")


def ensure_user_exists(db: Session, user_id: str) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user
    email = f"{user_id}@local.dev"
    user = models.User(id=user_id, email=email, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def duration_label(duration_sec: int) -> str:
    if duration_sec == DEMO_DURATION_SEC:
        return "30 sec demo"
    return f"{duration_sec // 60} min"


def list_billing_packages() -> list[dict]:
    items = [
        {
            "code": "demo_30s",
            "duration_sec": DEMO_DURATION_SEC,
            "duration_label": "30 sec demo",
            "price_rub": 0,
            "is_demo": True,
        }
    ]
    for seconds, price in sorted(PAID_PACKAGES_RUB.items()):
        items.append(
            {
                "code": f"pack_{seconds}",
                "duration_sec": seconds,
                "duration_label": duration_label(seconds),
                "price_rub": price,
                "is_demo": False,
            }
        )
    return items


def is_allowed_duration(duration_sec: int) -> bool:
    return duration_sec == DEMO_DURATION_SEC or duration_sec in PAID_PACKAGES_RUB


def price_for_duration(duration_sec: int) -> int:
    if duration_sec == DEMO_DURATION_SEC:
        return 0
    return PAID_PACKAGES_RUB.get(duration_sec, 0)


def create_purchase(
    db: Session,
    user_id: str,
    duration_sec: int,
    status: str,
    provider: str,
    provider_payment_id: Optional[str] = None,
) -> models.Purchase:
    ensure_user_exists(db, user_id)
    purchase = models.Purchase(
        user_id=user_id,
        duration_sec=duration_sec,
        price_rub=price_for_duration(duration_sec),
        status=status,
        provider=provider,
        provider_payment_id=provider_payment_id,
        consumed=False,
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


def list_user_purchases(db: Session, user_id: str) -> list[models.Purchase]:
    ensure_user_exists(db, user_id)
    return (
        db.query(models.Purchase)
        .filter(models.Purchase.user_id == user_id)
        .order_by(models.Purchase.created_at.desc())
        .all()
    )


def _find_valid_purchase(
    db: Session,
    user_id: str,
    duration_sec: int,
    purchase_id: Optional[str],
) -> Optional[models.Purchase]:
    q = db.query(models.Purchase).filter(models.Purchase.user_id == user_id)
    q = q.filter(models.Purchase.duration_sec == duration_sec)
    q = q.filter(models.Purchase.status == "paid")
    q = q.filter(models.Purchase.consumed == False)

    if purchase_id:
        return q.filter(models.Purchase.id == purchase_id).first()

    return q.order_by(models.Purchase.created_at.desc()).first()


def validate_generation_access(
    db: Session,
    user_id: str,
    duration_sec: int,
    purchase_id: Optional[str],
    text_len: int,
) -> tuple[bool, str, Optional[models.Purchase]]:
    ensure_user_exists(db, user_id)

    if text_len > MAX_TEXT_CHARS:
        return False, "Text is too long", None

    if not is_allowed_duration(duration_sec):
        return False, "Unsupported duration", None

    if duration_sec == DEMO_DURATION_SEC:
        return True, "", None

    purchase = _find_valid_purchase(db, user_id, duration_sec, purchase_id)
    if not purchase:
        return False, "Payment required for selected duration", None
    return True, "", purchase


def consume_purchase(db: Session, purchase: models.Purchase):
    purchase.consumed = True
    purchase.consumed_at = datetime.utcnow()
    db.commit()


def list_training_plans() -> list[dict]:
    return [dict(x) for x in TRAINING_PLANS]


def get_training_plan_by_code(plan_code: str) -> Optional[dict]:
    for plan in TRAINING_PLANS:
        if plan["code"] == plan_code:
            return plan
    return None


def get_training_plan_for_seats(seats: int) -> dict:
    if seats <= 1:
        return _individual_training_plan()
    for plan in TRAINING_PLANS:
        if plan["code"] == TRAINING_INDIVIDUAL_CODE:
            continue
        if seats <= plan["max_seats"]:
            return plan
    return TRAINING_PLANS[-1]


def normalize_training_selection(plan_code: str, seats: int) -> tuple[dict, int]:
    normalized_seats = max(1, seats)
    if plan_code == TRAINING_INDIVIDUAL_CODE:
        return _individual_training_plan(), 1
    auto_plan = get_training_plan_for_seats(normalized_seats)
    if auto_plan["code"] == TRAINING_INDIVIDUAL_CODE:
        auto_plan = get_training_plan_by_code("team_5") or TRAINING_PLANS[1]
    requested = get_training_plan_by_code(plan_code)
    if requested and requested["code"] != TRAINING_INDIVIDUAL_CODE and normalized_seats <= requested["max_seats"]:
        return requested, normalized_seats
    return auto_plan, normalized_seats


def create_training_order(
    db: Session,
    user_id: str,
    plan_code: str,
    seats: int,
    company_name: Optional[str],
    status: str,
    provider: str,
    provider_payment_id: Optional[str] = None,
) -> models.TrainingOrder:
    ensure_user_exists(db, user_id)
    plan, normalized_seats = normalize_training_selection(plan_code, seats)
    order = models.TrainingOrder(
        user_id=user_id,
        plan_code=plan["code"],
        seats=normalized_seats,
        company_name=(company_name or "").strip() or None,
        price_rub=plan["price_rub"],
        status=status,
        provider=provider,
        provider_payment_id=provider_payment_id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def list_training_orders(db: Session, user_id: str) -> list[models.TrainingOrder]:
    ensure_user_exists(db, user_id)
    return (
        db.query(models.TrainingOrder)
        .filter(models.TrainingOrder.user_id == user_id)
        .order_by(models.TrainingOrder.created_at.desc())
        .all()
    )


def mark_training_order_paid(db: Session, provider_payment_id: str) -> Optional[models.TrainingOrder]:
    order = (
        db.query(models.TrainingOrder)
        .filter(models.TrainingOrder.provider_payment_id == provider_payment_id)
        .first()
    )
    if not order:
        return None
    order.status = "paid"
    order.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order
