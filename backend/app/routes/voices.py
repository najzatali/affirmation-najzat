from fastapi import APIRouter, Query
from fastapi.responses import Response

from ..services.audio_preview import generate_voice_preview_mp3

router = APIRouter(prefix="/voices", tags=["voices"])

SYSTEM_VOICES = [
    {"id": "alyss", "gender": "female", "label_ru": "Алиса (мягкий)", "label_en": "Alyss (soft)"},
    {"id": "jane", "gender": "female", "label_ru": "Джейн (чистый)", "label_en": "Jane (clear)"},
    {"id": "oksana", "gender": "female", "label_ru": "Оксана (глубокий)", "label_en": "Oksana (deep)"},
    {"id": "filipp", "gender": "male", "label_ru": "Филипп (уверенный)", "label_en": "Filipp (confident)"},
    {"id": "ermil", "gender": "male", "label_ru": "Ермил (спокойный)", "label_en": "Ermil (calm)"},
    {"id": "zahar", "gender": "male", "label_ru": "Захар (энергичный)", "label_en": "Zahar (energetic)"},
]


@router.get("")
def list_voices():
    return [
        {
            **item,
            "preview_url": f"/api/voices/{item['id']}/preview",
        }
        for item in SYSTEM_VOICES
    ]


@router.get("/{voice_id}/preview")
def voice_preview(voice_id: str, lang: str = Query("ru", pattern="^(ru|en)$")):
    data = generate_voice_preview_mp3(voice_id, language=lang)
    return Response(content=data, media_type="audio/mpeg")
