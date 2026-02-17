import os
import subprocess
from datetime import datetime
from sqlalchemy.orm import Session
from db import SessionLocal
from models import AudioJob
from storage import upload_bytes
from config import settings
from providers.tts import synthesize_with_fallback
from audio_engine import mix_and_master_mp3


def _make_silence_mp3(duration_sec: int = 8) -> bytes:
    tmp_wav = "/tmp/voice.wav"
    tmp_mp3 = "/tmp/voice.mp3"
    ffmpeg = settings.ffmpeg_path or os.getenv("FFMPEG_PATH", "ffmpeg")

    # Generate silent WAV
    subprocess.run([
        ffmpeg, "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-t", str(duration_sec), tmp_wav
    ], check=True)

    # Convert to MP3
    subprocess.run([
        ffmpeg, "-y", "-i", tmp_wav, "-codec:a", "libmp3lame", "-qscale:a", "4", tmp_mp3
    ], check=True)

    with open(tmp_mp3, "rb") as f:
        return f.read()


def process_audio_job(job_id: str):
    db: Session = SessionLocal()
    try:
        job = db.query(AudioJob).filter(AudioJob.id == job_id).first()
        if not job:
            return
        job.status = "processing"
        job.updated_at = datetime.utcnow()
        db.commit()

        # TTS provider chain: configured provider, then fallback provider.
        selected_voice = job.preset_voice_id if job.voice_mode == "system_voice" else None
        audio_bytes = synthesize_with_fallback(job.input_text, voice_id=selected_voice)
        if not audio_bytes:
            audio_bytes = _make_silence_mp3()
        duration_sec = max(30, int(job.duration_sec or 30))
        audio_bytes = mix_and_master_mp3(audio_bytes, job.music_track_id, target_duration_sec=duration_sec)
        key = f"results/{job.id}.mp3"
        upload_bytes(key, audio_bytes, content_type="audio/mpeg")

        job.status = "completed"
        job.result_s3_key = key
        job.updated_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        if job:
            job.status = "failed"
            job.error = str(e)
            job.updated_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        db.close()
