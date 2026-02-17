from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import GenerateAffirmationsRequest, GenerateAffirmationsResponse
from ..services.affirmations import generate_affirmations
from ..db import get_db
from ..services.billing import MAX_TEXT_CHARS, ensure_user_exists

router = APIRouter(prefix="/affirmations", tags=["affirmations"])
FAKE_USER_ID = "demo-user"

@router.post("/generate", response_model=GenerateAffirmationsResponse)
def generate(payload: GenerateAffirmationsRequest, db: Session = Depends(get_db)):
    ensure_user_exists(db, FAKE_USER_ID)
    total_chars = sum(len(g.answer) for g in payload.goals)
    if total_chars > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail="Input text is too long")
    items = generate_affirmations(payload.goals, payload.language, payload.tone)
    return GenerateAffirmationsResponse(affirmations=items)
