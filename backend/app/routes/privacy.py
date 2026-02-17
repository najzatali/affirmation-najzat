from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models

router = APIRouter(prefix="/privacy", tags=["privacy"])

FAKE_USER_ID = "demo-user"

@router.delete("/voice")
def delete_voice_samples(db: Session = Depends(get_db)):
    items = db.query(models.VoiceSample).filter(models.VoiceSample.user_id == FAKE_USER_ID).all()
    for i in items:
        db.delete(i)
    db.commit()
    return {"deleted": len(items)}
