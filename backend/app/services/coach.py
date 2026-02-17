import base64
import json
import uuid

import httpx

from ..core.config import settings
from ..schemas import LessonCoachRequest, LessonCoachResponse, LessonHelpRequest, LessonHelpResponse


LEVEL_FOCUS_RU = {
    "beginner": "объясни максимально просто, шаги должны быть очень конкретными",
    "intermediate": "дай рабочий шаг с улучшением качества и одной итерацией",
    "advanced": "дай шаг с оптимизацией процесса и измеримой метрикой",
}

LEVEL_FOCUS_EN = {
    "beginner": "explain in very simple language with concrete actions",
    "intermediate": "provide one practical improvement iteration",
    "advanced": "provide one optimization step with measurable metric",
}


def _clean(text: str) -> str:
    return " ".join((text or "").split()).strip()


def _company_pack(payload: LessonCoachRequest) -> tuple[str, str]:
    lang = payload.language if payload.language in {"ru", "en"} else "ru"
    industry = payload.profile.industry or ("универсально" if lang == "ru" else "general")
    role = payload.profile.role or ("специалист" if lang == "ru" else "specialist")
    module_title = payload.module_title

    if lang == "ru":
        company_step = (
            f"Шаг для руководителя: назначь ответственного за внедрение модуля '{module_title}' в команде и "
            f"собери 1 общий шаблон промпта для отрасли {industry} и роли {role}. "
            "Проведи 15-минутный разбор результатов в конце дня."
        )
        company_kpi = (
            "KPI недели: время на задачу (до/после AI), доля задач без доработки, "
            "процент сотрудников, кто использовал шаблон минимум 3 раза."
        )
        return company_step, company_kpi

    company_step = (
        f"Manager action: assign one owner to roll out module '{module_title}' in the team and "
        f"create one shared prompt template for industry {industry} and role {role}. "
        "Run a 15-minute review at the end of day."
    )
    company_kpi = (
        "Weekly KPI: task cycle time (before/after AI), first-pass completion rate, "
        "and percentage of employees using the template at least 3 times."
    )
    return company_step, company_kpi


def _fallback(payload: LessonCoachRequest) -> LessonCoachResponse:
    lang = payload.language if payload.language in {"ru", "en"} else "ru"
    goals = ", ".join(payload.profile.goals[:3]) if payload.profile.goals else ("качество результата" if lang == "ru" else "quality")
    remaining_segments = max(0, int(payload.total_segments) - int(payload.visited_segments))
    tasks_count = len(payload.completed_tasks or [])
    practice = _clean(payload.practice_note)
    enough_practice = len(practice) >= 24

    if lang == "ru":
        role = payload.profile.role or "специалист"
        next_step = (
            f"Следующий шаг для роли {role}: открой новый чат и собери промпт по формуле "
            f"'Роль -> Цель -> Контекст -> Ограничения -> Формат -> Критерии качества' "
            f"под модуль '{payload.module_title}'. Сделай 2 версии ответа и выбери лучшую."
        )
        checkpoint = (
            f"Чекпоинт: закрыто задач {tasks_count}, осталось сегментов {remaining_segments}. "
            f"Фокус на цели: {goals}. {'Практика сохранена.' if enough_practice else 'Добавь практику не менее 24 символов.'}"
        )
        safety_note = (
            "Перед отправкой не включай пароли, персональные данные и закрытые документы. "
            "Критичные факты проверь по источнику."
        )
    else:
        role = payload.profile.role or "specialist"
        next_step = (
            f"Next step for role {role}: start a new chat and build a prompt using "
            f"'Role -> Goal -> Context -> Constraints -> Output -> Quality criteria' "
            f"for module '{payload.module_title}'. Generate two versions and keep the better one."
        )
        checkpoint = (
            f"Checkpoint: tasks done {tasks_count}, remaining segments {remaining_segments}. "
            f"Goal focus: {goals}. {'Practice saved.' if enough_practice else 'Add at least 24 characters in practice note.'}"
        )
        safety_note = (
            "Do not include passwords, personal data, or restricted internal documents. "
            "Verify high-impact facts with trusted sources."
        )

    company_step = None
    company_kpi = None
    if payload.profile.learner_type == "company":
        company_step, company_kpi = _company_pack(payload)

    return LessonCoachResponse(
        next_step=next_step,
        checkpoint=checkpoint,
        safety_note=safety_note,
        company_step=company_step,
        company_kpi=company_kpi,
        provider="fallback",
        fallback=True,
    )


