import asyncio
import os
import shutil
import subprocess
import tempfile

import edge_tts
import httpx

from ..core.config import settings


VOICE_PRESETS = {
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

MUSIC_TRACKS = {
    "calm-1": "https://assets.mixkit.co/music/443/443.mp3",
    "calm-2": "https://assets.mixkit.co/music/522/522.mp3",
    "focus-1": "https://assets.mixkit.co/music/127/127.mp3",
    "deep-1": "https://assets.mixkit.co/music/493/493.mp3",
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
        return "Я есть спокойствие, уверенность и ясность. Я имею устойчивый внутренний баланс."
    return "I am calm, confident, and clear. I have steady inner balance."


def _music_source(track_id: str) -> str:
    if track_id == "calm-2":
        return "sine=frequency=174:sample_rate=44100,volume=0.08"
    if track_id == "focus-1":
        return "sine=frequency=220:sample_rate=44100,volume=0.06"
    if track_id == "deep-1":
        return "sine=frequency=140:sample_rate=44100,volume=0.07"
    return "sine=frequency=196:sample_rate=44100,volume=0.08"


async def _edge_save_to_file(text: str, voice_name: str, rate: str, pitch: str, path: str):
    communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate, pitch=pitch)
    await communicate.save(path)


def _download_file(url: str, path: str):
    with httpx.Client(timeout=25.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)


def _yandex_preview(text: str, yandex_voice: str) -> bytes:
    if not settings.yandex_api_key:
        raise RuntimeError("YANDEX_API_KEY is not configured")
    headers = {"Authorization": f"Api-Key {settings.yandex_api_key}"}
    data = {"text": text, "lang": "ru-RU", "voice": yandex_voice, "format": "mp3"}
    with httpx.Client(timeout=25.0) as client:
        resp = client.post("https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize", headers=headers, data=data)
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
            "128k",
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
        edge_voice = preset.get("edge", {})
        try:
            if settings.tts_provider.lower() == "yandex":
                yandex_voice = preset.get("yandex", "jane")
                data = _yandex_preview(_voice_text(language), yandex_voice)
                with open(mp3_path, "wb") as f:
                    f.write(data)
                with open(mp3_path, "rb") as f:
                    return f.read()
            voice_name = edge_voice.get("voice", "ru-RU-SvetlanaNeural")
            rate = edge_voice.get("rate", "+0%")
            pitch = edge_voice.get("pitch", "+0Hz")
            asyncio.run(_edge_save_to_file(_voice_text(language), voice_name, rate, pitch, mp3_path))
            with open(mp3_path, "rb") as f:
                return f.read()
        except Exception:
            try:
                espeak = preset.get("espeak", {"voice": "ru+f2", "speed": 145, "pitch": 50})
                _run(
                    [
                        espeak_bin,
                        "-v",
                        espeak["voice"],
                        "-s",
                        str(espeak["speed"]),
                        "-p",
                        str(espeak["pitch"]),
                        "-w",
                        wav_path,
                        _voice_text(language),
                    ]
                )
                _trim_to_preview(wav_path, mp3_path, duration_sec=8)
                with open(mp3_path, "rb") as f:
                    return f.read()
            except Exception:
                # Last fallback: short tone so preview button always responds.
                tone_freq = 220
                if voice_id in {"alyss", "jane", "oksana"}:
                    tone_freq = 330
                _run(
                    [
                        ffmpeg,
                        "-y",
                        "-f",
                        "lavfi",
                        "-i",
                        f"sine=frequency={tone_freq}:sample_rate=44100,volume=0.08",
                        "-t",
                        "4",
                        "-c:a",
                        "libmp3lame",
                        "-b:a",
                        "128k",
                        mp3_path,
                    ]
                )
                with open(mp3_path, "rb") as f:
                    return f.read()


def generate_music_preview_mp3(track_id: str, duration_sec: int = 8) -> bytes:
    ffmpeg = _ffmpeg()
    with tempfile.TemporaryDirectory(prefix="music-preview-") as tmp:
        raw_path = os.path.join(tmp, "raw.mp3")
        mp3_path = os.path.join(tmp, "preview.mp3")
        try:
            track_url = MUSIC_TRACKS.get(track_id)
            if not track_url:
                raise RuntimeError("Track URL is missing")
            _download_file(track_url, raw_path)
            _trim_to_preview(raw_path, mp3_path, duration_sec=duration_sec)
            with open(mp3_path, "rb") as f:
                return f.read()
        except Exception:
            # Fallback: generated music bed if remote track is unavailable.
            _run(
                [
                    ffmpeg,
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    _music_source(track_id),
                    "-t",
                    str(max(4, int(duration_sec))),
                    "-ar",
                    "44100",
                    "-ac",
                    "2",
                    "-c:a",
                    "libmp3lame",
                    "-b:a",
                    "128k",
                    mp3_path,
                ]
            )
            with open(mp3_path, "rb") as f:
                return f.read()
