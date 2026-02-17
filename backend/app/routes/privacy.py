from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..core.config import settings
from ..db import get_db
from ..storage.s3 import delete_key

router = APIRouter(prefix="/privacy", tags=["privacy"])
FAKE_USER_ID = "demo-user"


@router.delete("/voice")
def delete_voice_samples(db: Session = Depends(get_db)):
    items = db.query(models.VoiceSample).filter(models.VoiceSample.user_id == FAKE_USER_ID).all()
    deleted = 0
    for item in items:
        if item.s3_key:
            delete_key(item.s3_key)
        db.delete(item)
        deleted += 1
    db.commit()
    return {"deleted": deleted}


@router.delete("/audio")
def delete_audio_results(db: Session = Depends(get_db)):
    jobs = db.query(models.AudioJob).all()
    deleted = 0
    for job in jobs:
        if job.result_s3_key:
            delete_key(job.result_s3_key)
            job.result_s3_key = None
            deleted += 1
    db.commit()
    return {"deleted": deleted}


@router.post("/cleanup")
def run_retention_cleanup(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(days=max(1, settings.voice_retention_days))

    voice_deleted = 0
    voice_items = db.query(models.VoiceSample).filter(models.VoiceSample.created_at < cutoff).all()
    for item in voice_items:
        if item.s3_key:
            delete_key(item.s3_key)
        db.delete(item)
        voice_deleted += 1

    result_deleted = 0
    old_jobs = db.query(models.AudioJob).filter(models.AudioJob.created_at < cutoff).all()
    for job in old_jobs:
        if job.result_s3_key:
            delete_key(job.result_s3_key)
            job.result_s3_key = None
            result_deleted += 1

    db.commit()
    return {
        "retention_days": settings.voice_retention_days,
        "voice_deleted": voice_deleted,
        "audio_deleted": result_deleted,
    }
