from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
from ..db import get_db
from .. import models, schemas
from ..storage.s3 import upload_bytes, ensure_bucket
from ..utils.files import read_upload_file
from ..utils.consent import require_consent
from ..services.billing import ensure_user_exists

router = APIRouter(prefix="/voice-samples", tags=["voice"])

FAKE_USER_ID = "demo-user"

@router.post("", response_model=schemas.VoiceSampleOut)
def upload_voice_sample(
    consent: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ensure_user_exists(db, FAKE_USER_ID)
    require_consent(consent)
    data = read_upload_file(file)
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    ensure_bucket()
    ext = os.path.splitext(file.filename or "")[1] or ".webm"
    safe_name = f"{uuid.uuid4()}{ext.lower()}"
    key = f"voice-samples/{FAKE_USER_ID}/{safe_name}"
    upload_bytes(key, data, content_type=file.content_type or "audio/wav")
    vs = models.VoiceSample(user_id=FAKE_USER_ID, s3_key=key, consent=consent)
    db.add(vs)
    db.commit()
    db.refresh(vs)
    return schemas.VoiceSampleOut(id=vs.id, s3_key=vs.s3_key, consent=vs.consent)
