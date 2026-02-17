import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import LessonCoachRequest, LessonCoachResponse, LessonHelpRequest, LessonHelpResponse, ScreenshotReviewResponse
from ..services.billing import MAX_TEXT_CHARS, ensure_user_exists
from ..services.coach import generate_lesson_coach, generate_lesson_help
from ..services.screenshot_review import review_screenshot
from ..utils.files import read_upload_file

router = APIRouter(prefix="/coach", tags=["coach"])
FAKE_USER_ID = "demo-user"


@router.post("/next-step", response_model=LessonCoachResponse)
def next_step(payload: LessonCoachRequest, db: Session = Depends(get_db)):
    ensure_user_exists(db, FAKE_USER_ID)
    if len(payload.practice_note or "") > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail="Practice note is too long")
    return generate_lesson_coach(payload)


@router.post("/help", response_model=LessonHelpResponse)
def help_chat(payload: LessonHelpRequest, db: Session = Depends(get_db)):
    ensure_user_exists(db, FAKE_USER_ID)
    if len(payload.user_question or "") < 3:
        raise HTTPException(status_code=400, detail="Question is too short")
    return generate_lesson_help(payload)


@router.post("/verify-screenshot", response_model=ScreenshotReviewResponse)
def verify_screenshot(
    language: str = Form("ru"),
    module_title: str = Form(""),
    mission_title: str = Form(""),
    learner_note: str = Form(""),
    required_checks: str = Form("[]"),
    screenshot: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ensure_user_exists(db, FAKE_USER_ID)
    data = read_upload_file(screenshot)
    if len(data or b"") == 0:
        raise HTTPException(status_code=400, detail="Uploaded screenshot is empty")

    try:
        parsed_checks = json.loads(required_checks) if required_checks else []
        checks = [str(item) for item in parsed_checks] if isinstance(parsed_checks, list) else []
    except Exception:
        checks = []

    try:
        return review_screenshot(
            language=language,
            module_title=module_title,
            mission_title=mission_title,
            learner_note=learner_note,
            required_checks=checks,
            image_bytes=data,
            content_type=screenshot.content_type or "image/png",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
