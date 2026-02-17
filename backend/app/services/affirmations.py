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
    "money": "finances",
    "health": "health",
    "relationships": "relationships",
    "career": "career",
    "body": "body",
    "sleep": "sleep",
}

AREA_DEFAULTS_RU = {
    "money": {"result": "стабильный доход и финансовая свобода", "feeling": "спокойствие и уверенность", "action": "разумные финансовые решения"},
    "health": {"result": "сильное и выносливое здоровье", "feeling": "легкость и жизненная энергия", "action": "забота о теле каждый день"},
    "relationships": {"result": "теплые и зрелые отношения", "feeling": "любовь и уважение", "action": "честный и открытый диалог"},
    "career": {"result": "сильная профессиональная позиция", "feeling": "ясность и уверенность", "action": "дисциплина и фокус на приоритетах"},
    "body": {"result": "подтянутое и сильное тело", "feeling": "легкость и уверенность в себе", "action": "регулярное движение и восстановление"},
    "sleep": {"result": "глубокий и восстанавливающий сон", "feeling": "внутренний покой", "action": "стабильный режим отдыха"},
}

AREA_DEFAULTS_EN = {
    "money": {"result": "steady income and financial freedom", "feeling": "calm confidence", "action": "wise financial decisions"},
    "health": {"result": "strong and resilient health", "feeling": "lightness and vital energy", "action": "daily care for my body"},
    "relationships": {"result": "warm and mature relationships", "feeling": "love and respect", "action": "honest and open communication"},
    "career": {"result": "a strong professional position", "feeling": "clarity and confidence", "action": "discipline and focus on priorities"},
    "body": {"result": "a fit and strong body", "feeling": "lightness and self-confidence", "action": "regular movement and recovery"},
    "sleep": {"result": "deep restorative sleep", "feeling": "inner calm", "action": "a steady rest routine"},
}

WEAK_WORDS_RU = {"классно", "классные", "хорошо", "нормально", "ок", "ok", "не знаю"}
WEAK_WORDS_EN = {"good", "fine", "ok", "nice", "great", "i don't know", "dont know"}

BAD_PREFIXES_RU = ("какой ", "какие ", "как ", "почему ", "что ")
BAD_PREFIXES_EN = ("what ", "why ", "how ", "which ", "where ")

RU_NEGATIVE_PATTERNS = [
    "я хочу ",
    "хочу ",
    "мне нужно ",
    "я бы хотел ",
    "я бы хотела ",
]
EN_NEGATIVE_PATTERNS = ["i want ", "i need ", "i would like "]


def _clean_text(text: str) -> str:
    return " ".join((text or "").strip().split())


def _group_goals(goals: List[GoalAnswer]) -> Dict[str, List[GoalAnswer]]:
    grouped: Dict[str, List[GoalAnswer]] = defaultdict(list)
    for g in goals:
        grouped[g.area].append(g)
    return grouped


def _answer_by_key(items: List[GoalAnswer], key: str) -> str:
    for item in items:
        if (item.key or "").strip() == key:
            return _clean_text(item.answer)
    return ""


def _is_weak(text: str, language: str) -> bool:
    value = _clean_text(text).lower()
    if not value or len(value) < 5:
        return True
    words = set(value.replace(",", " ").split())
    weak = WEAK_WORDS_RU if language == "ru" else WEAK_WORDS_EN
    return words.issubset(weak)


def _normalize_fragment(text: str, language: str) -> str:
    value = _clean_text(text)
    if not value:
        return ""
    low = value.lower()
    patterns = RU_NEGATIVE_PATTERNS if language == "ru" else EN_NEGATIVE_PATTERNS
    for prefix in patterns:
        if low.startswith(prefix):
            value = value[len(prefix) :]
            break
    value = value.strip(" .,!?:;")
    # A tiny guard against raw copied prompt text.
    value = value.replace("в сфере", "").replace("in area", "").strip()
    return _clean_text(value)


def _safe_line(line: str, language: str) -> str:
    prepared = sanitize(_clean_text(line))
    if not prepared:
        return ""
    prepared = prepared.replace("?", "").strip()
    return enforce_affirmation_style(prepared, language)


def _faith_score(items: List[GoalAnswer]) -> float:
    scores = []
    for key in ("faith_possible", "faith_worthy"):
        raw = _answer_by_key(items, key)
        digits = "".join(ch for ch in raw if ch.isdigit())
        if digits:
            val = int(digits)
            if 1 <= val <= 10:
                scores.append(val)
    if not scores:
        return 7.0
    return sum(scores) / len(scores)


def _first_non_weak(values: Iterable[str], language: str, fallback: str) -> str:
    for value in values:
        clean = _normalize_fragment(value, language)
        if not _is_weak(clean, language):
            return clean
    return fallback


def _area_label(area: str, language: str) -> str:
    return (AREA_LABELS_RU if language == "ru" else AREA_LABELS_EN).get(area, "жизнь" if language == "ru" else "life")


def _area_defaults(area: str, language: str) -> dict:
    defaults = AREA_DEFAULTS_RU if language == "ru" else AREA_DEFAULTS_EN
    return defaults.get(area, defaults["health" if language == "ru" else "health"])


