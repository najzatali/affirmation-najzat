from __future__ import annotations

import re

SAFE_BANNED = [
    "cure",
    "лечит",
    "вылечит",
    "гарантия",
    "guarantee",
    "100%",
]

DISCLAIMER_RU = "Это вдохновляющие утверждения. Они не являются медицинской рекомендацией."
DISCLAIMER_EN = "These are inspirational affirmations and not medical advice."

NEGATIVE_PATTERNS_RU = [
    r"\bне\b",
    r"\bникогда\b",
    r"\bнет\b",
]
NEGATIVE_PATTERNS_EN = [
    r"\bnot\b",
    r"\bnever\b",
    r"\bno\b",
]


def sanitize(text: str) -> str:
    value = " ".join((text or "").strip().split())
    if not value:
        return ""
    lowered = value.lower()
    if any(bad in lowered for bad in SAFE_BANNED):
        return ""
    return value


def remove_negative_words(text: str, language: str) -> str:
    value = text
    patterns = NEGATIVE_PATTERNS_RU if language == "ru" else NEGATIVE_PATTERNS_EN
    for pattern in patterns:
        value = re.sub(pattern, "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s{2,}", " ", value).strip(" ,.;:-")
    return value


def enforce_affirmation_style(text: str, language: str) -> str:
    value = sanitize(text)
    if not value:
        return ""

    value = value.replace("?", "").strip(" .,!;:")
    value = remove_negative_words(value, language)
    if not value:
        return ""

    if language == "ru":
        low = value.lower()
        if low.startswith("я есть") or low.startswith("я имею"):
            return " ".join([part for part in value.split(" ") if part]).strip()
        if low.startswith("я "):
            return "Я есть " + value[2:].strip(" ,.;:-")
        return "Я есть " + value

    low = value.lower()
    if low.startswith("i am") or low.startswith("i have"):
        return " ".join([part for part in value.split(" ") if part]).strip()
    if low.startswith("i "):
        return "I am " + value[2:].strip(" ,.;:-")
    return "I am " + value


def add_disclaimer(items: list[str], language: str) -> list[str]:
    # Disclaimer should be rendered by UI as a footnote.
    return items
