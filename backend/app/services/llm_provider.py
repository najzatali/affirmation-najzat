from __future__ import annotations

import base64
import json
import re
import uuid
from collections import defaultdict
from typing import List

import httpx

from ..core.config import settings
from ..schemas import GoalAnswer

KEY_LABELS_RU = {
    "goal_real_desire": "Желаемый результат",
    "goal_why": "Почему это важно",
    "goal_life_change": "Как изменится жизнь",
    "goal_feeling": "Какие чувства нужны",
    "reality_current": "Что происходит сейчас",
    "reality_pain": "Что беспокоит",
    "reality_fear": "Где есть страх",
    "reality_pattern": "Повторяющийся сценарий",
    "belief_why_not": "Ограничивающее убеждение",
    "belief_self_view": "Что думаешь о себе",
    "belief_childhood": "Убеждение из детства",
    "belief_auto_thought": "Первая автоматическая мысль",
    "faith_possible": "Вера в возможность (1-10)",
    "faith_worthy": "Ощущение достойности (1-10)",
}

KEY_LABELS_EN = {
    "goal_real_desire": "Desired outcome",
    "goal_why": "Why it matters",
    "goal_life_change": "Life change",
    "goal_feeling": "Desired feelings",
    "reality_current": "Current reality",
    "reality_pain": "Main concern",
    "reality_fear": "Where fear appears",
    "reality_pattern": "Repeating pattern",
    "belief_why_not": "Limiting belief",
    "belief_self_view": "Self-view",
    "belief_childhood": "Childhood imprint",
    "belief_auto_thought": "First automatic thought",
    "faith_possible": "Belief this is possible (1-10)",
    "faith_worthy": "Sense of worthiness (1-10)",
}

AREA_LABELS_RU = {
    "money": "Финансы",
    "health": "Здоровье",
    "relationships": "Отношения",
    "body": "Тело",
    "career": "Карьера",
    "sleep": "Сон",
}

AREA_LABELS_EN = {
    "money": "Money",
    "health": "Health",
    "relationships": "Relationships",
    "body": "Body",
    "career": "Career",
    "sleep": "Sleep",
}


def _group_payload(goals: List[GoalAnswer], language: str) -> str:
    labels = KEY_LABELS_RU if language == "ru" else KEY_LABELS_EN
    area_labels = AREA_LABELS_RU if language == "ru" else AREA_LABELS_EN
    grouped: dict[str, list[GoalAnswer]] = defaultdict(list)
    for item in goals:
        grouped[item.area].append(item)

    chunks = []
    for area, items in grouped.items():
        area_title = area_labels.get(area, area)
        lines = []
        for it in items:
            if not (it.answer or "").strip():
                continue
            label = labels.get((it.key or "").strip(), it.prompt or it.key or "input")
            lines.append(f"- {label}: {(it.answer or '').strip()}")
        if lines:
            chunks.append(f"[{area_title}]\n" + "\n".join(lines))
    return "\n\n".join(chunks)


def _build_prompt(goals: List[GoalAnswer], language: str, tone: str) -> str:
    grouped_areas = {g.area for g in goals}
    area_count = max(1, len(grouped_areas))
    line_count = min(21, max(6, area_count * 6))
    user_context = _group_payload(goals, language)

    if language == "ru":
        return (
            "Ты senior-редактор аффирмаций. Сгенерируй текст строго в формате JSON.\n"
            "Цель: сильные, психологически безопасные аффирмации по инструкции клиента.\n"
            "Жесткие правила:\n"
            "1) Только настоящее время, как уже происходящий факт.\n"
            "2) Только формулы 'Я есть ...' или 'Я имею ...' в начале каждой строки.\n"
            "3) Запрещено: 'хочу', 'буду', вопросительные формы, отрицания с частицей 'не'.\n"
            "4) Одна строка = одна мысль. Никаких кодов категорий, вопросов и служебного текста.\n"
            "5) Добавляй эмоцию и конкретику, но без медицинских обещаний и магических гарантий.\n"
            "6) Если уровень веры низкий (1-4), используй мягкие формулировки: 'Я есть человек, который открывается...', 'Я имею право...'.\n"
            f"7) Верни ровно {line_count} строк.\n"
            f"8) Тон: {tone}.\n\n"
            "Верни ТОЛЬКО JSON без markdown:\n"
            "{\n"
            '  "affirmations": ["строка 1", "строка 2"]\n'
            "}\n\n"
            f"Данные пользователя:\n{user_context}\n"
        )

    return (
        "You are a senior affirmation editor. Generate output strictly as JSON.\n"
        "Goal: high-quality, psychologically safe affirmations.\n"
        "Rules:\n"
        "1) Present tense only, as already true now.\n"
        "2) Every line starts with 'I am' or 'I have'.\n"
        "3) Forbidden: 'I want', future tense, questions, negations.\n"
        "4) One line = one thought. No category codes, no copied questions.\n"
        "5) Add emotion and concrete meaning, no medical claims, no unrealistic guarantees.\n"
        "6) If belief score is low (1-4), use softer lines: 'I am open...', 'I have permission...'.\n"
        f"7) Return exactly {line_count} lines.\n"
        f"8) Tone: {tone}.\n\n"
        "Return JSON only:\n"
        "{\n"
        '  "affirmations": ["line 1", "line 2"]\n'
        "}\n\n"
        f"User data:\n{user_context}\n"
    )


