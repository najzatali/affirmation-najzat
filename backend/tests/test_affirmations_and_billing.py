from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_generate_affirmations_returns_required_style():
    payload = {
        "language": "ru",
        "tone": "calm",
        "goals": [
            {"area": "money", "key": "goal_real_desire", "answer": "стабильный доход 500000 рублей"},
            {"area": "money", "key": "goal_feeling", "answer": "уверенность и легкость"},
            {"area": "money", "key": "reality_current", "answer": "ежедневно планирую продажи"},
            {"area": "money", "key": "belief_why_not", "answer": "думал что не справлюсь"},
            {"area": "money", "key": "faith_possible", "answer": "7"},
            {"area": "money", "key": "faith_worthy", "answer": "7"},
        ],
    }

    response = client.post("/api/affirmations/generate", json=payload)
    assert response.status_code == 200

    lines = response.json()["affirmations"]
    assert len(lines) >= 5
    for line in lines:
        low = line.lower()
        assert low.startswith("я есть") or low.startswith("я имею")
        assert "?" not in line


def test_billing_packages_contains_demo_and_paid_options():
    response = client.get("/api/billing/packages")
    assert response.status_code == 200

    items = response.json()
    durations = {item["duration_sec"] for item in items}
    assert 30 in durations
    assert 120 in durations
    assert 300 in durations


def test_local_purchase_flow_for_paid_package():
    response = client.post(
        "/api/billing/purchases",
        json={
            "duration_sec": 120,
            "success_url": "http://localhost:3000/billing/success",
            "cancel_url": "http://localhost:3000/billing/cancel",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["duration_sec"] == 120
    assert data["status"] in {"paid", "pending"}
    assert data["price_rub"] == 190
