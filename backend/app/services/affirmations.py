from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List

from ..core.config import settings
from ..schemas import GoalAnswer
from .llm_provider import generate_with_deepseek, generate_with_gigachat, generate_with_ollama
from .safety import add_disclaimer, enforce_affirmation_style, sanitize

AREA_LABELS_RU = {
    "money": "финансы",
    "health": "здоровье",
    "relationships": "отношения",
    "career": "карьера",
    "body": "тело",
    "sleep": "сон",
}

AREA_LABELS_EN = {
    "money": "money",
    "health": "health",
    "relationships": "relationships",
    "career": "career",
    "body": "body",
    "sleep": "sleep",
}

RU_BAD_STARTS = (
    "как ",
    "какой ",
    "какие ",
    "почему ",
    "что ",
    "где ",
    "когда ",
)
EN_BAD_STARTS = (
    "what ",
    "which ",
    "how ",
    "why ",
    "where ",
    "when ",
)

RU_WEAK = {"хорошо", "классно", "нормально", "не знаю", "ок", "ok"}
EN_WEAK = {"good", "fine", "ok", "nice", "i dont know", "i don't know"}


def _clean(text: str) -> str:
    return " ".join((text or "").strip().split())


def _group(goals: List[GoalAnswer]) -> Dict[str, List[GoalAnswer]]:
    grouped: Dict[str, List[GoalAnswer]] = defaultdict(list)
    for item in goals:
        grouped[item.area].append(item)
    return grouped


def _answer(items: List[GoalAnswer], key: str) -> str:
    for item in items:
        if (item.key or "").strip() == key:
            return _clean(item.answer)
    return ""


def _normalize(value: str, language: str) -> str:
    text = _clean(value)
    if not text:
        return ""

    low = text.lower()
    if language == "ru":
        prefixes = ["я хочу ", "хочу ", "я буду ", "буду ", "мне нужно ", "нужно "]
    else:
        prefixes = ["i want ", "want ", "i will ", "will ", "i need ", "need "]

    for prefix in prefixes:
        if low.startswith(prefix):
            text = text[len(prefix) :]
            break

    text = text.strip(" .,!?:;")
    return _clean(text)


def _is_bad(text: str, language: str) -> bool:
    value = _clean(text)
    if not value:
        return True

    low = value.lower()
    if "?" in low:
        return True

    if language == "ru":
        if any(low.startswith(prefix) for prefix in RU_BAD_STARTS):
            return True
        if low in RU_WEAK:
            return True
        if " в сфере " in low:
            return True
    else:
        if any(low.startswith(prefix) for prefix in EN_BAD_STARTS):
            return True
        if low in EN_WEAK:
            return True
        if " in area " in low:
            return True

    return False


def _first_valid(values: Iterable[str], language: str, fallback: str) -> str:
    for raw in values:
        value = _normalize(raw, language)
        if not _is_bad(value, language):
            return value
    return fallback


def _faith_score(items: List[GoalAnswer]) -> float:
    scores: list[int] = []
    for key in ("faith_possible", "faith_worthy"):
        raw = _answer(items, key)
        digits = "".join(ch for ch in raw if ch.isdigit())
        if not digits:
            continue
        val = int(digits)
        if 1 <= val <= 10:
            scores.append(val)
    if not scores:
        return 7.0
    return sum(scores) / len(scores)


def _area_label(area: str, language: str) -> str:
    if language == "ru":
        return AREA_LABELS_RU.get(area, "жизнь")
    return AREA_LABELS_EN.get(area, "life")


def _fallback_ru(area: str, items: List[GoalAnswer]) -> List[str]:
    label = _area_label(area, "ru")
    faith_low = _faith_score(items) < 5

    result = _first_valid(
        [_answer(items, "goal_real_desire"), _answer(items, "goal_life_change"), _answer(items, "goal_why")],
        "ru",
        "стабильный результат, который усиливает мою жизнь",
    )
    feelings = _first_valid(
        [_answer(items, "goal_feeling"), _answer(items, "reality_fear")],
        "ru",
        "спокойствие, ясность и уверенность",
    )
    action = _first_valid(
        [_answer(items, "reality_current"), _answer(items, "reality_pattern")],
        "ru",
        "ежедневные простые действия в нужном ритме",
    )
    blocker = _first_valid(
        [_answer(items, "belief_why_not"), _answer(items, "belief_auto_thought"), _answer(items, "belief_childhood")],
        "ru",
        "внутреннюю опору и зрелые решения",
    )

    if faith_low:
        raw_lines = [
            f"Я есть человек, который мягко открывается росту в сфере {label}",
            f"Я имею право укреплять результат через спокойные шаги каждый день",
            f"Я есть внутреннее спокойствие и уважение к себе, когда выбираю {action}",
            f"Я имею все больше подтверждений, что мой путь ведет к состоянию: {result}",
            f"Я есть человек, который разрешает себе чувствовать {feelings}",
            f"Я имею зрелую опору и отпускаю старый сценарий: {blocker}",
        ]
    else:
        raw_lines = [
            f"Я есть человек, который уже живет в состоянии: {result}",
            f"Я имею устойчивый ритм действий и каждый день выбираю {action}",
            f"Я есть спокойная сила и ясность в теме {label}",
            "Я имею зрелые решения, которые усиливают мой результат без перегруза",
            f"Я есть благодарность и уверенность, когда ощущаю {feelings}",
            f"Я имею внутреннюю опору, которая заменила прошлый сценарий: {blocker}",
        ]

    out = []
    for line in raw_lines:
        safe = enforce_affirmation_style(sanitize(line), "ru")
        if safe and not _is_bad(safe, "ru"):
            out.append(safe)
    return out


