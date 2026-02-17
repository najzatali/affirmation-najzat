from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import stripe

from .. import models
from ..core.config import settings
from ..db import get_db

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    if not settings.stripe_secret_key or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook is not configured")

    stripe.api_key = settings.stripe_secret_key
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.stripe_webhook_secret,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {exc}")

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