def _prompt(payload: LessonCoachRequest) -> str:
    lang = payload.language if payload.language in {"ru", "en"} else "ru"
    level_focus = (LEVEL_FOCUS_RU if lang == "ru" else LEVEL_FOCUS_EN).get(payload.profile.level, "")

    profile_block = {
        "learner_type": payload.profile.learner_type,
        "age_group": payload.profile.age_group,
        "industry": payload.profile.industry,
        "role": payload.profile.role,
        "level": payload.profile.level,
        "format": payload.profile.format,
        "goals": payload.profile.goals,
    }
    lesson_block = {
        "module_id": payload.module_id,
        "module_title": payload.module_title,
        "module_summary": payload.module_summary,
        "practice_note": payload.practice_note,
        "completed_tasks": payload.completed_tasks,
        "visited_segments": payload.visited_segments,
        "total_segments": payload.total_segments,
    }

    if lang == "ru":
        extra_company = (
            "7) Если learner_type=company, добавь поля company_step и company_kpi.\n"
            "8) company_step: действие для руководителя/тимлида по внедрению в команду.\n"
            "9) company_kpi: короткий KPI-блок для контроля эффекта.\n"
        )
        return (
            "Ты AI-наставник в онлайн обучении по искусственному интеллекту.\n"
            "Дай JSON с полями next_step, checkpoint, safety_note. "
            "Для компаний дополнительно company_step и company_kpi.\n"
            "Требования:\n"
            "1) На русском, без воды, практично.\n"
            "2) next_step: одно конкретное действие прямо сейчас.\n"
            "3) checkpoint: как проверить, что действие выполнено.\n"
            "4) safety_note: одна рекомендация по безопасности данных или факт-чекингу.\n"
            "5) Учти роль, отрасль, возраст, уровень и формат.\n"
            f"6) Доп.фокус уровня: {level_focus}.\n"
            f"{extra_company}"
            "Ответ только JSON без markdown.\n"
            f"Профиль: {json.dumps(profile_block, ensure_ascii=False)}\n"
            f"Контекст урока: {json.dumps(lesson_block, ensure_ascii=False)}"
        )

    extra_company = (
        "7) If learner_type=company, also return company_step and company_kpi.\n"
        "8) company_step: one manager/team-lead action for rollout.\n"
        "9) company_kpi: a short KPI block to track impact.\n"
    )
    return (
        "You are an AI learning coach.\n"
        "Return JSON with next_step, checkpoint, safety_note. "
        "For companies also include company_step and company_kpi.\n"
        "Requirements:\n"
        "1) concise, practical, no fluff.\n"
        "2) next_step: one concrete action to do now.\n"
        "3) checkpoint: how to verify completion.\n"
        "4) safety_note: one data-safety or fact-check rule.\n"
        "5) Adapt to role, industry, age, level, and format.\n"
        f"6) Level focus: {level_focus}.\n"
        f"{extra_company}"
        "Output JSON only.\n"
        f"Profile: {json.dumps(profile_block, ensure_ascii=False)}\n"
        f"Lesson context: {json.dumps(lesson_block, ensure_ascii=False)}"
    )


def _parse_json_block(text: str) -> dict:
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Empty coach response")

    # Handle models that wrap JSON in code fences.
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
        raise ValueError("Coach response is not an object")
    return parsed


def _deepseek(prompt: str) -> str:
    if not settings.deepseek_api_key:
        raise RuntimeError("DeepSeek API key is not configured")
    url = f"{settings.deepseek_api_base.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.deepseek_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 450,
    }
    with httpx.Client(timeout=40.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def _ollama(prompt: str) -> str:
    url = f"{settings.ollama_api_base.rstrip('/')}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")


def _openai(prompt: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API key is not configured")
    url = f"{settings.openai_api_base.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openai_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 450,
        "response_format": {"type": "json_object"},
    }
    with httpx.Client(timeout=45.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def _gigachat_token() -> str:
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
        response = client.post(settings.gigachat_auth_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]


def _gigachat(prompt: str) -> str:
    token = _gigachat_token()
    url = f"{settings.gigachat_api_base.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.gigachat_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 500,
    }
    with httpx.Client(timeout=35.0, verify=settings.gigachat_verify_ssl) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def _run_provider(provider: str, prompt: str) -> str:
    if provider == "deepseek":
        return _deepseek(prompt)
    if provider == "openai":
        return _openai(prompt)
    if provider == "ollama":
        return _ollama(prompt)
    if provider == "gigachat":
        return _gigachat(prompt)
    raise RuntimeError(f"Unsupported provider: {provider}")


def generate_lesson_coach(payload: LessonCoachRequest) -> LessonCoachResponse:
    provider = (settings.llm_provider or "").lower()
    prompt = _prompt(payload)

    text = ""
    fallback = False
    try:
        text = _run_provider(provider, prompt)
    except Exception:
        fallback = True

    if fallback:
        return _fallback(payload)

    try:
        parsed = _parse_json_block(text)
        next_step = _clean(str(parsed.get("next_step", "")))
        checkpoint = _clean(str(parsed.get("checkpoint", "")))
        safety_note = _clean(str(parsed.get("safety_note", "")))
        if not next_step or not checkpoint or not safety_note:
            raise ValueError("Missing fields")
        company_step = _clean(str(parsed.get("company_step", ""))) or None
        company_kpi = _clean(str(parsed.get("company_kpi", ""))) or None

        if payload.profile.learner_type == "company" and (not company_step or not company_kpi):
            fb_step, fb_kpi = _company_pack(payload)
            company_step = company_step or fb_step
            company_kpi = company_kpi or fb_kpi

        return LessonCoachResponse(
            next_step=next_step,
            checkpoint=checkpoint,
            safety_note=safety_note,
            company_step=company_step,
            company_kpi=company_kpi,
            provider=provider,
            fallback=False,
        )
    except Exception:
        fb = _fallback(payload)
        fb.provider = provider or "fallback"
        fb.fallback = True
        return fb


