from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import Response

from ..services.audio_preview import generate_music_preview_mp3

router = APIRouter(prefix="/music", tags=["music"])

MUSIC = [
    {
        "id": "calm-1",
        "title_ru": "Тихий рассвет",
        "title_en": "Quiet Dawn",
        "mood": "calm",
        "source": "Affirmation Studio",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    {
        "id": "calm-2",
        "title_ru": "Мягкий фокус",
        "title_en": "Soft Focus",
        "mood": "focus",
        "source": "Affirmation Studio",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    {
        "id": "calm-3",
        "title_ru": "Теплый поток",
        "title_en": "Warm Flow",
        "mood": "warm",
        "source": "Affirmation Studio",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    {
        "id": "deep-1",
        "title_ru": "Глубокое дыхание",
        "title_en": "Deep Breathing",
        "mood": "deep",
        "source": "Affirmation Studio",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
]


@router.get("")
def list_music():
    return [
        {
            **item,
            "preview_url": f"/api/music/{item['id']}/preview",
        }
        for item in MUSIC
    ]


@router.get("/{track_id}/preview")
def music_preview(track_id: str, duration_sec: int = Query(10, ge=4, le=25)):
    data = generate_music_preview_mp3(track_id, duration_sec=duration_sec)
    return Response(content=data, media_type="audio/mpeg")
