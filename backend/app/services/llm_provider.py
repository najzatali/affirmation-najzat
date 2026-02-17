import base64
import uuid
import re
from typing import List

import httpx

from ..core.config import settings
from ..schemas import GoalAnswer


KEY_LABELS_RU = {
    "goal_real_desire": "желанный результат",
    "goal_why": "почему это важно",
    "goal_life_change": "изменения в жизни",
    "goal_feeling": "желаемое ощущение",
    "reality_current": "текущая реальность",
    "reality_pain": "ключевая трудность",
    "reality_fear": "внутреннее напряжение",
    "reality_pattern": "повторяющийся сценарий",
    "belief_why_not": "убеждение, которое тормозит",
    "belief_self_view": "образ себя",
    "belief_childhood": "убеждение из прошлого",
    "belief_auto_thought": "автоматическая мысль",
    "faith_possible": "вера, что возможно (1-10)",
    "faith_worthy": "ощущение достойности (1-10)",
}

KEY_LABELS_EN = {
    "goal_real_desire": "desired outcome",
    "goal_why": "why it matters",
    "goal_life_change": "life change",
    "goal_feeling": "desired feeling",
    "reality_current": "current reality",
    "reality_pain": "main challenge",
    "reality_fear": "inner tension",
    "reality_pattern": "repeating pattern",
    "belief_why_not": "limiting belief",
    "belief_self_view": "self-image",
    "belief_childhood": "belief from the past",
    "belief_auto_thought": "automatic thought",
    "faith_possible": "belief this is possible (1-10)",
    "faith_worthy": "sense of worthiness (1-10)",
}


def _build_prompt(goals: List[GoalAnswer], language: str, tone: str) -> str:
    grouped = {}
    for item in goals:
        grouped.setdefault(item.area, []).append(item)

    chunks = []
    for area, items in grouped.items():
        lines = []
        for it in items:
            labels = KEY_LABELS_RU if language == "ru" else KEY_LABELS_EN
            label = labels.get((it.key or "").strip(), (it.key or "input").strip())
            val = (it.answer or "").strip()
            if val:
                lines.append(f"- {label}: {val}")
        if lines:
            chunks.append(f"[{area}]\n" + "\n".join(lines))
    joined = "\n\n".join(chunks)
    areas_count = max(1, len(grouped))
    lines_per_area = 5
    total_lines = areas_count * lines_per_area

    if language == "ru":
        return (
            "Сгенерируй персональные аффирмации строго по правилам.\n"
            "Правила:\n"
            "1) Настоящее время, как уже свершившийся факт.\n"
            "2) Без частицы 'не' и без отрицаний.\n"
            "3) Конкретно и кратко: 1 мысль в 1 строке.\n"
            "4) Всегда от первого лица: каждая строка начинается с 'Я'.\n"
            "5) Добавляй ощущение/эмоцию, а не сухой факт.\n"
            "6) Без фантастики и без внутренних конфликтов.\n"
            "7) Если вера ниже 5/10, используй мягкие формулировки: 'Я открыт', 'Я разрешаю себе', 'Я учусь'.\n"
            "8) Не копируй текст вопросов, не пиши названия категорий и коды вроде money/health.\n"
            "9) Не используй слова: 'хочу', 'буду', '?'.\n"
            f"Выдай ровно {total_lines} строк ({lines_per_area} на каждую выбранную сферу).\n"
            f"Тон: {tone}\n"
            f"Данные пользователя:\n{joined}\n"
            "Верни только нумерованный список."
        )
    return (
        "Generate personal affirmations following strict rules.\n"
        "Rules:\n"
        "1) Present tense, already true now.\n"
        "2) No negations.\n"
        "3) Specific and concise: one thought per line.\n"
        "4) First person: each line starts with 'I'.\n"
        "5) Include emotional state, not only facts.\n"
        "6) No fantasy claims and no internal contradiction.\n"
        "7) If belief is below 5/10, use soft lines: 'I am open', 'I allow myself', 'I am learning'.\n"
        "8) Do not copy question text and do not mention category code names.\n"
        "9) Do not use: 'I want', future tense, '?'.\n"
        f"Return exactly {total_lines} lines ({lines_per_area} per selected area).\n"
        f"Tone: {tone}\n"
        f"User context:\n{joined}\n"
        "Return only a numbered list."
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


def _parse_numbered_lines(text: str) -> List[str]:
    items: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line[0].isdigit():
            _, _, value = line.partition(".")
            line = value.strip() if value else line
        line = re.sub(r"^[\-\*\u2022]\s*", "", line).strip()
        if line:
            items.append(line)
    return items[:32]


def generate_with_gigachat(goals: List[GoalAnswer], language: str, tone: str) -> List[str]:
    token = _token()
    prompt = _build_prompt(goals, language, tone)
    payload = {
        "model": settings.gigachat_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 400,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = f"{settings.gigachat_api_base.rstrip('/')}/chat/completions"
    with httpx.Client(timeout=30.0, verify=settings.gigachat_verify_ssl) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        parsed = _parse_numbered_lines(content)
        return parsed if parsed else [content.strip()]


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
        content = resp.json().get("message", {}).get("content", "").strip()
        parsed = _parse_numbered_lines(content)
        return parsed if parsed else [content]


def generate_with_deepseek(goals: List[GoalAnswer], language: str, tone: str) -> List[str]:
    if not settings.deepseek_api_key:
        raise RuntimeError("DeepSeek API key is not configured")
    prompt = _build_prompt(goals, language, tone)
    payload = {
        "model": settings.deepseek_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 700,
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
        parsed = _parse_numbered_lines(content)
        return parsed if parsed else [content.strip()]