def _help_prompt(payload: LessonHelpRequest) -> str:
    lang = payload.language if payload.language in {"ru", "en"} else "ru"
    profile_block = {
        "industry": payload.profile.industry,
        "role": payload.profile.role,
        "level": payload.profile.level,
        "goals": payload.profile.goals,
    }

    if lang == "ru":
        return (
            "Ты дружелюбный наставник в AI-обучении.\n"
            "Верни СТРОГО JSON с полями answer, what_wrong, how_fix.\n"
            "Правила:\n"
            "1) Пиши очень просто, без сложных терминов.\n"
            "2) answer: прямой ответ на вопрос ученика в 2-4 предложениях.\n"
            "3) what_wrong: где вероятная ошибка ученика (1-2 предложения).\n"
            "4) how_fix: что сделать прямо сейчас (пошагово, 2-4 шага).\n"
            "5) Не ругай, объясняй спокойно и по делу.\n"
            f"Модуль: {payload.module_title}\n"
            f"Текущий шаг: {payload.step_title}\n"
            f"Вопрос ученика: {payload.user_question}\n"
            f"Ответ/попытка ученика: {payload.user_attempt or 'не указана'}\n"
            f"Профиль: {json.dumps(profile_block, ensure_ascii=False)}"
        )

    return (
        "You are a friendly AI learning tutor.\n"
        "Return STRICT JSON with fields answer, what_wrong, how_fix.\n"
        "Rules:\n"
        "1) Use plain language.\n"
        "2) answer: direct response in 2-4 sentences.\n"
        "3) what_wrong: likely learner mistake in 1-2 sentences.\n"
        "4) how_fix: immediate fix steps (2-4 steps).\n"
        "5) Correct gently, no harsh tone.\n"
        f"Module: {payload.module_title}\n"
        f"Current step: {payload.step_title}\n"
        f"Learner question: {payload.user_question}\n"
        f"Learner attempt: {payload.user_attempt or 'not provided'}\n"
        f"Profile: {json.dumps(profile_block, ensure_ascii=False)}"
    )


def _help_fallback(payload: LessonHelpRequest) -> LessonHelpResponse:
    lang = payload.language if payload.language in {"ru", "en"} else "ru"
    attempt = _clean(payload.user_attempt)

    if lang == "ru":
        answer = (
            "Смотри проще: сначала формулируй цель одним предложением, затем укажи формат результата и ограничения. "
            "После этого отправь запрос и сравни ответ по точности и полезности."
        )
        what_wrong = (
            "Похоже, в попытке не хватает конкретики: не до конца видно цель или критерий качества."
            if len(attempt) < 28
            else "Похоже, ошибка в размытой формулировке запроса: мало ограничений и ожидаемого формата."
        )
        how_fix = (
            "1) Перепиши цель в 1 строку.\n"
            "2) Добавь формат ответа (список/таблица).\n"
            "3) Добавь 1-2 ограничения (длина, стиль, запреты).\n"
            "4) Повтори запрос и проверь результат по чеклисту."
        )
        return LessonHelpResponse(
            answer=answer,
            what_wrong=what_wrong,
            how_fix=how_fix,
            provider="fallback",
            fallback=True,
        )

    answer = (
        "Keep it simple: define one clear goal, then output format, then constraints. "
        "Send the prompt and review response for usefulness and accuracy."
    )
    what_wrong = (
        "Your attempt likely misses concrete goal or quality criteria."
        if len(attempt) < 28
        else "Your prompt is likely too broad and lacks output constraints."
    )
    how_fix = (
        "1) Rewrite goal in one sentence.\n"
        "2) Add output format (list/table).\n"
        "3) Add 1-2 constraints (length, style, limits).\n"
        "4) Run again and compare output quality."
    )
    return LessonHelpResponse(
        answer=answer,
        what_wrong=what_wrong,
        how_fix=how_fix,
        provider="fallback",
        fallback=True,
    )


def generate_lesson_help(payload: LessonHelpRequest) -> LessonHelpResponse:
    provider = (settings.llm_provider or "").lower()
    prompt = _help_prompt(payload)

    text = ""
    fallback = False
    try:
        text = _run_provider(provider, prompt)
    except Exception:
        fallback = True

    if fallback:
        return _help_fallback(payload)

    try:
        parsed = _parse_json_block(text)
        answer = _clean(str(parsed.get("answer", "")))
        what_wrong = _clean(str(parsed.get("what_wrong", "")))
        how_fix = _clean(str(parsed.get("how_fix", "")))
        if not answer or not what_wrong or not how_fix:
            raise ValueError("Missing fields")
        return LessonHelpResponse(
            answer=answer,
            what_wrong=what_wrong,
            how_fix=how_fix,
            provider=provider,
            fallback=False,
        )
    except Exception:
        fb = _help_fallback(payload)
        fb.provider = provider or "fallback"
        fb.fallback = True
        return fb
