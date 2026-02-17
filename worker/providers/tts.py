import asyncio
import os
import shutil
import subprocess
import tempfile
from typing import Optional

import edge_tts
import httpx

from config import settings


VOICE_PROVIDER_MAP = {
    "alyss": {
        "yandex": "alena",
        "edge": {"voice": "ru-RU-SvetlanaNeural", "rate": "-6%", "pitch": "+2Hz"},
        "espeak": {"voice": "ru+f3", "speed": 152, "pitch": 58},
    },
    "jane": {
        "yandex": "jane",
        "edge": {"voice": "ru-RU-SvetlanaNeural", "rate": "+0%", "pitch": "+0Hz"},
        "espeak": {"voice": "ru+f2", "speed": 145, "pitch": 52},
    },
    "oksana": {
        "yandex": "oksana",
        "edge": {"voice": "ru-RU-SvetlanaNeural", "rate": "+4%", "pitch": "-2Hz"},
        "espeak": {"voice": "ru+f4", "speed": 138, "pitch": 44},
    },
    "filipp": {
        "yandex": "filipp",
        "edge": {"voice": "ru-RU-DmitryNeural", "rate": "+0%", "pitch": "+0Hz"},
        "espeak": {"voice": "ru+m3", "speed": 148, "pitch": 42},
    },
    "ermil": {
        "yandex": "ermil",
        "edge": {"voice": "ru-RU-DmitryNeural", "rate": "-10%", "pitch": "-2Hz"},
        "espeak": {"voice": "ru+m1", "speed": 136, "pitch": 36},
    },
    "zahar": {
        "yandex": "zahar",
        "edge": {"voice": "ru-RU-DmitryNeural", "rate": "+8%", "pitch": "+2Hz"},
        "espeak": {"voice": "ru+m5", "speed": 162, "pitch": 50},
    },
}


def _run(cmd: list[str]):
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _pick_espeak() -> str:
    preferred = settings.espeak_path or "espeak-ng"
    if shutil.which(preferred):
        return preferred
    return "espeak" if shutil.which("espeak") else preferred


def _contains_cyrillic(text: str) -> bool:
    return any("а" <= ch.lower() <= "я" or ch.lower() == "ё" for ch in text)


def _mock_tts(_: str) -> bytes:
    return b""


def _voice_map(voice_id: Optional[str]) -> dict:
    if voice_id and voice_id in VOICE_PROVIDER_MAP:
        return VOICE_PROVIDER_MAP[voice_id]
    return {
        "yandex": settings.yandex_voice,
        "edge": {"voice": "ru-RU-SvetlanaNeural", "rate": "+0%", "pitch": "+0Hz"},
        "espeak": {"voice": "ru+f2", "speed": 145, "pitch": 50},
    }


def _yandex_tts(text: str, voice_id: Optional[str] = None) -> bytes:
    if not settings.yandex_api_key:
        raise RuntimeError("YANDEX_API_KEY is not configured")
    mapped_voice = _voice_map(voice_id).get("yandex") or settings.yandex_voice
    headers = {"Authorization": f"Api-Key {settings.yandex_api_key}"}
    data = {
        "text": text,
        "lang": settings.yandex_lang,
        "voice": mapped_voice,
        "format": settings.yandex_format,
    }
    with httpx.Client(timeout=40.0) as client:
        resp = client.post(settings.yandex_tts_url, headers=headers, data=data)
        resp.raise_for_status()
        return resp.content


def _salute_tts(text: str, voice_id: Optional[str] = None) -> bytes:
    if not settings.salute_api_key:
        raise RuntimeError("SALUTE_API_KEY is not configured")
    # Salute voice naming is provider-specific. We keep configured default for reliability.
    headers = {"Authorization": f"Bearer {settings.salute_api_key}"}
    payload = {
        "text": text,
        "voice": settings.salute_voice,
        "lang": settings.salute_lang,
        "format": "mp3",
    }
    with httpx.Client(timeout=40.0) as client:
        resp = client.post(settings.salute_tts_url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.content


async def _edge_save_to_file(text: str, voice_name: str, rate: str, pitch: str, path: str):
    communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate, pitch=pitch)
    await communicate.save(path)


def _edge_tts(text: str, voice_id: Optional[str] = None) -> bytes:
    voice = _voice_map(voice_id).get("edge", {})
    voice_name = voice.get("voice") or ("ru-RU-SvetlanaNeural" if _contains_cyrillic(text) else "en-US-AriaNeural")
    rate = voice.get("rate", "+0%")
    pitch = voice.get("pitch", "+0Hz")
    with tempfile.TemporaryDirectory(prefix="tts-edge-") as tmp:
        out_path = os.path.join(tmp, "speech.mp3")
        asyncio.run(_edge_save_to_file(text, voice_name, rate, pitch, out_path))
        with open(out_path, "rb") as f:
            return f.read()


def _espeak_tts(text: str, voice_id: Optional[str] = None) -> bytes:
    profile = _voice_map(voice_id).get("espeak")
    if not profile:
        if _contains_cyrillic(text):
            profile = {"voice": "ru+f2", "speed": 145, "pitch": 50}
        else:
            profile = {"voice": "en-us+f3", "speed": 150, "pitch": 52}
    espeak_bin = _pick_espeak()
    ffmpeg = settings.ffmpeg_path or os.getenv("FFMPEG_PATH", "ffmpeg")
    with tempfile.TemporaryDirectory(prefix="tts-") as tmp:
        wav_path = os.path.join(tmp, "speech.wav")
        mp3_path = os.path.join(tmp, "speech.mp3")
        _run(
            [
                espeak_bin,
                "-v",
                str(profile["voice"]),
                "-s",
                str(profile["speed"]),
                "-p",
                str(profile["pitch"]),
                "-w",
                wav_path,
                text,
            ]
        )
        _run(
            [
                ffmpeg,
                "-y",
                "-i",
                wav_path,
                "-ar",
                "44100",
                "-ac",
                "2",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                mp3_path,
            ]
        )
        with open(mp3_path, "rb") as f:
            return f.read()


def _synthesize_by_provider(provider: str, text: str, voice_id: Optional[str]) -> bytes:
    if provider == "yandex":
        return _yandex_tts(text, voice_id=voice_id)
    if provider == "salute":
        return _salute_tts(text, voice_id=voice_id)
    if provider == "edge":
        return _edge_tts(text, voice_id=voice_id)
    if provider == "espeak":
        return _espeak_tts(text, voice_id=voice_id)
    return _mock_tts(text)


def synthesize(text: str, voice_id: Optional[str] = None) -> bytes:
    provider = settings.tts_provider.lower()
    return _synthesize_by_provider(provider, text, voice_id)


def synthesize_with_fallback(text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
    if not text.strip():
        return None
    provider = settings.tts_provider.lower()
    order = [provider]
    if provider == "yandex":
        order.extend(["salute", "edge", "espeak"])
    elif provider == "salute":
        order.extend(["yandex", "edge", "espeak"])
    elif provider == "edge":
        order.extend(["yandex", "salute", "espeak"])
    elif provider == "espeak":
        order.append("espeak")
    else:
        order.extend(["edge", "espeak"])

    seen = set()
    for name in order:
        if name in seen:
            continue
        seen.add(name)
        try:
            audio = _synthesize_by_provider(name, text, voice_id)
            if audio:
                return audio
        except Exception:
            continue
    return None
