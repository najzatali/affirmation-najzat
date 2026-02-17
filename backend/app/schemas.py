from pydantic import BaseModel, Field
from typing import List, Optional


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
    title: str
    language: str = "ru"


class ProjectOut(BaseModel):
    id: str
    title: str
    language: str


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


class VoiceSampleOut(BaseModel):
    id: str
    s3_key: str
    consent: bool


class PlanOut(BaseModel):
    code: str
    price_month_usd: int
    max_generations: int
    max_text_chars: int


class SubscriptionOut(BaseModel):
    plan: str
    status: str
    provider: str


class CheckoutRequest(BaseModel):
    plan_code: str
    success_url: str = "http://localhost:3000/billing/success"
    cancel_url: str = "http://localhost:3000/billing/cancel"


class CheckoutOut(BaseModel):
    checkout_url: str


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


class TrainingPlanOut(BaseModel):
    code: str
    title: str
    max_seats: int
    price_rub: int


class TrainingOrderCreate(BaseModel):
    plan_code: str
    seats: int = 1
    company_name: Optional[str] = None
    success_url: str = "http://localhost:3000/billing/success"
    cancel_url: str = "http://localhost:3000/billing/cancel"


class TrainingOrderOut(BaseModel):
    id: str
    plan_code: str
    seats: int
    company_name: Optional[str] = None
    price_rub: int
    status: str
    checkout_url: Optional[str] = None


class CoachProfile(BaseModel):
    learner_type: str = "individual"
    age_group: str = "young"
    industry: str = "general"
    role: str = "specialist"
    level: str = "beginner"
    format: str = "hybrid"
    goals: List[str] = []


class LessonCoachRequest(BaseModel):
    language: str = "ru"
    module_id: str
    module_title: str
    module_summary: str = ""
    practice_note: str = ""
    completed_tasks: List[str] = []
    visited_segments: int = 0
    total_segments: int = 0
    profile: CoachProfile


class LessonCoachResponse(BaseModel):
    next_step: str
    checkpoint: str
    safety_note: str
    company_step: Optional[str] = None
    company_kpi: Optional[str] = None
    provider: str
    fallback: bool = False


class ScreenshotReviewResponse(BaseModel):
    passed: bool
    score: int
    summary: str
    found: List[str]
    missing: List[str]
    next_action: str
    provider: str
    fallback: bool = False


class LessonHelpRequest(BaseModel):
    language: str = "ru"
    module_title: str
    step_title: str = ""
    user_question: str
    user_attempt: str = ""
    profile: CoachProfile


class LessonHelpResponse(BaseModel):
    answer: str
    what_wrong: str
    how_fix: str
    provider: str
    fallback: bool = False
