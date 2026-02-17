SAFE_BANNED = [
    "cure", "heal", "лечит", "вылечит", "гарантия", "guarantee",
]

DISCLAIMER_RU = "Это вдохновляющие утверждения. Они не являются медицинской рекомендацией."
DISCLAIMER_EN = "These affirmations are inspirational and not medical advice."


def sanitize(text: str) -> str:
    lowered = text.lower()
    if any(b in lowered for b in SAFE_BANNED):
        return ""
    return text


def enforce_affirmation_style(text: str, language: str) -> str:
    value = text.strip()
    if not value:
        return value
    value = value.replace("?", "").strip()
    if language == "ru":
        low = value.lower()
        if low.startswith("я хочу "):
            value = "Я выбираю " + value[7:].strip(" ,.-")
            low = value.lower()
        if low.startswith("я "):
            return "Я " + value[2:].strip(" ,.-")
        return "Я " + value[0].lower() + value[1:] if len(value) > 1 else "Я " + value.lower()
    low = value.lower()
    if low.startswith("i want "):
        value = "I choose " + value[7:].strip(" ,.-")
        low = value.lower()
    if low.startswith("i "):
        return value
    return "I " + value[0].lower() + value[1:] if len(value) > 1 else "I " + value.lower()


def add_disclaimer(items: list[str], language: str) -> list[str]:
    # Disclaimer is shown in UI, not as part of affirmation lines.
    return items
