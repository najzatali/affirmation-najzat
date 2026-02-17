from __future__ import annotations

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


def ensure_user_exists(db: Session, user_id: str) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user

    user = models.User(id=user_id, email=f"{user_id}@local.dev", is_active=True)
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
            "duration_label": duration_label(DEMO_DURATION_SEC),
            "price_rub": 0,
            "is_demo": True,
        }
    ]
    for duration_sec, price_rub in sorted(PAID_PACKAGES_RUB.items()):
        items.append(
            {
                "code": f"pack_{duration_sec}",
                "duration_sec": duration_sec,
                "duration_label": duration_label(duration_sec),
                "price_rub": price_rub,
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
    query = db.query(models.Purchase).filter(models.Purchase.user_id == user_id)
    query = query.filter(models.Purchase.duration_sec == duration_sec)
    query = query.filter(models.Purchase.status == "paid")
    query = query.filter(models.Purchase.consumed == False)

    if purchase_id:
        return query.filter(models.Purchase.id == purchase_id).first()

    return query.order_by(models.Purchase.created_at.desc()).first()


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

    purchase = _find_valid_purchase(db, user_id=user_id, duration_sec=duration_sec, purchase_id=purchase_id)
    if not purchase:
        return False, "Payment required for selected duration", None

    return True, "", purchase


def consume_purchase(db: Session, purchase: models.Purchase):
    purchase.consumed = True
    purchase.consumed_at = datetime.utcnow()
    db.commit()
