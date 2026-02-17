import hashlib

from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.responses import PlainTextResponse
import stripe

from ..core.config import settings
from ..db import get_db
from .. import models
from ..services.billing import mark_training_order_paid

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    if not settings.stripe_secret_key or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook is not configured")

    stripe.api_key = settings.stripe_secret_key
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=settings.stripe_webhook_secret
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook: {e}")

    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        session_id = data.get("id")
        purchase = db.query(models.Purchase).filter(models.Purchase.provider_payment_id == session_id).first()
        if purchase:
            purchase.status = "paid"
            purchase.consumed = False
            db.commit()

    if event_type == "checkout.session.expired":
        session_id = data.get("id")
        purchase = db.query(models.Purchase).filter(models.Purchase.provider_payment_id == session_id).first()
        if purchase and purchase.status != "paid":
            purchase.status = "expired"
            db.commit()

    return {"received": True, "event_type": event_type}


@router.api_route("/robokassa/result", methods=["GET", "POST"])
async def robokassa_result(request: Request, db: Session = Depends(get_db)):
    if not settings.robokassa_password_2:
        raise HTTPException(status_code=500, detail="Robokassa result endpoint is not configured")

    payload = dict(request.query_params)
    if request.method == "POST":
        form = await request.form()
        payload.update(dict(form))

    out_sum = str(payload.get("OutSum", "")).strip()
    inv_id = str(payload.get("InvId", "")).strip()
    signature_value = str(payload.get("SignatureValue", "")).strip()
    if not out_sum or not inv_id or not signature_value:
        raise HTTPException(status_code=400, detail="Missing Robokassa result fields")

    raw = f"{out_sum}:{inv_id}:{settings.robokassa_password_2}"
    expected = hashlib.md5(raw.encode("utf-8")).hexdigest().upper()
    if expected != signature_value.upper():
        raise HTTPException(status_code=400, detail="Invalid Robokassa signature")

    mark_training_order_paid(db, provider_payment_id=inv_id)

    return PlainTextResponse(f"OK{inv_id}")
