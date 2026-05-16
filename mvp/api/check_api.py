from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)

    health = client.get("/api/health")
    assert health.status_code == 200, health.text
    assert health.json()["status"] == "ok"

    login = client.post("/api/auth/login", json={"account": "demo", "password": "demo"})
    assert login.status_code == 200, login.text
    assert login.json()["token"]

    me = client.get("/api/auth/me")
    assert me.status_code == 200, me.text
    assert me.json()["role"] == "admin"

    products = client.get("/api/travel-products")
    assert products.status_code == 200, products.text
    assert len(products.json()) >= 1

    generated = client.post(
        "/api/ai/generate-posts",
        json={
            "productId": "bali-6d5n",
            "platforms": ["xiaohongshu", "douyin", "wechat_channels"],
            "contentGoal": "lead_generation",
        },
    )
    assert generated.status_code == 200, generated.text
    assert len(generated.json()["variants"]) == 3

    compliance = client.post(
        "/api/ai/compliance-check",
        json={
            "platform": "xiaohongshu",
            "title": "巴厘岛最低价",
            "body": "保证满意",
            "assetLicenseStatus": "pending",
        },
    )
    assert compliance.status_code == 200, compliance.text
    assert compliance.json()["riskLevel"] == "high"
    assert compliance.json()["allowPublish"] is False

    calendar = client.get("/api/publish-tasks/calendar")
    assert calendar.status_code == 200, calendar.text
    assert len(calendar.json()) >= 1

    analytics = client.get("/api/analytics/overview")
    assert analytics.status_code == 200, analytics.text
    assert analytics.json()["totalLeads"] >= 0

    print("API checks passed")


if __name__ == "__main__":
    main()
