from sqlalchemy import text

from .db import engine


def run_lightweight_migrations():
    # Local/dev safety: add new columns without external migration tooling.
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                ALTER TABLE IF EXISTS audio_jobs
                ADD COLUMN IF NOT EXISTS voice_mode VARCHAR(16) DEFAULT 'my_voice'
                """
            )
        )
        conn.execute(
            text(
                """
                ALTER TABLE IF EXISTS audio_jobs
                ADD COLUMN IF NOT EXISTS preset_voice_id VARCHAR(64)
                """
            )
        )
        conn.execute(
            text(
                """
                ALTER TABLE IF EXISTS audio_jobs
                ADD COLUMN IF NOT EXISTS duration_sec INTEGER DEFAULT 30
                """
            )
        )
        conn.execute(
            text(
                """
                ALTER TABLE IF EXISTS audio_jobs
                ADD COLUMN IF NOT EXISTS purchase_id VARCHAR(36)
                """
            )
        )
