from fastapi import HTTPException
from ..core.config import settings


def require_consent(consent: bool):
    if settings.require_consent and not consent:
        raise HTTPException(status_code=400, detail="Consent required to process voice data")
