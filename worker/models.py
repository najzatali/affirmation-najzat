import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from db import Base


def _uuid():
    return str(uuid.uuid4())


class AudioJob(Base):
    __tablename__ = "audio_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(String(36))
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
