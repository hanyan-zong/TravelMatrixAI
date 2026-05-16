from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


Platform = Literal[
    "xiaohongshu",
    "douyin",
    "wechat_channels",
    "toutiao",
    "weibo",
    "douban",
]


class TravelProduct(BaseModel):
    id: str
    name: str
    destination: str
    days: int
    target_audience: str
    reference_price: str
    selling_points: list[str]


class LoginRequest(BaseModel):
    account: str
    password: str


class UserProfile(BaseModel):
    id: str
    name: str
    role: str
    workspace: str


class LoginResponse(BaseModel):
    token: str
    user: UserProfile


class GeneratePostsRequest(BaseModel):
    product_id: str = Field(alias="productId")
    platforms: list[Platform]
    content_goal: str = Field(default="lead_generation", alias="contentGoal")
    target_audience: str | None = Field(default=None, alias="targetAudience")


class PostVariant(BaseModel):
    id: str
    platform: Platform
    title: str
    body: str
    hashtags: list[str]
    cover_text: str = Field(alias="coverText")
    risk_level: Literal["low", "medium", "high"] = Field(alias="riskLevel")
    status: str


class GeneratePostsResponse(BaseModel):
    draft_id: str = Field(alias="draftId")
    product: TravelProduct
    variants: list[PostVariant]


class PublishTask(BaseModel):
    id: str
    platform: Platform
    account_name: str = Field(alias="accountName")
    scheduled_at: datetime = Field(alias="scheduledAt")
    publish_method: Literal["api", "enterprise_api", "manual_assist"] = Field(alias="publishMethod")
    status: str


class MediaAsset(BaseModel):
    id: str
    type: Literal["image", "video", "audio", "document"]
    title: str
    destination: str | None = None
    scene: str | None = None
    license_status: str = Field(default="pending", alias="licenseStatus")
    tags: list[str] = []
    file_url: str = Field(alias="fileUrl")


class CreateMediaAssetRequest(BaseModel):
    type: Literal["image", "video", "audio", "document"]
    title: str
    destination: str | None = None
    scene: str | None = None
    license_status: str = Field(default="pending", alias="licenseStatus")
    tags: list[str] = []
    file_url: str = Field(alias="fileUrl")


class ComplianceRequest(BaseModel):
    platform: Platform
    title: str
    body: str
    asset_license_status: str = Field(default="approved", alias="assetLicenseStatus")


class ComplianceResponse(BaseModel):
    risk_level: Literal["low", "medium", "high"] = Field(alias="riskLevel")
    issues: list[str]
    suggestions: list[str]
    allow_publish: bool = Field(alias="allowPublish")
    allow_auto_publish: bool = Field(alias="allowAutoPublish")


class CreatePublishTaskRequest(BaseModel):
    variant_id: str = Field(alias="variantId")
    platform: Platform
    account_name: str = Field(alias="accountName")
    scheduled_at: datetime = Field(alias="scheduledAt")
    publish_method: Literal["api", "enterprise_api", "manual_assist"] = Field(
        default="manual_assist", alias="publishMethod"
    )


class PublishResultRequest(BaseModel):
    published_url: str | None = Field(default=None, alias="publishedUrl")
    status: str
    note: str | None = None


class MetricRequest(BaseModel):
    publish_task_id: str = Field(alias="publishTaskId")
    views: int = 0
    likes: int = 0
    saves: int = 0
    comments: int = 0
    shares: int = 0
    leads: int = 0
    conversions: int = 0


class AnalyticsOverview(BaseModel):
    total_views: int = Field(alias="totalViews")
    total_leads: int = Field(alias="totalLeads")
    total_conversions: int = Field(alias="totalConversions")
    best_platform: str = Field(alias="bestPlatform")
    recommendation: str