def _fallback_en(area: str, items: List[GoalAnswer]) -> List[str]:
    label = _area_label(area, "en")
    faith_low = _faith_score(items) < 5

    result = _first_valid(
        [_answer(items, "goal_real_desire"), _answer(items, "goal_life_change"), _answer(items, "goal_why")],
        "en",
        "a stable result that improves my life",
    )
    feelings = _first_valid(
        [_answer(items, "goal_feeling"), _answer(items, "reality_fear")],
        "en",
        "calm, clarity, and confidence",
    )
    action = _first_valid(
        [_answer(items, "reality_current"), _answer(items, "reality_pattern")],
        "en",
        "simple daily actions in a healthy rhythm",
    )
    blocker = _first_valid(
        [_answer(items, "belief_why_not"), _answer(items, "belief_auto_thought"), _answer(items, "belief_childhood")],
        "en",
        "inner stability and mature decisions",
    )

    if faith_low:
        raw_lines = [
            f"I am a person who opens up to growth in {label} step by step",
            "I have permission to build my result through calm consistent action",
            f"I am calm self-respect while I choose {action}",
            f"I have growing evidence that my path leads to this state: {result}",
            f"I am a person who allows myself to feel {feelings}",
            f"I have inner stability and release the old pattern: {blocker}",
        ]
    else:
        raw_lines = [
            f"I am a person who already lives in this state: {result}",
            f"I have a steady daily rhythm and choose {action}",
            f"I am calm strength and clarity in {label}",
            "I have mature decisions that strengthen my result every day",
            f"I am gratitude and confidence while I feel {feelings}",
            f"I have an inner foundation that replaced the old pattern: {blocker}",
        ]

    out = []
    for line in raw_lines:
        safe = enforce_affirmation_style(sanitize(line), "en")
        if safe and not _is_bad(safe, "en"):
            out.append(safe)
    return out


def _dedupe(items: List[str]) -> List[str]:
    result: List[str] = []
    seen = set()
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _postprocess(items: List[str], language: str) -> List[str]:
    out: List[str] = []
    for raw in items:
        value = enforce_affirmation_style(sanitize(raw), language)
        if not value:
            continue
        if _is_bad(value, language):
            continue

        low = value.lower()
        if language == "ru" and low.startswith("я ") and not (low.startswith("я есть") or low.startswith("я имею")):
            value = "Я есть " + value[2:].strip()
        if language == "en" and low.startswith("i ") and not (low.startswith("i am") or low.startswith("i have")):
            value = "I am " + value[2:].strip()

        out.append(value)
    return _dedupe(out)


def _fallback(goals: List[GoalAnswer], language: str) -> List[str]:
    grouped = _group(goals)
    if not grouped:
        grouped = {"health": []}

    out: List[str] = []
    for area, items in grouped.items():
        if language == "ru":
            out.extend(_fallback_ru(area, items))
        else:
            out.extend(_fallback_en(area, items))
    return _dedupe(out)


def generate_affirmations(goals: List[GoalAnswer], language: str, tone: str) -> List[str]:
    grouped = _group(goals)
    area_count = max(1, len(grouped))
    min_count = area_count * 5
    max_count = area_count * 7

    fallback = _fallback(goals, language)
    provider = settings.llm_provider.lower().strip()
    llm_lines: List[str] = []

    try:
        if provider == "deepseek":
            llm_lines = _postprocess(generate_with_deepseek(goals, language, tone), language)
        elif provider == "gigachat":
            llm_lines = _postprocess(generate_with_gigachat(goals, language, tone), language)
        elif provider == "ollama":
            llm_lines = _postprocess(generate_with_ollama(goals, language, tone), language)
    except Exception:
        llm_lines = []

    merged = _dedupe(llm_lines + fallback)
    if len(merged) < min_count:
        merged.extend([line for line in fallback if line not in merged])

    return add_disclaimer(merged[:max_count], language)