def _area_rule_based(area: str, items: List[GoalAnswer], language: str) -> List[str]:
    defaults = _area_defaults(area, language)
    area_label = _area_label(area, language)

    result = _first_non_weak(
        [
            _answer_by_key(items, "goal_real_desire"),
            _answer_by_key(items, "goal_life_change"),
            _answer_by_key(items, "goal_why"),
        ],
        language,
        defaults["result"],
    )
    feeling = _first_non_weak(
        [
            _answer_by_key(items, "goal_feeling"),
            _answer_by_key(items, "reality_fear"),
            _answer_by_key(items, "reality_pain"),
        ],
        language,
        defaults["feeling"],
    )
    action = _first_non_weak(
        [
            _answer_by_key(items, "reality_current"),
            _answer_by_key(items, "reality_pattern"),
            _answer_by_key(items, "belief_self_view"),
        ],
        language,
        defaults["action"],
    )
    blocker = _first_non_weak(
        [
            _answer_by_key(items, "belief_why_not"),
            _answer_by_key(items, "belief_auto_thought"),
            _answer_by_key(items, "belief_childhood"),
        ],
        language,
        defaults["action"],
    )

    soft_mode = _faith_score(items) < 5

    if language == "ru":
        if soft_mode:
            lines = [
                f"Я есть человек, который мягко открывается росту в сфере {area_label}.",
                f"Я имею право двигаться к результату: {result}.",
                f"Я есть спокойствие и уважение к себе в ежедневных шагах.",
                f"Я имею устойчивый фокус на действиях: {action}.",
                f"Я есть внутренняя опора, которая растворяет старый сценарий: {blocker}.",
                f"Я имею все больше ощущение, что {feeling}.",
            ]
        else:
            lines = [
                f"Я есть человек, который уже живет в состоянии: {result}.",
                f"Я имею ясный фокус и ежедневные действия: {action}.",
                f"Я есть спокойствие, сила и уверенность в теме {area_label}.",
                f"Я имею зрелые решения и устойчивый прогресс в каждом дне.",
                f"Я есть новая внутренняя опора, которая заменяет старый сценарий: {blocker}.",
                f"Я имею живое ощущение, что {feeling}.",
            ]
    else:
        if soft_mode:
            lines = [
                f"I am a person who gently opens up to growth in {area_label}.",
                f"I have the right to move toward this result: {result}.",
                "I am calm and respectful toward myself in daily steps.",
                f"I have stable focus on actions: {action}.",
                f"I am inner support that dissolves the old pattern: {blocker}.",
                f"I have a growing feeling of {feeling}.",
            ]
        else:
            lines = [
                f"I am a person who already lives in this state: {result}.",
                f"I have clear focus and daily actions: {action}.",
                f"I am calm strength and confidence in {area_label}.",
                "I have mature decisions and steady progress every day.",
                f"I am a new inner foundation replacing the old pattern: {blocker}.",
                f"I have a vivid feeling of {feeling}.",
            ]

    output = []
    for line in lines:
        safe = _safe_line(line, language)
        if safe:
            output.append(safe)
    return output


def _is_bad_generated_line(line: str, language: str) -> bool:
    low = line.lower().strip()
    if not low:
        return True
    if "?" in low:
        return True
    if language == "ru" and " не " in f" {low} ":
        return True
    if language == "en" and " not " in f" {low} ":
        return True
    prefixes = BAD_PREFIXES_RU if language == "ru" else BAD_PREFIXES_EN
    if any(low.startswith(p) for p in prefixes):
        return True
    return False


def _postprocess_generated(items: List[str], language: str) -> List[str]:
    out = []
    for raw in items:
        line = _safe_line(raw, language)
        if not line:
            continue
        if _is_bad_generated_line(line, language):
            continue
        out.append(line)
    return out


def _dedupe(items: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for line in items:
        key = line.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(line)
    return out


def _rule_based_affirmations(goals: List[GoalAnswer], language: str) -> List[str]:
    grouped = _group_goals(goals)
    if not grouped:
        grouped = {"health": []}
    all_lines: List[str] = []
    for area, items in grouped.items():
        all_lines.extend(_area_rule_based(area, items, language))
    return _dedupe(all_lines)


def generate_affirmations(goals: List[GoalAnswer], language: str, tone: str) -> List[str]:
    grouped = _group_goals(goals)
    areas_count = max(1, len(grouped))
    min_count = areas_count * 3
    max_count = areas_count * 7

    fallback_items = _rule_based_affirmations(goals, language)
    provider = settings.llm_provider.lower()
    llm_items: List[str] = []

    if provider == "deepseek":
        try:
            llm_items = _postprocess_generated(generate_with_deepseek(goals, language, tone), language)
        except Exception:
            llm_items = []
    elif provider == "gigachat":
        try:
            llm_items = _postprocess_generated(generate_with_gigachat(goals, language, tone), language)
        except Exception:
            llm_items = []
    elif provider == "ollama":
        try:
            llm_items = _postprocess_generated(generate_with_ollama(goals, language, tone), language)
        except Exception:
            llm_items = []

    if len(llm_items) >= min_count:
        items = _dedupe(llm_items)[:max_count]
    else:
        items = fallback_items

    if len(items) < min_count:
        for line in fallback_items:
            if line not in items:
                items.append(line)
            if len(items) >= min_count:
                break

    return add_disclaimer(items[:max_count], language)
