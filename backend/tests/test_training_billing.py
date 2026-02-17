from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_training_plans_contains_expected_tiers():
    response = client.get("/api/billing/training-plans")
    assert response.status_code == 200

    payload = response.json()
    codes = {item["code"] for item in payload}
    assert "individual" in codes
    assert "team_5" in codes
    assert "team_10" in codes
    assert "team_50" in codes
    assert "team_100" in codes


def test_create_training_order_local_provider():
    response = client.post(
        "/api/billing/training-orders",
        json={
            "plan_code": "team_5",
            "seats": 4,
            "company_name": "Test Team",
            "success_url": "http://localhost:3000/billing/success",
            "cancel_url": "http://localhost:3000/billing/cancel",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["plan_code"] == "team_5"
    assert payload["price_rub"] == 10000
    assert payload["status"] in {"paid", "pending"}
