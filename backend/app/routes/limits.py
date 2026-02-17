from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.billing import DEMO_DURATION_SEC, list_billing_packages, list_user_purchases

router = APIRouter(prefix="/limits", tags=["limits"])
FAKE_USER_ID = "demo-user"


@router.get("")
def get_limits(db: Session = Depends(get_db)):
    purchases = list_user_purchases(db, FAKE_USER_ID)
    paid_unused = len([p for p in purchases if p.status == "paid" and not p.consumed])
    return {
        "demo_duration_sec": DEMO_DURATION_SEC,
        "packages": list_billing_packages(),
        "paid_unused_purchases": paid_unused,
    }
