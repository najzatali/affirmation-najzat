import base64
import json
from typing import List

import httpx

from ..core.config import settings
from ..schemas import ScreenshotReviewResponse


MAX_SCREENSHOT_BYTES = 6 * 1024 * 1024


def _clean(text: str) -> str:
    return " ".join((text or "").split()).strip()


def _normalize_list(items: List[str]) -> List[str]:
    clean = [_clean(str(item)) for item in (items or []) if _clean(str(item))]
    unique = []
    for item in clean:
        if item not in unique:
            unique.append(item)
    return unique[:6]


def _parse_json_block(text: str) -> dict:
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Empty screenshot review response")

    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start : end + 1]

    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("Review response is not an object")
    return parsed


def _build_prompt(
    language: str,
    module_title: str,
    mission_title: str,
    learner_note: str,
    required_checks: List[str],
) -> str:
    lang = language if language in {"ru", "en"} else "ru"
    checks = _normalize_list(required_checks)

    if lang == "ru":
        checklist = "\n".join([f"- {item}" for item in checks]) if checks else "- Нет явных чекпойнтов"
        return (
            "Ты AI-проверяющий домашнего задания в курсе по AI.\n"
            "Нужно оценить, подтверждает ли скриншот выполнение практической задачи.\n"
            "Верни СТРОГО JSON с полями:\n"
            "passed (boolean), score (0-100), summary (string), found (array of strings), "
            "missing (array of strings), next_action (string).\n"
            "Правила:\n"
            "1) score отражает реальное качество подтверждения.\n"
            "2) passed=true только если на скриншоте явно видно выполнение ключевых шагов.\n"
            "3) found: что действительно видно.\n"
            "4) missing: чего не хватает для подтверждения.\n"
            "5) next_action: одно конкретное действие для пересдачи/улучшения.\n"
            "6) Пиши просто и коротко, без воды.\n"
            f"Модуль: {module_title}\n"
            f"Практическая миссия: {mission_title}\n"
            f"Комментарий ученика: {_clean(learner_note) or 'не указан'}\n"
            f"Чекпойнты задания:\n{checklist}"
        )

    checklist = "\n".join([f"- {item}" for item in checks]) if checks else "- No explicit checkpoints"
    return (
        "You are an AI homework reviewer for an AI course.\n"
        "Evaluate whether screenshot evidence confirms mission completion.\n"
        "Return STRICT JSON with fields:\n"
        "passed (boolean), score (0-100), summary (string), found (array of strings), "
        "missing (array of strings), next_action (string).\n"
        "Rules:\n"
        "1) score must reflect real evidence quality.\n"
        "2) passed=true only when key mission actions are clearly visible.\n"
        "3) found: only what is visible.\n"
        "4) missing: what is required but not visible.\n"
        "5) next_action: one concrete retry/improvement action.\n"
        "6) keep response concise and plain.\n"
        f"Module: {module_title}\n"
        f"Practice mission: {mission_title}\n"
        f"Learner note: {_clean(learner_note) or 'not provided'}\n"
        f"Mission checkpoints:\n{checklist}"
    )


def _openai_vision(prompt: str, image_bytes: bytes, content_type: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API key is not configured")

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{content_type};base64,{image_b64}"
    url = f"{settings.openai_api_base.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openai_model,
        "temperature": 0.2,
        "max_tokens": 500,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def _fallback_review(
    language: str,
    learner_note: str,
    required_checks: List[str],
    image_bytes: bytes,
    content_type: str,
) -> ScreenshotReviewResponse:
    lang = language if language in {"ru", "en"} else "ru"
    checks = _normalize_list(required_checks)
    size_ok = len(image_bytes or b"") > 14_000
    mime_ok = (content_type or "").startswith("image/")
    has_note = len(_clean(learner_note)) >= 20
    prelim_pass = bool(size_ok and mime_ok and has_note)

    if lang == "ru":
        if prelim_pass:
            return ScreenshotReviewResponse(
                passed=True,
                score=70,
                summary="Скриншот принят в предварительном режиме: файл выглядит корректно, есть пояснение ученика.",
                found=["Скриншот загружен", "Есть текстовый комментарий к выполнению"],
                missing=checks[:2],
                next_action=(
                    "Добавь на скриншот видимые элементы результата (название сервиса, введенный запрос, полученный ответ) "
                    "и отправь повторно для точной AI-проверки."
                ),
                provider="fallback",
                fallback=True,
            )
        return ScreenshotReviewResponse(
            passed=False,
            score=35,
            summary="Недостаточно данных для подтверждения задания.",
            found=["Файл получен" if image_bytes else "Файл не получен"],
            missing=checks[:3] or ["Нет читаемого скриншота", "Нет понятного описания выполнения"],
            next_action="Загрузи четкий скриншот и добавь 2-3 предложения: что сделал и что получилось.",
            provider="fallback",
            fallback=True,
        )

    if prelim_pass:
        return ScreenshotReviewResponse(
            passed=True,
            score=70,
            summary="Screenshot accepted in preliminary mode: file looks valid and learner note is present.",
            found=["Screenshot file uploaded", "Learner note is provided"],
            missing=checks[:2],
            next_action="Retake screenshot with visible service name, prompt, and generated output for full AI verification.",
            provider="fallback",
            fallback=True,
        )
    return ScreenshotReviewResponse(
        passed=False,
        score=35,
        summary="Not enough evidence to confirm task completion.",
        found=["File received" if image_bytes else "No file data"],
        missing=checks[:3] or ["No readable screenshot", "No clear execution note"],
        next_action="Upload a clear screenshot and add 2-3 sentences describing what you did and what result you got.",
        provider="fallback",
        fallback=True,
    )


def review_screenshot(
    language: str,
    module_title: str,
    mission_title: str,
    learner_note: str,
    required_checks: List[str],
    image_bytes: bytes,
    content_type: str,
) -> ScreenshotReviewResponse:
    if len(image_bytes or b"") == 0:
        raise ValueError("Screenshot file is empty")
    if len(image_bytes) > MAX_SCREENSHOT_BYTES:
        raise ValueError("Screenshot file is too large")
    if not (content_type or "").startswith("image/"):
        raise ValueError("Only image files are supported")

    prompt = _build_prompt(language, module_title, mission_title, learner_note, required_checks)

    use_openai = bool(settings.openai_api_key)
    if not use_openai:
        return _fallback_review(language, learner_note, required_checks, image_bytes, content_type)

    try:
        raw = _openai_vision(prompt, image_bytes, content_type)
        parsed = _parse_json_block(raw)

        found = _normalize_list(parsed.get("found", []))
        missing = _normalize_list(parsed.get("missing", []))
        score = max(0, min(100, int(parsed.get("score", 0))))
        passed = bool(parsed.get("passed", False))
        summary = _clean(str(parsed.get("summary", "")))
        next_action = _clean(str(parsed.get("next_action", "")))

        if not summary:
            raise ValueError("Missing summary")
        if not next_action:
            raise ValueError("Missing next_action")

        return ScreenshotReviewResponse(
            passed=passed,
            score=score,
            summary=summary,
            found=found,
            missing=missing,
            next_action=next_action,
            provider="openai",
            fallback=False,
        )
    except Exception:
        return _fallback_review(language, learner_note, required_checks, image_bytes, content_type)
