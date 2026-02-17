from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_lesson_coach_next_step_returns_payload():
    payload = {
        "language": "ru",
        "module_id": "foundation-prompt-blueprint",
        "module_title": "Промпт по частям",
        "module_summary": "Роль, цель, контекст, ограничения, формат.",
        "practice_note": "Собрал промпт и сравнил две версии ответа для своей задачи.",
        "completed_tasks": ["task_prompt", "task_output"],
        "visited_segments": 6,
        "total_segments": 8,
        "profile": {
            "learner_type": "individual",
            "age_group": "young",
            "industry": "education",
            "role": "teacher",
            "level": "beginner",
            "format": "hybrid",
            "goals": ["quality", "training"],
        },
    }
    response = client.post("/api/coach/next-step", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("next_step"), str) and len(data["next_step"]) > 10
    assert isinstance(data.get("checkpoint"), str) and len(data["checkpoint"]) > 10
    assert isinstance(data.get("safety_note"), str) and len(data["safety_note"]) > 10
    assert "provider" in data


def test_lesson_coach_company_payload_has_team_guidance():
    payload = {
        "language": "ru",
        "module_id": "company-ai-rollout",
        "module_title": "Пакет внедрения AI",
        "module_summary": "Внедрение по шагам для команды.",
        "practice_note": "Собрал шаблон промпта и план внедрения по двум отделам.",
        "completed_tasks": ["task_prompt", "task_output", "task_check"],
        "visited_segments": 8,
        "total_segments": 10,
        "profile": {
            "learner_type": "company",
            "age_group": "adults",
            "industry": "services",
            "role": "manager",
            "level": "intermediate",
            "format": "hybrid",
            "goals": ["automation", "training"],
        },
    }
    response = client.post("/api/coach/next-step", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("company_step"), str) and len(data["company_step"]) > 10
    assert isinstance(data.get("company_kpi"), str) and len(data["company_kpi"]) > 10


def test_lesson_help_chat_returns_guidance():
    payload = {
        "language": "ru",
        "module_title": "База AI",
        "step_title": "Как выбрать инструмент",
        "user_question": "Я не понимаю, как правильно сформулировать запрос. Что именно писать первым?",
        "user_attempt": "Сделай мне что-нибудь полезное по теме.",
        "profile": {
            "learner_type": "individual",
            "age_group": "young",
            "industry": "education",
            "role": "teacher",
            "level": "beginner",
            "format": "hybrid",
            "goals": ["quality", "training"],
        },
    }
    response = client.post("/api/coach/help", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("answer"), str) and len(data["answer"]) > 10
    assert isinstance(data.get("what_wrong"), str) and len(data["what_wrong"]) > 5
    assert isinstance(data.get("how_fix"), str) and len(data["how_fix"]) > 10
