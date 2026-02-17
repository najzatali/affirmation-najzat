from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List

from ..core.config import settings
from ..schemas import GoalAnswer
from .llm_provider import generate_with_deepseek, generate_with_gigachat, generate_with_ollama
from .safety import add_disclaimer, enforce_affirmation_style, sanitize

AREA_LABELS_RU = {
    "money": "финансов",
    "health": "здоровья",
    "relationships": "отношений",
    "career": "карьеры",
    "body": "тела",
    "sleep": "сна",
}

AREA_LABELS_EN = {
    "money": "money",
    "health": "health",
    "relationships": "relationships",
    "career": "career",
    "body": "body",
    "sleep": "sleep",
}

RU_BAD_STARTS = ("как ", "какой ", "какие ", "почему ", "что ", "где ", "когда ")
EN_BAD_STARTS = ("what ", "which ", "how ", "why ", "where ", "when ")

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
        prefixes = ["я хочу ", "хочу ", "я буду ", "буду ", "мне нужно ", "нужно ", "я бы хотел ", "я бы хотела "]
    else:
        prefixes = ["i want ", "want ", "i will ", "will ", "i need ", "need ", "i would like "]

    for prefix in prefixes:
        if low.startswith(prefix):
            text = text[len(prefix) :]
            break

    return _clean(text.strip(" .,!?:;"))


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
    else:
        if any(low.startswith(prefix) for prefix in EN_BAD_STARTS):
            return True
        if low in EN_WEAK:
            return True

    return False


def _first_valid(values: Iterable[str], language: str, fallback: str) -> str:
    for raw in values:
        value = _normalize(raw, language)
        if value and not _is_bad(value, language):
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


def _with_name(line: str, user_name: str, language: str) -> str:
    name = _clean(user_name)
    if not name:
        return line

    if language == "ru" and line.startswith("Я есть "):
        return f"Я есть {name}, {line[7:].lstrip()}"
    if language == "en" and line.startswith("I am "):
        return f"I am {name}, {line[5:].lstrip()}"

    return line


def _fallback_ru(area: str, items: List[GoalAnswer], user_name: str) -> List[str]:
    area_label = AREA_LABELS_RU.get(area, "жизни")
    soft_mode = _faith_score(items) < 5

    result = _first_valid(
        [_answer(items, "goal_real_desire"), _answer(items, "goal_life_change"), _answer(items, "goal_why")],
        "ru",
        "устойчивый результат, который усиливает мою жизнь",
    )
    feeling = _first_valid(
        [_answer(items, "goal_feeling"), _answer(items, "reality_fear")],
        "ru",
        "спокойствие, уверенность и легкость",
    )
    action = _first_valid(
        [_answer(items, "reality_current"), _answer(items, "reality_pattern")],
        "ru",
        "ежедневные точные действия в правильном ритме",
    )
    blocker = _first_valid(
        [_answer(items, "belief_why_not"), _answer(items, "belief_auto_thought"), _answer(items, "belief_childhood")],
        "ru",
        "старую привычку сомневаться в себе",
    )

    if soft_mode:
        lines = [
            f"Я есть человек, который мягко открывается росту в теме {area_label}",
            f"Я имею право двигаться к результату: {result}",
            f"Я есть спокойное уважение к себе, когда выбираю {action}",
            f"Я имею устойчивый ритм и замечаю, как в моей жизни усиливается {feeling}",
            f"Я есть новая внутренняя опора, которая оставляет в прошлом сценарий: {blocker}",
            "Я имею пространство для роста и принимаю свой результат шаг за шагом",
        ]
    else:
        lines = [
            f"Я есть человек, который уже живет в состоянии: {result}",
            f"Я имею ежедневный ритм действий: {action}",
            f"Я есть спокойная сила и ясность в сфере {area_label}",
            f"Я имею зрелые решения, которые устойчиво усиливают {result}",
            f"Я есть уверенность и благодарность, когда ощущаю {feeling}",
            f"Я имею внутреннюю опору и выбираю новый сценарий вместо: {blocker}",
        ]

    if user_name:
        lines[0] = _with_name(lines[0], user_name, "ru")

    out = []
    for raw in lines:
        safe = enforce_affirmation_style(sanitize(raw), "ru")
        if safe and not _is_bad(safe, "ru"):
            out.append(safe)
    return out


