from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..services.billing import ensure_user_exists
from ..storage.s3 import ensure_bucket, upload_bytes
from ..utils.consent import require_consent
from ..utils.files import read_upload_file

router = APIRouter(prefix="/voice-samples", tags=["voice"])
FAKE_USER_ID = "demo-user"

ALLOWED_CONTENT_TYPES = {
    "audio/webm",
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "video/webm",  # browser recorder may send this mime type with audio track.
}


@router.post("", response_model=schemas.VoiceSampleOut)
def upload_voice_sample(
    consent: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ensure_user_exists(db, FAKE_USER_ID)
    require_consent(consent)

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    data = read_upload_file(file)
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Voice sample is too large")

    ensure_bucket()
    ext = os.path.splitext(file.filename or "")[1] or ".webm"
    key = f"voice-samples/{FAKE_USER_ID}/{uuid.uuid4()}{ext.lower()}"
    upload_bytes(key, data, content_type=file.content_type or "audio/webm")

    sample = models.VoiceSample(user_id=FAKE_USER_ID, s3_key=key, consent=consent)
    db.add(sample)
    db.commit()
    db.refresh(sample)

    return schemas.VoiceSampleOut(id=sample.id, s3_key=sample.s3_key, consent=sample.consent)


@router.get("/latest", response_model=schemas.VoiceSampleOut | None)
def latest_voice_sample(db: Session = Depends(get_db)):
    ensure_user_exists(db, FAKE_USER_ID)
    sample = (
        db.query(models.VoiceSample)
        .filter(models.VoiceSample.user_id == FAKE_USER_ID)
        .order_by(models.VoiceSample.created_at.desc())
        .first()
    )
    if not sample:
        return None

    return schemas.VoiceSampleOut(id=sample.id, s3_key=sample.s3_key, consent=sample.consent)
