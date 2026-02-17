from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import GenerateAffirmationsRequest, GenerateAffirmationsResponse
from ..services.affirmations import generate_affirmations
from ..services.billing import MAX_TEXT_CHARS, ensure_user_exists

router = APIRouter(prefix="/affirmations", tags=["affirmations"])
FAKE_USER_ID = "demo-user"


@router.post("/generate", response_model=GenerateAffirmationsResponse)
def generate(payload: GenerateAffirmationsRequest, db: Session = Depends(get_db)):
    ensure_user_exists(db, FAKE_USER_ID)

    if payload.language not in {"ru", "en"}:
        raise HTTPException(status_code=400, detail="Unsupported language")

    if not payload.goals:
        raise HTTPException(status_code=400, detail="At least one answer is required")

    total_chars = sum(len((item.answer or "").strip()) for item in payload.goals)
    if total_chars == 0:
        raise HTTPException(status_code=400, detail="Answers cannot be empty")

    if total_chars > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail="Input text is too long")

    items = generate_affirmations(payload.goals, payload.language, payload.tone, payload.user_name or "")
    if not items:
        raise HTTPException(status_code=500, detail="Failed to generate affirmations")

    return GenerateAffirmationsResponse(affirmations=items)
