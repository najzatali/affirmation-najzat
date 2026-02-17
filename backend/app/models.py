import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


def _uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    projects: Mapped[list["Project"]] = relationship(back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(8), default="ru")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="projects")
    affirmations: Mapped[list["Affirmation"]] = relationship(back_populates="project")


class Affirmation(Base):
    __tablename__ = "affirmations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    text: Mapped[str] = mapped_column(Text)
    tone: Mapped[str] = mapped_column(String(32), default="calm")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="affirmations")


class VoiceSample(Base):
    __tablename__ = "voice_samples"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    s3_key: Mapped[str] = mapped_column(String(255))
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AudioJob(Base):
    __tablename__ = "audio_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    input_text: Mapped[str] = mapped_column(Text)
    music_track_id: Mapped[str] = mapped_column(String(64))
    duration_sec: Mapped[int] = mapped_column(default=30)
    voice_mode: Mapped[str] = mapped_column(String(16), default="my_voice")
    preset_voice_id: Mapped[str] = mapped_column(String(64), nullable=True)
    purchase_id: Mapped[str] = mapped_column(String(36), nullable=True)
    result_s3_key: Mapped[str] = mapped_column(String(255), nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    plan_code: Mapped[str] = mapped_column(String(16), default="free")
    status: Mapped[str] = mapped_column(String(32), default="active")
    provider: Mapped[str] = mapped_column(String(16), default="local")
    provider_customer_id: Mapped[str] = mapped_column(String(128), nullable=True)
    provider_subscription_id: Mapped[str] = mapped_column(String(128), nullable=True)
    current_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    units: Mapped[int] = mapped_column(default=1)
    job_id: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    duration_sec: Mapped[int] = mapped_column()
    price_rub: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(32), default="paid")
    provider: Mapped[str] = mapped_column(String(16), default="local")
    provider_payment_id: Mapped[str] = mapped_column(String(128), nullable=True)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False)
    consumed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class TrainingOrder(Base):
    __tablename__ = "training_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    plan_code: Mapped[str] = mapped_column(String(32), index=True)
    seats: Mapped[int] = mapped_column(default=1)
    company_name: Mapped[str] = mapped_column(String(255), nullable=True)
    price_rub: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    provider: Mapped[str] = mapped_column(String(16), default="local")
    provider_payment_id: Mapped[str] = mapped_column(String(128), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