app = FastAPI(title="TravelMatrix AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
        "http://127.0.0.1:4180",
        "http://localhost:4180",
        "http://127.0.0.1:4181",
        "http://localhost:4181",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRODUCTS = [
    TravelProduct(
        id="bali-6d5n",
        name="巴厘岛 6 天 5 晚纯玩",
        destination="巴厘岛",
        days=6,
        target_audience="亲子、蜜月、第一次去海岛的客人",
        reference_price="5899 元起，以实际咨询为准",
        selling_points=["蓝梦岛出海", "乌布梯田", "海边酒店", "中文司导", "无购物纯玩"],
    ),
    TravelProduct(
        id="lombok-day-tour",
        name="龙目岛一日游系列",
        destination="龙目岛",
        days=1,
        target_audience="喜欢海岛、浮潜、轻户外的客人",
        reference_price="按线路咨询",
        selling_points=["粉红沙滩", "吉利群岛", "瀑布", "包车灵活", "中文服务"],
    ),
]

MEDIA_ASSETS: list[MediaAsset] = [
    MediaAsset(
        id="asset_bali_beach",
        type="image",
        title="巴厘岛海边酒店外景",
        destination="巴厘岛",
        scene="酒店",
        licenseStatus="approved",
        tags=["海边", "酒店", "度假"],
        fileUrl="/demo-assets/bali-beach.jpg",
    ),
    MediaAsset(
        id="asset_lombok_boat",
        type="video",
        title="龙目岛出海短视频",
        destination="龙目岛",
        scene="出海",
        licenseStatus="approved",
        tags=["出海", "浮潜", "短视频"],
        fileUrl="/demo-assets/lombok-boat.mp4",
    ),
]

PUBLISH_TASKS: list[PublishTask] = []
METRICS: list[MetricRequest] = []
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATE_FILE = DATA_DIR / "state.json"
DEMO_USER = UserProfile(id="user_demo_admin", name="运营管理员", role="admin", workspace="TravelMatrix Demo")
DEMO_TOKEN = "demo-token-travelmatrix"


PLATFORM_LABELS: dict[Platform, str] = {
    "xiaohongshu": "小红书",
    "douyin": "抖音",
    "wechat_channels": "视频号",
    "toutiao": "今日头条",
    "weibo": "微博",
    "douban": "豆瓣",
}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    # MVP demo auth. Replace with password hashing and JWT before production use.
    if not payload.account:
        payload.account = "demo"
    return LoginResponse(token=DEMO_TOKEN, user=DEMO_USER)


@app.get("/api/auth/me", response_model=UserProfile)
def me() -> UserProfile:
    return DEMO_USER


@app.get("/api/travel-products", response_model=list[TravelProduct])
def list_products() -> list[TravelProduct]:
    return PRODUCTS


@app.get("/api/media-assets", response_model=list[MediaAsset])
def list_media_assets() -> list[MediaAsset]:
    return MEDIA_ASSETS


@app.post("/api/media-assets", response_model=MediaAsset)
def create_media_asset(payload: CreateMediaAssetRequest) -> MediaAsset:
    asset = MediaAsset(id=f"asset_{uuid4().hex[:10]}", **payload.model_dump(by_alias=True))
    MEDIA_ASSETS.append(asset)
    save_state()
    return asset


@app.post("/api/ai/generate-posts", response_model=GeneratePostsResponse)
def generate_posts(payload: GeneratePostsRequest) -> GeneratePostsResponse:
    product = next((item for item in PRODUCTS if item.id == payload.product_id), PRODUCTS[0])
    variants = [build_variant(product, platform) for platform in payload.platforms]
    return GeneratePostsResponse(draftId=f"draft_{uuid4().hex[:10]}", product=product, variants=variants)


@app.get("/api/publish-tasks/calendar", response_model=list[PublishTask])
def calendar() -> list[PublishTask]:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    demo_tasks = [
        PublishTask(
            id="task_xhs_001",
            platform="xiaohongshu",
            accountName="亲子海岛账号",
            scheduledAt=now + timedelta(hours=2),
            publishMethod="manual_assist",
            status="manual_required",
        ),
        PublishTask(
            id="task_douyin_001",
            platform="douyin",
            accountName="东南亚短视频账号",
            scheduledAt=now + timedelta(hours=5),
            publishMethod="manual_assist",
            status="scheduled",
        ),
        PublishTask(
            id="task_weibo_001",
            platform="weibo",
            accountName="官方活动账号",
            scheduledAt=now + timedelta(hours=8),
            publishMethod="api",
            status="scheduled",
        ),
    ]
    return PUBLISH_TASKS + demo_tasks


@app.post("/api/ai/compliance-check", response_model=ComplianceResponse)
def compliance_check(payload: ComplianceRequest) -> ComplianceResponse:
    issues: list[str] = []
    suggestions: list[str] = []
    text = f"{payload.title}\n{payload.body}"
    blocked_words = ["保证", "最低价", "100%", "绝对安全", "全网最低"]

    for word in blocked_words:
        if word in text:
            issues.append(f"包含高风险表达：{word}")
            suggestions.append("删除绝对化或无法证明的承诺。")

    if payload.asset_license_status != "approved":
        issues.append("素材授权状态不是 approved")
        suggestions.append("请先确认素材版权和人物授权。")

    if "价格" in text and "以实际咨询为准" not in text:
        issues.append("价格表达缺少确认提示")
        suggestions.append("补充“以实际咨询为准”。")

    risk_level: Literal["low", "medium", "high"] = "low"
    if issues:
        risk_level = "high" if payload.asset_license_status != "approved" else "medium"

    return ComplianceResponse(
        riskLevel=risk_level,
        issues=issues,
        suggestions=suggestions,
        allowPublish=risk_level != "high",
        allowAutoPublish=risk_level == "low",
    )


@app.post("/api/publish-tasks", response_model=PublishTask)
def create_publish_task(payload: CreatePublishTaskRequest) -> PublishTask:
    task = PublishTask(
        id=f"task_{uuid4().hex[:10]}",
        platform=payload.platform,
        accountName=payload.account_name,
        scheduledAt=payload.scheduled_at,
        publishMethod=payload.publish_method,
        status="scheduled",
    )
    PUBLISH_TASKS.append(task)
    save_state()
    return task


@app.post("/api/publish-tasks/{task_id}/result", response_model=PublishTask)
def record_publish_result(task_id: str, payload: PublishResultRequest) -> PublishTask:
    task = next((item for item in PUBLISH_TASKS if item.id == task_id), None)
    if task is None:
        task = PublishTask(
            id=task_id,
            platform="weibo",
            accountName="手动补录账号",
            scheduledAt=datetime.now(timezone.utc),
            publishMethod="manual_assist",
            status=payload.status,
        )
        PUBLISH_TASKS.append(task)
    else:
        task.status = payload.status
    save_state()
    return task


@app.post("/api/metrics", response_model=MetricRequest)
def record_metrics(payload: MetricRequest) -> MetricRequest:
    METRICS.append(payload)
    save_state()
    return payload


@app.get("/api/analytics/overview", response_model=AnalyticsOverview)
def analytics_overview() -> AnalyticsOverview:
    total_views = sum(item.views for item in METRICS) or 12860
    total_leads = sum(item.leads for item in METRICS) or 42
    total_conversions = sum(item.conversions for item in METRICS) or 6
    return AnalyticsOverview(
        totalViews=total_views,
        totalLeads=total_leads,
        totalConversions=total_conversions,
        bestPlatform="小红书",
        recommendation="下周继续增加海岛亲子攻略内容，标题保留价格确认提示，短视频重点优化前三秒钩子。",
    )


def build_variant(product: TravelProduct, platform: Platform) -> PostVariant:
    label = PLATFORM_LABELS[platform]
    if platform == "xiaohongshu":
        title = f"第一次去{product.destination}，{product.days}天这样玩更省心"
        body = f"适合{product.target_audience}。亮点包括：{'、'.join(product.selling_points)}。参考价格 {product.reference_price}。"
        cover = f"{product.destination}{product.days}天攻略"
        risk = "medium"
    elif platform == "douyin":
        title = f"{product.destination}{product.days}天怎么玩才不踩坑？"
        body = "前三秒钩子：第一次去海岛，别把时间浪费在路上。镜头按酒店、出海、景点、咨询引导排列。"
        cover = f"{product.destination}避坑路线"
        risk = "low"
    elif platform == "wechat_channels":
        title = f"{product.name}行程参考"
        body = f"这条行程适合{product.target_audience}，节奏稳，适合公司官方账号介绍。"
        cover = f"{product.destination}纯玩参考"
        risk = "low"
    elif platform == "toutiao":
        title = f"{product.name}攻略：行程、费用和注意事项"
        body = "文章建议分为适合人群、每日安排、费用说明、注意事项和咨询入口，突出信息完整度。"
        cover = f"{product.destination}完整攻略"
        risk = "low"
    elif platform == "weibo":
        title = f"{product.destination}旅行行程参考"
        body = f"{product.name}适合想轻松规划的客人，重点体验：{'、'.join(product.selling_points[:3])}。"
        cover = f"{product.destination}出行灵感"
        risk = "low"
    else:
        title = f"第一次去{product.destination}，怎么安排比较舒服"
        body = "建议用经验分享角度说明行程节奏、预算咨询方式和避坑提醒，降低营销感。"
        cover = f"{product.destination}经验分享"
        risk = "medium"

    return PostVariant(
        id=f"variant_{platform}_{uuid4().hex[:8]}",
        platform=platform,
        title=title,
        body=body,
        hashtags=[label, product.destination, "旅行攻略"],
        coverText=cover,
        riskLevel=risk,
        status="draft",
    )


def load_state() -> None:
    if not STATE_FILE.exists():
        return

    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    MEDIA_ASSETS[:] = [MediaAsset.model_validate(item) for item in data.get("mediaAssets", [])] or MEDIA_ASSETS
    PUBLISH_TASKS[:] = [PublishTask.model_validate(item) for item in data.get("publishTasks", [])]
    METRICS[:] = [MetricRequest.model_validate(item) for item in data.get("metrics", [])]


def save_state() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "mediaAssets": [item.model_dump(mode="json", by_alias=True) for item in MEDIA_ASSETS],
        "publishTasks": [item.model_dump(mode="json", by_alias=True) for item in PUBLISH_TASKS],
        "metrics": [item.model_dump(mode="json", by_alias=True) for item in METRICS],
    }
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


load_state()
