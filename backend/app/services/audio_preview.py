from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import tempfile

import edge_tts
import httpx

from ..core.config import settings


VOICE_PRESETS = {
    "alice": {
        "yandex": "alena",
        "edge": {"voice": "ru-RU-SvetlanaNeural", "rate": "-4%", "pitch": "+1Hz"},
        "espeak": {"voice": "ru+f3", "speed": 150, "pitch": 58},
    },
    "jane": {
        "yandex": "jane",
        "edge": {"voice": "ru-RU-SvetlanaNeural", "rate": "+2%", "pitch": "+0Hz"},
        "espeak": {"voice": "ru+f2", "speed": 142, "pitch": 52},
    },
    "oksana": {
        "yandex": "oksana",
        "edge": {"voice": "ru-RU-SvetlanaNeural", "rate": "-1%", "pitch": "-2Hz"},
        "espeak": {"voice": "ru+f4", "speed": 136, "pitch": 44},
    },
    "filipp": {
        "yandex": "filipp",
        "edge": {"voice": "ru-RU-DmitryNeural", "rate": "+0%", "pitch": "+0Hz"},
        "espeak": {"voice": "ru+m3", "speed": 145, "pitch": 42},
    },
    "ermil": {
        "yandex": "ermil",
        "edge": {"voice": "ru-RU-DmitryNeural", "rate": "-8%", "pitch": "-2Hz"},
        "espeak": {"voice": "ru+m1", "speed": 138, "pitch": 36},
    },
    "zahar": {
        "yandex": "zahar",
        "edge": {"voice": "ru-RU-DmitryNeural", "rate": "+7%", "pitch": "+2Hz"},
        "espeak": {"voice": "ru+m5", "speed": 154, "pitch": 48},
    },
}

MUSIC_FILTERS = {
    "calm-1": "0.014*sin(2*PI*174*t)+0.011*sin(2*PI*220*t)+0.007*sin(2*PI*261*t)",
    "calm-2": "0.012*sin(2*PI*164*t)+0.010*sin(2*PI*207*t)+0.006*sin(2*PI*246*t)",
    "calm-3": "0.013*sin(2*PI*196*t)+0.010*sin(2*PI*247*t)+0.006*sin(2*PI*294*t)",
    "deep-1": "0.015*sin(2*PI*130*t)+0.010*sin(2*PI*165*t)+0.006*sin(2*PI*196*t)",
}


def _run(cmd: list[str]):
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _pick_espeak() -> str:
    preferred = settings.espeak_path or "espeak-ng"
    if shutil.which(preferred):
        return preferred
    return "espeak" if shutil.which("espeak") else preferred


def _ffmpeg() -> str:
    return settings.ffmpeg_path or "ffmpeg"


def _voice_text(language: str) -> str:
    if language == "ru":
        return "Я есть спокойствие и уверенность. Я имею ясный фокус и внутреннюю опору каждый день."
    return "I am calm and confident. I have clear focus and inner stability every day."


async def _edge_save_to_file(text: str, voice_name: str, rate: str, pitch: str, path: str):
    communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate, pitch=pitch)
    await communicate.save(path)


def _yandex_preview(text: str, voice_name: str) -> bytes:
    if not settings.yandex_api_key:
        raise RuntimeError("YANDEX_API_KEY is not configured")

    headers = {"Authorization": f"Api-Key {settings.yandex_api_key}"}
    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": voice_name,
        "format": "mp3",
    }
    with httpx.Client(timeout=25.0) as client:
        resp = client.post(settings.yandex_tts_url, headers=headers, data=data)
        resp.raise_for_status()
        return resp.content


def _trim_to_preview(in_path: str, out_path: str, duration_sec: int):
    ffmpeg = _ffmpeg()
    _run(
        [
            ffmpeg,
            "-y",
            "-i",
            in_path,
            "-t",
            str(max(4, int(duration_sec))),
            "-ar",
            "44100",
            "-ac",
            "2",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "160k",
            out_path,
        ]
    )


def _build_generated_music(track_id: str, duration_sec: int, out_path: str):
    ffmpeg = _ffmpeg()
    expr = MUSIC_FILTERS.get(track_id, MUSIC_FILTERS["calm-1"])
    source = f"aevalsrc={expr}:s=44100"
    fade_out_start = max(0, int(duration_sec) - 2)

    _run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            source,
            "-t",
            str(max(4, int(duration_sec))),
            "-af",
            f"lowpass=f=1800,afade=t=in:st=0:d=0.8,afade=t=out:st={fade_out_start}:d=1.8",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "160k",
            out_path,
        ]
    )


def generate_voice_preview_mp3(voice_id: str, language: str = "ru") -> bytes:
    preset = VOICE_PRESETS.get(voice_id, VOICE_PRESETS["jane"])
    espeak_bin = _pick_espeak()
    ffmpeg = _ffmpeg()

    with tempfile.TemporaryDirectory(prefix="voice-preview-") as tmp:
        wav_path = os.path.join(tmp, "preview.wav")
        mp3_path = os.path.join(tmp, "preview.mp3")

        try:
            # 1) Best quality for RU/CIS if user provided Yandex key.
            if settings.yandex_api_key:
                data = _yandex_preview(_voice_text(language), preset.get("yandex", "jane"))
                with open(mp3_path, "wb") as f:
                    f.write(data)
                with open(mp3_path, "rb") as f:
                    return f.read()

            # 2) Free fallback.
            edge_cfg = preset.get("edge", {})
            voice_name = edge_cfg.get("voice", "ru-RU-SvetlanaNeural")
            rate = edge_cfg.get("rate", "+0%")
            pitch = edge_cfg.get("pitch", "+0Hz")
            asyncio.run(_edge_save_to_file(_voice_text(language), voice_name, rate, pitch, mp3_path))
            with open(mp3_path, "rb") as f:
                return f.read()
        except Exception:
            # 3) Last fallback to local TTS.
            espeak_cfg = preset.get("espeak", {"voice": "ru+f2", "speed": 145, "pitch": 50})
            _run(
                [
                    espeak_bin,
                    "-v",
                    espeak_cfg["voice"],
                    "-s",
                    str(espeak_cfg["speed"]),
                    "-p",
                    str(espeak_cfg["pitch"]),
                    "-w",
                    wav_path,
                    _voice_text(language),
                ]
            )
            _trim_to_preview(wav_path, mp3_path, duration_sec=8)
            with open(mp3_path, "rb") as f:
                return f.read()


def generate_music_preview_mp3(track_id: str, duration_sec: int = 10) -> bytes:
    with tempfile.TemporaryDirectory(prefix="music-preview-") as tmp:
        mp3_path = os.path.join(tmp, "preview.mp3")
        _build_generated_music(track_id=track_id, duration_sec=max(4, int(duration_sec)), out_path=mp3_path)
        with open(mp3_path, "rb") as f:
            return f.read()
