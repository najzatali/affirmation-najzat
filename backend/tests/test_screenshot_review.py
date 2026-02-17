from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_verify_screenshot_fallback_response_shape():
    file_bytes = b"\x89PNG\r\n\x1a\n" + b"0" * 20000
    response = client.post(
        "/api/coach/verify-screenshot",
        data={
            "language": "ru",
            "module_title": "Базовый модуль",
            "mission_title": "Сделать первый запрос в AI",
            "learner_note": "Я зарегистрировался в сервисе и отправил первый структурный промпт.",
            "required_checks": '["Открыт AI-сервис","Есть введенный запрос","Есть результат"]',
        },
        files={"screenshot": ("proof.png", file_bytes, "image/png")},
    )

    assert response.status_code == 200
    data = response.json()
    assert "passed" in data
    assert "score" in data
    assert "summary" in data
    assert "found" in data
    assert "missing" in data
    assert "next_action" in data
    assert "provider" in data
    assert "fallback" in data
    assert isinstance(data["score"], int)
