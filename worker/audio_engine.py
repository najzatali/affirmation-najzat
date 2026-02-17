from __future__ import annotations

import os
import subprocess
import tempfile
import uuid

from config import settings


MUSIC_FILTERS = {
    "calm-1": "0.014*sin(2*PI*174*t)+0.011*sin(2*PI*220*t)+0.007*sin(2*PI*261*t)",
    "calm-2": "0.012*sin(2*PI*164*t)+0.010*sin(2*PI*207*t)+0.006*sin(2*PI*246*t)",
    "calm-3": "0.013*sin(2*PI*196*t)+0.010*sin(2*PI*247*t)+0.006*sin(2*PI*294*t)",
    "deep-1": "0.015*sin(2*PI*130*t)+0.010*sin(2*PI*165*t)+0.006*sin(2*PI*196*t)",
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


def _generate_music_bed(track_id: str, duration_sec: float, out_path: str):
    ffmpeg = settings.ffmpeg_path
    expr = MUSIC_FILTERS.get(track_id, MUSIC_FILTERS["calm-1"])
    source = f"aevalsrc={expr}:s=44100"
    fade_out_start = max(0.0, duration_sec - 2.0)

    _run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            source,
            "-t",
            str(duration_sec),
            "-af",
            f"lowpass=f=1800,afade=t=in:st=0:d=1,afade=t=out:st={fade_out_start}:d=2",
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
        music_in = os.path.join(tmp, "music_input.mp3")
        out_mp3 = os.path.join(tmp, "final.mp3")
        out_fitted_mp3 = os.path.join(tmp, "final_fitted.mp3")

        with open(voice_in, "wb") as file:
            file.write(voice_bytes)

        duration = max(float(target_duration_sec), _probe_duration(voice_in))
        _generate_music_bed(track_id=music_track_id, duration_sec=duration, out_path=music_in)

        fade_out_start = max(0.0, duration - 2.0)
        filter_graph = (
            "[0:a]loudnorm=I=-16:LRA=11:TP=-1.5[voice];"
            f"[1:a]volume=-14dB,afade=t=in:st=0:d=1,afade=t=out:st={fade_out_start}:d=2[music];"
            "[voice][music]amix=inputs=2:duration=longest:dropout_transition=2[mix];"
            "[mix]loudnorm=I=-16:LRA=11:TP=-1.5[out]"
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
        with open(out_fitted_mp3, "rb") as file:
            return file.read()