def _fallback_en(area: str, items: List[GoalAnswer], user_name: str) -> List[str]:
    area_label = AREA_LABELS_EN.get(area, "life")
    soft_mode = _faith_score(items) < 5

    result = _first_valid(
        [_answer(items, "goal_real_desire"), _answer(items, "goal_life_change"), _answer(items, "goal_why")],
        "en",
        "a steady result that improves my life",
    )
    feeling = _first_valid(
        [_answer(items, "goal_feeling"), _answer(items, "reality_fear")],
        "en",
        "calm confidence and lightness",
    )
    action = _first_valid(
        [_answer(items, "reality_current"), _answer(items, "reality_pattern")],
        "en",
        "daily focused actions in the right rhythm",
    )
    blocker = _first_valid(
        [_answer(items, "belief_why_not"), _answer(items, "belief_auto_thought"), _answer(items, "belief_childhood")],
        "en",
        "old self-doubt pattern",
    )

    if soft_mode:
        lines = [
            f"I am a person who gently opens up to growth in {area_label}",
            f"I have permission to move toward this result: {result}",
            f"I am calm self-respect while I choose {action}",
            f"I have a steady rhythm and feel how {feeling} grows in my life",
            f"I am an inner foundation that leaves this old pattern behind: {blocker}",
            "I have enough space to grow and receive my result step by step",
        ]
    else:
        lines = [
            f"I am a person who already lives in this state: {result}",
            f"I have a daily action rhythm: {action}",
            f"I am calm strength and clarity in {area_label}",
            f"I have mature decisions that steadily reinforce {result}",
            f"I am confidence and gratitude while I feel {feeling}",
            f"I have inner stability and choose a new pattern instead of: {blocker}",
        ]

    if user_name:
        lines[0] = _with_name(lines[0], user_name, "en")

    out = []
    for raw in lines:
        safe = enforce_affirmation_style(sanitize(raw), "en")
        if safe and not _is_bad(safe, "en"):
            out.append(safe)
    return out


def _dedupe(items: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _postprocess(items: List[str], language: str, user_name: str) -> List[str]:
    out: List[str] = []
    for raw in items:
        value = enforce_affirmation_style(sanitize(raw), language)
        if not value:
            continue
        if _is_bad(value, language):
            continue
        out.append(value)

    unique = _dedupe(out)
    if user_name and unique:
        unique[0] = _with_name(unique[0], user_name, language)
    return unique


def _fallback(goals: List[GoalAnswer], language: str, user_name: str) -> List[str]:
    grouped = _group(goals)
    if not grouped:
        grouped = {"health": []}

    lines: List[str] = []
    for area, items in grouped.items():
        if language == "ru":
            lines.extend(_fallback_ru(area, items, user_name))
        else:
            lines.extend(_fallback_en(area, items, user_name))

    return _dedupe(lines)


def generate_affirmations(goals: List[GoalAnswer], language: str, tone: str, user_name: str = "") -> List[str]:
    grouped = _group(goals)
    area_count = max(1, len(grouped))
    min_count = area_count * 4
    max_count = area_count * 7

    fallback = _fallback(goals, language, user_name)

    provider = settings.llm_provider.lower().strip()
    llm_lines: List[str] = []

    try:
        if provider == "deepseek":
            llm_raw = generate_with_deepseek(goals, language, tone, user_name)
            llm_lines = _postprocess(llm_raw, language, user_name)
        elif provider == "gigachat":
            llm_raw = generate_with_gigachat(goals, language, tone, user_name)
            llm_lines = _postprocess(llm_raw, language, user_name)
        elif provider == "ollama":
            llm_raw = generate_with_ollama(goals, language, tone, user_name)
            llm_lines = _postprocess(llm_raw, language, user_name)
    except Exception:
        llm_lines = []

    merged = _dedupe(llm_lines + fallback)
    if len(merged) < min_count:
        merged.extend([line for line in fallback if line not in merged])

    return add_disclaimer(merged[:max_count], language)
