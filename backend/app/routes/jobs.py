from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..services.billing import consume_purchase, ensure_user_exists, validate_generation_access
from ..storage.s3 import delete_key, download_bytes
from ..worker_client import enqueue_audio_job

router = APIRouter(prefix="/jobs", tags=["jobs"])
FAKE_USER_ID = "demo-user"


@router.post("", response_model=schemas.JobOut)
def create_job(payload: schemas.JobCreate, db: Session = Depends(get_db)):
    ensure_user_exists(db, FAKE_USER_ID)

    project = db.query(models.Project).filter(models.Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.voice_mode not in {"my_voice", "system_voice"}:
        raise HTTPException(status_code=400, detail="Unsupported voice mode")

    ok, reason, purchase = validate_generation_access(
        db,
        user_id=FAKE_USER_ID,
        duration_sec=payload.duration_sec,
        purchase_id=payload.purchase_id,
        text_len=len(payload.affirmation_text),
    )
    if not ok:
        raise HTTPException(status_code=402, detail=reason)

    job = models.AudioJob(
        project_id=payload.project_id,
        input_text=payload.affirmation_text,
        music_track_id=payload.music_track_id,
        duration_sec=payload.duration_sec,
        voice_mode=payload.voice_mode,
        preset_voice_id=payload.preset_voice_id,
        purchase_id=purchase.id if purchase else payload.purchase_id,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    if purchase:
        consume_purchase(db, purchase)

    enqueue_audio_job(job.id)
    return schemas.JobOut(id=job.id, status=job.status)


@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(models.AudioJob).filter(models.AudioJob.id == job_id).first()
    if not job:
        return schemas.JobOut(id=job_id, status="not_found")

    result_url = f"/api/jobs/{job.id}/result" if job.result_s3_key else None
    return schemas.JobOut(id=job.id, status=job.status, result_url=result_url, error=job.error)


@router.get("/{job_id}/result")
def download_job_result(
    job_id: str,
    delete_after_download: bool = Query(True),
    db: Session = Depends(get_db),
):
    job = db.query(models.AudioJob).filter(models.AudioJob.id == job_id).first()
    if not job or not job.result_s3_key:
        raise HTTPException(status_code=404, detail="Result file not found")

    data = download_bytes(job.result_s3_key)
    if not data:
        raise HTTPException(status_code=404, detail="Result file is empty")

    headers = {"Content-Disposition": f'attachment; filename="affirmation-{job.id}.mp3"'}
    response = Response(content=data, media_type="audio/mpeg", headers=headers)

    if delete_after_download:
        delete_key(job.result_s3_key)
        job.result_s3_key = None
        db.commit()

    return response
