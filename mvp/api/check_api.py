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

    ip_profiles = client.get("/api/ip-profiles")
    assert ip_profiles.status_code == 200, ip_profiles.text
    assert len(ip_profiles.json()) >= 1

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

    creative = client.post(
        "/api/ai/generate-creative-package",
        json={
            "productId": "bali-6d5n",
            "platform": "douyin",
            "objective": "短视频引流",
            "durationSeconds": 30,
        },
    )
    assert creative.status_code == 200, creative.text
    assert len(creative.json()["storyboard"]) >= 4
    assert len(creative.json()["imagePrompts"]) >= 1

    talking_video = client.post(
        "/api/ai/generate-talking-video",
        json={
            "productId": "bali-6d5n",
            "ipProfileId": "travel_consultant",
            "platform": "douyin",
            "topic": "第一次去巴厘岛避坑",
            "durationSeconds": 45,
        },
    )
    assert talking_video.status_code == 200, talking_video.text
    assert len(talking_video.json()["teleprompter"]) >= 3
    assert len(talking_video.json()["viralStructure"]) >= 3

    reference_analysis = client.post(
        "/api/ai/analyze-talking-reference",
        json={
            "productId": "bali-6d5n",
            "ipProfileId": "travel_consultant",
            "platform": "douyin",
            "topic": "参考爆款结构改写",
            "referenceText": "第一次去海岛千万别只看价格？很多人踩坑都是因为行程顺序排错，先看酒店位置，再看出海天气，最后再看服务。",
        },
    )
    assert reference_analysis.status_code == 200, reference_analysis.text
    assert reference_analysis.json()["hookType"]
    assert len(reference_analysis.json()["structure"]) >= 3
    assert len(reference_analysis.json()["rewrittenPlan"]["teleprompter"]) >= 3

    batch_talking = client.post(
        "/api/ai/batch-talking-videos",
        json={
            "productId": "bali-6d5n",
            "ipProfileId": "travel_consultant",
            "platform": "douyin",
            "count": 5,
            "angles": ["第一次出行避坑", "预算和价格说明", "酒店位置怎么选"],
        },
    )
    assert batch_talking.status_code == 200, batch_talking.text
    assert len(batch_talking.json()["items"]) == 5
    assert batch_talking.json()["items"][0]["teleprompter"]

    saved_draft = client.post(
        "/api/creative-drafts",
        json={"package": creative.json()},
    )
    assert saved_draft.status_code == 200, saved_draft.text
    draft_id = saved_draft.json()["id"]
    assert saved_draft.json()["status"] == "draft"

    drafts = client.get("/api/creative-drafts")
    assert drafts.status_code == 200, drafts.text
    assert any(item["id"] == draft_id for item in drafts.json())

    review_item = client.post(f"/api/creative-drafts/{draft_id}/submit-review")
    assert review_item.status_code == 200, review_item.text
    assert review_item.json()["status"] == "pending"

    review_queue = client.get("/api/review-queue")
    assert review_queue.status_code == 200, review_queue.text
    assert any(item["draftId"] == draft_id for item in review_queue.json())

    review_decision = client.post(
        f"/api/review-items/{review_item.json()['id']}/decision",
        json={"decision": "approved", "note": "测试通过", "reviewer": "API 检查"},
    )
    assert review_decision.status_code == 200, review_decision.text
    assert review_decision.json()["status"] == "approved"

    publish_package = client.get(f"/api/creative-drafts/{draft_id}/publish-package")
    assert publish_package.status_code == 200, publish_package.text
    assert publish_package.json()["copy"]
    assert publish_package.json()["assetChecklist"]
    assert publish_package.json()["operatorChecklist"]
    assert publish_package.json()["platformAdaptation"]
    assert publish_package.json()["finalStatus"] in {"needs_confirmation", "confirmed"}

    publish_confirmation = client.post(
        f"/api/creative-drafts/{draft_id}/publish-package/confirm",
        json={
            "operator": "API 检查",
            "checklist": publish_package.json()["operatorChecklist"][:3],
            "note": "发布包确认测试",
        },
    )
    assert publish_confirmation.status_code == 200, publish_confirmation.text
    assert publish_confirmation.json()["draftId"] == draft_id

    publish_confirmations = client.get(
        f"/api/creative-drafts/{draft_id}/publish-package/confirmations"
    )
    assert publish_confirmations.status_code == 200, publish_confirmations.text
    assert len(publish_confirmations.json()) >= 1

    publish_task = client.post(
        f"/api/creative-drafts/{draft_id}/publish-task",
        json={
            "accountName": "API 检查账号",
            "scheduledAt": "2026-05-22T10:00:00+00:00",
            "publishMethod": "manual_assist",
        },
    )
    assert publish_task.status_code == 200, publish_task.text
    publish_task_id = publish_task.json()["id"]
    assert publish_task.json()["draftId"] == draft_id
    assert publish_task.json()["packageTitle"]

    publish_result = client.post(
        f"/api/publish-tasks/{publish_task_id}/result",
        json={
            "publishedUrl": "https://example.com/published/travel-post",
            "status": "published",
            "note": "发布结果回填测试",
        },
    )
    assert publish_result.status_code == 200, publish_result.text
    assert publish_result.json()["status"] == "published"
    assert publish_result.json()["publishedUrl"]

    metric = client.post(
        "/api/metrics",
        json={
            "publishTaskId": publish_task_id,
            "views": 1200,
            "likes": 80,
            "saves": 30,
            "comments": 12,
            "shares": 6,
            "leads": 4,
            "conversions": 1,
        },
    )
    assert metric.status_code == 200, metric.text
    assert metric.json()["leads"] == 4

    created_asset = client.post(
        "/api/media-assets",
        json={
            "type": "image",
            "title": "测试授权封面图",
            "destination": "巴厘岛",
            "scene": "封面",
            "licenseStatus": "approved",
            "consentStatus": "not_applicable",
            "usageScope": ["商业推广", "小红书", "抖音"],
            "source": "测试素材库",
            "owner": "TravelMatrix",
            "tags": ["封面", "授权"],
            "fileUrl": "/demo-assets/test-cover.jpg",
        },
    )
    assert created_asset.status_code == 200, created_asset.text
    asset_id = created_asset.json()["id"]

    asset_summary = client.get("/api/media-assets/compliance-summary")
    assert asset_summary.status_code == 200, asset_summary.text
    assert asset_summary.json()["totalAssets"] >= 1

    asset_usage = client.post(
        f"/api/media-assets/{asset_id}/usage",
        json={"draftId": draft_id, "usage": "cover", "note": "用于测试发布包封面"},
    )
    assert asset_usage.status_code == 200, asset_usage.text
    assert asset_usage.json()["assetId"] == asset_id

    asset_usage_list = client.get(f"/api/media-assets/{asset_id}/usage")
    assert asset_usage_list.status_code == 200, asset_usage_list.text
    assert len(asset_usage_list.json()) >= 1

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
