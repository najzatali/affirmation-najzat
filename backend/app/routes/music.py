from fastapi import APIRouter, Query
from fastapi.responses import Response

from ..services.audio_preview import generate_music_preview_mp3

router = APIRouter(prefix="/music", tags=["music"])

MUSIC = [
    {
        "id": "calm-1",
        "title": "Serene View",
        "mood": "calm",
        "source": "Mixkit",
        "license_url": "https://mixkit.co/license/",
    },
    {
        "id": "calm-2",
        "title": "Relaxing in Nature",
        "mood": "calm",
        "source": "Mixkit",
        "license_url": "https://mixkit.co/license/",
    },
    {
        "id": "focus-1",
        "title": "Valley Sunset",
        "mood": "focus",
        "source": "Mixkit",
        "license_url": "https://mixkit.co/license/",
    },
    {
        "id": "deep-1",
        "title": "Beautiful Dream",
        "mood": "deep",
        "source": "Mixkit",
        "license_url": "https://mixkit.co/license/",
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
def music_preview(track_id: str, duration_sec: int = Query(8, ge=4, le=20)):
    data = generate_music_preview_mp3(track_id, duration_sec=duration_sec)
    return Response(content=data, media_type="audio/mpeg")
