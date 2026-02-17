from __future__ import annotations

import os
import subprocess
from datetime import datetime

from sqlalchemy.orm import Session

from audio_engine import mix_and_master_mp3
from config import settings
from db import SessionLocal
from models import AudioJob
from providers.tts import synthesize_with_fallback
from storage import upload_bytes


VOICE_DEFAULTS = {
    "system_voice": "jane",
    "my_voice": "jane",  # MVP fallback: reuse high-quality preset voice if cloning provider is absent.
}


def _make_silence_mp3(duration_sec: int = 8) -> bytes:
    tmp_wav = "/tmp/voice.wav"
    tmp_mp3 = "/tmp/voice.mp3"
    ffmpeg = settings.ffmpeg_path or os.getenv("FFMPEG_PATH", "ffmpeg")

    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-t",
            str(duration_sec),
            tmp_wav,
        ],
        check=True,
    )
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            tmp_wav,
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "4",
            tmp_mp3,
        ],
        check=True,
    )

    with open(tmp_mp3, "rb") as file:
        return file.read()


def process_audio_job(job_id: str):
    db: Session = SessionLocal()
    job = None
    try:
        job = db.query(AudioJob).filter(AudioJob.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        job.updated_at = datetime.utcnow()
        db.commit()

        if job.voice_mode == "system_voice":
            selected_voice = job.preset_voice_id or VOICE_DEFAULTS["system_voice"]
        else:
            selected_voice = VOICE_DEFAULTS["my_voice"]

        tts_audio = synthesize_with_fallback(job.input_text, voice_id=selected_voice)
        if not tts_audio:
            tts_audio = _make_silence_mp3()

        duration_sec = max(30, int(job.duration_sec or 30))
        final_audio = mix_and_master_mp3(
            voice_bytes=tts_audio,
            music_track_id=job.music_track_id,
            target_duration_sec=duration_sec,
        )

        key = f"results/{job.id}.mp3"
        upload_bytes(key, final_audio, content_type="audio/mpeg")

        job.status = "completed"
        job.result_s3_key = key
        job.updated_at = datetime.utcnow()
        db.commit()
    except Exception as exc:
        if job:
            job.status = "failed"
            job.error = str(exc)
            job.updated_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        db.close()
