from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class GoalAnswer(BaseModel):
    area: str
    key: Optional[str] = None
    prompt: Optional[str] = None
    answer: str


class GenerateAffirmationsRequest(BaseModel):
    language: str = "ru"
    tone: str = "calm"
    goals: List[GoalAnswer]


class GenerateAffirmationsResponse(BaseModel):
    affirmations: List[str]


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    language: str = "ru"


class ProjectOut(BaseModel):
    id: str
    title: str
    language: str


class VoiceSampleOut(BaseModel):
    id: str
    s3_key: str
    consent: bool


class JobCreate(BaseModel):
    project_id: str
    affirmation_text: str = Field(min_length=5)
    music_track_id: str = "calm-1"
    duration_sec: int = 30
    voice_mode: str = "my_voice"
    preset_voice_id: Optional[str] = None
    purchase_id: Optional[str] = None


class JobOut(BaseModel):
    id: str
    status: str
    result_url: Optional[str] = None
    error: Optional[str] = None


class BillingPackageOut(BaseModel):
    code: str
    duration_sec: int
    duration_label: str
    price_rub: int
    is_demo: bool = False


class PurchaseCreate(BaseModel):
    duration_sec: int
    success_url: str = "http://localhost:3000/billing/success"
    cancel_url: str = "http://localhost:3000/billing/cancel"


class PurchaseOut(BaseModel):
    id: str
    duration_sec: int
    price_rub: int
    status: str
    consumed: bool
    checkout_url: Optional[str] = None
