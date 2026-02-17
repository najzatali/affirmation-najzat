import os
import subprocess
import tempfile
import uuid

import httpx

from config import settings


MUSIC_TRACK_URLS = {
    "calm-1": "https://assets.mixkit.co/music/443/443.mp3",
    "calm-2": "https://assets.mixkit.co/music/522/522.mp3",
    "focus-1": "https://assets.mixkit.co/music/127/127.mp3",
    "deep-1": "https://assets.mixkit.co/music/493/493.mp3",
}


def _run(cmd: list[str]):
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _probe_duration(path: str) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    out = subprocess.check_output(cmd).decode("utf-8").strip()
    try:
        return max(1.0, float(out))
    except Exception:
        return 8.0


def _download_track(track_id: str, out_path: str) -> bool:
    url = MUSIC_TRACK_URLS.get(track_id)
    if not url:
        return False
    try:
        with httpx.Client(timeout=25.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(resp.content)
        return True
    except Exception:
        return False


def _prepare_music_from_track(track_path: str, duration_sec: float, out_path: str):
    ffmpeg = settings.ffmpeg_path
    _run(
        [
            ffmpeg,
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            track_path,
            "-t",
            str(duration_sec),
            "-ar",
            "44100",
            "-ac",
            "2",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            out_path,
        ]
    )


def _generate_music_bed(track_id: str, duration_sec: float, out_path: str):
    ffmpeg = settings.ffmpeg_path
    if track_id == "calm-2":
        src = "sine=frequency=174:sample_rate=44100,volume=0.08"
    elif track_id == "focus-1":
        src = "sine=frequency=220:sample_rate=44100,volume=0.06"
    elif track_id == "deep-1":
        src = "sine=frequency=140:sample_rate=44100,volume=0.07"
    else:
        src = "sine=frequency=196:sample_rate=44100,volume=0.08"
    _run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            src,
            "-t",
            str(duration_sec),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            out_path,
        ]
    )


def _fit_to_duration(in_path: str, duration_sec: int, out_path: str):
    ffmpeg = settings.ffmpeg_path
    _run(
        [
            ffmpeg,
            "-y",
            "-i",
            in_path,
            "-af",
            f"apad=pad_dur={duration_sec},atrim=0:{duration_sec}",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            out_path,
        ]
    )


def mix_and_master_mp3(voice_bytes: bytes, music_track_id: str, target_duration_sec: int) -> bytes:
    ffmpeg = settings.ffmpeg_path
    temp_id = str(uuid.uuid4())
    with tempfile.TemporaryDirectory(prefix=f"audio-{temp_id}-") as tmp:
        voice_in = os.path.join(tmp, "voice_input.mp3")
        music_raw = os.path.join(tmp, "music_raw.mp3")
        music_in = os.path.join(tmp, "music_input.mp3")
        out_mp3 = os.path.join(tmp, "final.mp3")
        out_fitted_mp3 = os.path.join(tmp, "final_fitted.mp3")

        with open(voice_in, "wb") as f:
            f.write(voice_bytes)

        duration = max(float(target_duration_sec), _probe_duration(voice_in))
        if _download_track(music_track_id, music_raw):
            _prepare_music_from_track(music_raw, duration, music_in)
        else:
            _generate_music_bed(music_track_id, duration, music_in)

        fade_out_start = max(0.0, duration - 2.0)
        filter_graph = (
            f"[0:a]loudnorm=I=-16:LRA=11:TP=-1.5[voice];"
            f"[1:a]volume=-14dB,afade=t=in:st=0:d=2,afade=t=out:st={fade_out_start}:d=2[music];"
            f"[voice][music]amix=inputs=2:duration=longest:dropout_transition=2[mix];"
            f"[mix]loudnorm=I=-16:LRA=11:TP=-1.5[out]"
        )

        _run(
            [
                ffmpeg,
                "-y",
                "-i",
                voice_in,
                "-i",
                music_in,
                "-filter_complex",
                filter_graph,
                "-map",
                "[out]",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                out_mp3,
            ]
        )
        _fit_to_duration(out_mp3, target_duration_sec, out_fitted_mp3)
        with open(out_fitted_mp3, "rb") as f:
            return f.read()