def _token() -> str:
    if not settings.gigachat_client_id or not settings.gigachat_client_secret:
        raise RuntimeError("GigaChat credentials are not configured")

    creds = f"{settings.gigachat_client_id}:{settings.gigachat_client_secret}".encode("utf-8")
    b64 = base64.b64encode(creds).decode("utf-8")
    headers = {
        "Authorization": f"Basic {b64}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"scope": settings.gigachat_scope}
    with httpx.Client(timeout=20.0, verify=settings.gigachat_verify_ssl) as client:
        resp = client.post(settings.gigachat_auth_url, headers=headers, data=data)
        resp.raise_for_status()
        return resp.json()["access_token"]


def _parse_json_or_lines(text: str) -> List[str]:
    value = (text or "").strip()
    if not value:
        return []

    try:
        data = json.loads(value)
        items = data.get("affirmations") if isinstance(data, dict) else None
        if isinstance(items, list):
            return [str(item).strip() for item in items if str(item).strip()]
    except Exception:
        pass

    # Try to extract embedded JSON block.
    match = re.search(r"\{[\s\S]*\}", value)
    if match:
        try:
            data = json.loads(match.group(0))
            items = data.get("affirmations") if isinstance(data, dict) else None
            if isinstance(items, list):
                return [str(item).strip() for item in items if str(item).strip()]
        except Exception:
            pass

    # Fallback to numbered/bulleted lines.
    lines: List[str] = []
    for raw in value.splitlines():
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^\d+[\).\-:\s]+", "", line)
        line = re.sub(r"^[\-\*\u2022\s]+", "", line)
        line = line.strip()
        if line:
            lines.append(line)
    return lines


def generate_with_gigachat(goals: List[GoalAnswer], language: str, tone: str) -> List[str]:
    token = _token()
    prompt = _build_prompt(goals, language, tone)
    payload = {
        "model": settings.gigachat_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 900,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = f"{settings.gigachat_api_base.rstrip('/')}/chat/completions"
    with httpx.Client(timeout=35.0, verify=settings.gigachat_verify_ssl) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return _parse_json_or_lines(content)


def generate_with_ollama(goals: List[GoalAnswer], language: str, tone: str) -> List[str]:
    prompt = _build_prompt(goals, language, tone)
    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    url = f"{settings.ollama_api_base.rstrip('/')}/api/chat"
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "")
        return _parse_json_or_lines(content)


def generate_with_deepseek(goals: List[GoalAnswer], language: str, tone: str) -> List[str]:
    if not settings.deepseek_api_key:
        raise RuntimeError("DeepSeek API key is not configured")

    prompt = _build_prompt(goals, language, tone)
    payload = {
        "model": settings.deepseek_model,
        "messages": [
            {
                "role": "system",
                "content": "Return only valid JSON as requested by the user prompt.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.35,
        "max_tokens": 1200,
    }
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    url = f"{settings.deepseek_api_base.rstrip('/')}/chat/completions"
    with httpx.Client(timeout=45.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return _parse_json_or_lines(content)
