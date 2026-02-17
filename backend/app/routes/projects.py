from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..services.billing import ensure_user_exists

router = APIRouter(prefix="/projects", tags=["projects"])

# NOTE: auth is stubbed. Replace user_id with real auth.
FAKE_USER_ID = "demo-user"

@router.post("", response_model=schemas.ProjectOut)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    ensure_user_exists(db, FAKE_USER_ID)
    project = models.Project(user_id=FAKE_USER_ID, title=payload.title, language=payload.language)
    db.add(project)
    db.commit()
    db.refresh(project)
    return schemas.ProjectOut(id=project.id, title=project.title, language=project.language)

@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    items = db.query(models.Project).filter(models.Project.user_id == FAKE_USER_ID).all()
    return [schemas.ProjectOut(id=i.id, title=i.title, language=i.language) for i in items]
