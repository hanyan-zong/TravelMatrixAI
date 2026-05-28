from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
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


class IpProfile(BaseModel):
    id: str
    name: str
    persona: str
    audience: str
    tone: str
    signature: str
    prohibited_claims: list[str] = Field(alias="prohibitedClaims")


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


class GenerateCreativePackageRequest(BaseModel):
    product_id: str = Field(alias="productId")
    platform: Platform = "douyin"
    objective: str = "短视频引流"
    duration_seconds: int = Field(default=30, ge=15, le=90, alias="durationSeconds")


class GenerateTalkingVideoRequest(BaseModel):
    product_id: str = Field(alias="productId")
    ip_profile_id: str = Field(default="travel_consultant", alias="ipProfileId")
    platform: Platform = "douyin"
    topic: str = "第一次出行避坑"
    reference_hook: str | None = Field(default=None, alias="referenceHook")
    duration_seconds: int = Field(default=45, ge=20, le=120, alias="durationSeconds")


class AnalyzeTalkingReferenceRequest(BaseModel):
    product_id: str = Field(alias="productId")
    ip_profile_id: str = Field(default="travel_consultant", alias="ipProfileId")
    platform: Platform = "douyin"
    reference_text: str = Field(alias="referenceText", min_length=10)
    topic: str = "参考爆款结构改写"


class BatchTalkingVideoRequest(BaseModel):
    product_id: str = Field(alias="productId")
    ip_profile_id: str = Field(default="travel_consultant", alias="ipProfileId")
    platform: Platform = "douyin"
    count: int = Field(default=10, ge=3, le=20)
    angles: list[str] = Field(default_factory=list)


class BatchTalkingVideoResponse(BaseModel):
    batch_id: str = Field(alias="batchId")
    product: TravelProduct
    ip_profile: IpProfile = Field(alias="ipProfile")
    platform: Platform
    items: list[TalkingVideoPlan]
    production_notes: list[str] = Field(alias="productionNotes")


class TalkingReferenceAnalysis(BaseModel):
    id: str
    platform: Platform
    topic: str
    hook_type: str = Field(alias="hookType")
    structure: list[str]
    rhythm_notes: list[str] = Field(alias="rhythmNotes")
    reusable_patterns: list[str] = Field(alias="reusablePatterns")
    originality_warnings: list[str] = Field(alias="originalityWarnings")
    rewritten_plan: TalkingVideoPlan = Field(alias="rewrittenPlan")


class TalkingVideoPlan(BaseModel):
    id: str
    product: TravelProduct
    ip_profile: IpProfile = Field(alias="ipProfile")
    platform: Platform
    topic: str
    title_options: list[str] = Field(alias="titleOptions")
    viral_structure: list[str] = Field(alias="viralStructure")
    teleprompter: list[str]
    script: str
    shot_plan: list[StoryboardScene] = Field(alias="shotPlan")
    cover_text: str = Field(alias="coverText")
    call_to_action: str = Field(alias="callToAction")
    compliance_notes: list[str] = Field(alias="complianceNotes")


class StoryboardScene(BaseModel):
    order: int
    shot: str
    visual_prompt: str = Field(alias="visualPrompt")
    voiceover: str
    subtitle: str
    asset_hint: str = Field(alias="assetHint")


class CreativePackage(BaseModel):
    id: str
    product: TravelProduct
    platform: Platform
    objective: str
    hook: str
    cover_title: str = Field(alias="coverTitle")
    video_script: str = Field(alias="videoScript")
    image_prompts: list[str] = Field(alias="imagePrompts")
    advertorial: str
    storyboard: list[StoryboardScene]
    compliance_notes: list[str] = Field(alias="complianceNotes")


class CreativeDraft(BaseModel):
    id: str
    title: str
    package: CreativePackage
    status: Literal["draft", "pending_review", "approved", "rejected"]
    review_note: str | None = Field(default=None, alias="reviewNote")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class SaveCreativeDraftRequest(BaseModel):
    package: CreativePackage


class ReviewItem(BaseModel):
    id: str
    draft_id: str = Field(alias="draftId")
    title: str
    platform: Platform
    status: Literal["pending", "approved", "rejected"]
    submitted_at: datetime = Field(alias="submittedAt")
    reviewed_at: datetime | None = Field(default=None, alias="reviewedAt")
    reviewer: str | None = None
    note: str | None = None


class ReviewDecisionRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    note: str | None = None
    reviewer: str = "运营审核"


class PublishPackage(BaseModel):
    draft_id: str = Field(alias="draftId")
    title: str
    platform: Platform
    copy_text: str = Field(alias="copy")
    hashtags: list[str]
    cover_title: str = Field(alias="coverTitle")
    video_script: str = Field(alias="videoScript")
    image_prompts: list[str] = Field(alias="imagePrompts")
    asset_checklist: list[str] = Field(alias="assetChecklist")
    compliance_notes: list[str] = Field(alias="complianceNotes")
    platform_adaptation: list[str] = Field(default_factory=list, alias="platformAdaptation")
    operator_checklist: list[str] = Field(default_factory=list, alias="operatorChecklist")
    final_status: Literal["needs_confirmation", "confirmed"] = Field(
        default="needs_confirmation", alias="finalStatus"
    )


class PublishPackageConfirmation(BaseModel):
    id: str
    draft_id: str = Field(alias="draftId")
    operator: str
    confirmed_at: datetime = Field(alias="confirmedAt")
    checklist: list[str]
    note: str | None = None


class ConfirmPublishPackageRequest(BaseModel):
    operator: str = "运营确认"
    checklist: list[str]
    note: str | None = None


class PublishTask(BaseModel):
    id: str
    platform: Platform
    account_name: str = Field(alias="accountName")
    scheduled_at: datetime = Field(alias="scheduledAt")
    publish_method: Literal["api", "enterprise_api", "manual_assist"] = Field(alias="publishMethod")
    status: str
    draft_id: str | None = Field(default=None, alias="draftId")
    package_title: str | None = Field(default=None, alias="packageTitle")
    published_url: str | None = Field(default=None, alias="publishedUrl")
    result_note: str | None = Field(default=None, alias="resultNote")


class MediaAsset(BaseModel):
    id: str
    type: Literal["image", "video", "audio", "document"]
    title: str
    destination: str | None = None
    scene: str | None = None
    license_status: Literal["approved", "pending", "expired", "restricted"] = Field(
        default="pending", alias="licenseStatus"
    )
    consent_status: Literal["not_applicable", "approved", "pending", "expired"] = Field(
        default="not_applicable", alias="consentStatus"
    )
    usage_scope: list[str] = Field(default_factory=list, alias="usageScope")
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    source: str | None = None
    owner: str | None = None
    tags: list[str] = Field(default_factory=list)
    file_url: str = Field(alias="fileUrl")


class CreateMediaAssetRequest(BaseModel):
    type: Literal["image", "video", "audio", "document"]
    title: str
    destination: str | None = None
    scene: str | None = None
    license_status: Literal["approved", "pending", "expired", "restricted"] = Field(
        default="pending", alias="licenseStatus"
    )
    consent_status: Literal["not_applicable", "approved", "pending", "expired"] = Field(
        default="not_applicable", alias="consentStatus"
    )
    usage_scope: list[str] = Field(default_factory=list, alias="usageScope")
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    source: str | None = None
    owner: str | None = None
    tags: list[str] = Field(default_factory=list)
    file_url: str = Field(alias="fileUrl")


class AssetUsageRequest(BaseModel):
    draft_id: str = Field(alias="draftId")
    usage: Literal["cover", "storyboard", "article", "video", "reference"]
    note: str | None = None


class AssetUsageRecord(BaseModel):
    id: str
    asset_id: str = Field(alias="assetId")
    draft_id: str = Field(alias="draftId")
    usage: Literal["cover", "storyboard", "article", "video", "reference"]
    note: str | None = None
    created_at: datetime = Field(alias="createdAt")


class AssetComplianceSummary(BaseModel):
    total_assets: int = Field(alias="totalAssets")
    approved_assets: int = Field(alias="approvedAssets")
    pending_assets: int = Field(alias="pendingAssets")
    blocked_assets: int = Field(alias="blockedAssets")
    expiring_soon: int = Field(alias="expiringSoon")


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
    draft_id: str | None = Field(default=None, alias="draftId")
    package_title: str | None = Field(default=None, alias="packageTitle")


class CreatePublishTaskFromPackageRequest(BaseModel):
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

IP_PROFILES = [
    IpProfile(
        id="travel_consultant",
        name="东南亚旅行顾问",
        persona="长期做海岛线路规划的旅行顾问，擅长把复杂行程讲清楚",
        audience="第一次去东南亚、怕踩坑、需要中文服务的客人",
        tone="专业、直接、低营销感",
        signature="先讲避坑逻辑，再给省心方案",
        prohibitedClaims=["保证最低价", "绝对安全", "100%满意", "不用确认直接下单"],
    ),
    IpProfile(
        id="family_trip_planner",
        name="亲子海岛规划师",
        persona="关注亲子节奏、酒店便利和安全边界的海岛规划师",
        audience="带孩子出行、重视舒适度和服务确定性的家庭",
        tone="温和、可信、细节充分",
        signature="少赶路，多留白，把孩子和老人体验放前面",
        prohibitedClaims=["孩子一定喜欢", "全程无风险", "永久有效价格"],
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
        consentStatus="not_applicable",
        usageScope=["商业推广", "小红书", "抖音", "视频号"],
        source="品牌自有素材",
        owner="TravelMatrix",
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
        consentStatus="approved",
        usageScope=["商业推广", "短视频", "发布包"],
        source="供应商授权",
        owner="龙目岛地接",
        tags=["出海", "浮潜", "短视频"],
        fileUrl="/demo-assets/lombok-boat.mp4",
    ),
]

PUBLISH_TASKS: list[PublishTask] = []
METRICS: list[MetricRequest] = []
CREATIVE_DRAFTS: list[CreativeDraft] = []
REVIEW_ITEMS: list[ReviewItem] = []
ASSET_USAGE_RECORDS: list[AssetUsageRecord] = []
PUBLISH_PACKAGE_CONFIRMATIONS: list[PublishPackageConfirmation] = []
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


@app.get("/api/ip-profiles", response_model=list[IpProfile])
def list_ip_profiles() -> list[IpProfile]:
    return IP_PROFILES


@app.get("/api/media-assets", response_model=list[MediaAsset])
def list_media_assets() -> list[MediaAsset]:
    return MEDIA_ASSETS


@app.get("/api/media-assets/compliance-summary", response_model=AssetComplianceSummary)
def media_asset_compliance_summary() -> AssetComplianceSummary:
    now = datetime.now(timezone.utc)
    expiring_threshold = now + timedelta(days=30)
    blocked_assets = [
        asset
        for asset in MEDIA_ASSETS
        if asset.license_status in {"expired", "restricted"}
        or asset.consent_status in {"pending", "expired"}
        or (asset.expires_at is not None and asset.expires_at < now)
    ]
    return AssetComplianceSummary(
        totalAssets=len(MEDIA_ASSETS),
        approvedAssets=len([asset for asset in MEDIA_ASSETS if asset.license_status == "approved"]),
        pendingAssets=len([asset for asset in MEDIA_ASSETS if asset.license_status == "pending"]),
        blockedAssets=len(blocked_assets),
        expiringSoon=len(
            [
                asset
                for asset in MEDIA_ASSETS
                if asset.expires_at is not None and now <= asset.expires_at <= expiring_threshold
            ]
        ),
    )


@app.post("/api/media-assets", response_model=MediaAsset)
def create_media_asset(payload: CreateMediaAssetRequest) -> MediaAsset:
    asset = MediaAsset(id=f"asset_{uuid4().hex[:10]}", **payload.model_dump(by_alias=True))
    MEDIA_ASSETS.append(asset)
    save_state()
    return asset


@app.post("/api/media-assets/{asset_id}/usage", response_model=AssetUsageRecord)
def record_asset_usage(asset_id: str, payload: AssetUsageRequest) -> AssetUsageRecord:
    asset = find_media_asset(asset_id)
    if not is_asset_usable(asset):
        raise HTTPException(status_code=400, detail="Asset authorization is not ready for publishing")

    record = AssetUsageRecord(
        id=f"usage_{uuid4().hex[:10]}",
        assetId=asset_id,
        draftId=payload.draft_id,
        usage=payload.usage,
        note=payload.note,
        createdAt=datetime.now(timezone.utc),
    )
    ASSET_USAGE_RECORDS.append(record)
    save_state()
    return record


@app.get("/api/media-assets/{asset_id}/usage", response_model=list[AssetUsageRecord])
def list_asset_usage(asset_id: str) -> list[AssetUsageRecord]:
    find_media_asset(asset_id)
    return [record for record in ASSET_USAGE_RECORDS if record.asset_id == asset_id]


@app.post("/api/ai/generate-posts", response_model=GeneratePostsResponse)
def generate_posts(payload: GeneratePostsRequest) -> GeneratePostsResponse:
    product = next((item for item in PRODUCTS if item.id == payload.product_id), PRODUCTS[0])
    variants = [build_variant(product, platform) for platform in payload.platforms]
    return GeneratePostsResponse(draftId=f"draft_{uuid4().hex[:10]}", product=product, variants=variants)


@app.post("/api/ai/generate-creative-package", response_model=CreativePackage)
def generate_creative_package(payload: GenerateCreativePackageRequest) -> CreativePackage:
    product = next((item for item in PRODUCTS if item.id == payload.product_id), PRODUCTS[0])
    return build_creative_package(product, payload)


@app.post("/api/ai/generate-talking-video", response_model=TalkingVideoPlan)
def generate_talking_video(payload: GenerateTalkingVideoRequest) -> TalkingVideoPlan:
    product = next((item for item in PRODUCTS if item.id == payload.product_id), PRODUCTS[0])
    profile = next((item for item in IP_PROFILES if item.id == payload.ip_profile_id), IP_PROFILES[0])
    return build_talking_video_plan(product, profile, payload)


@app.post("/api/ai/analyze-talking-reference", response_model=TalkingReferenceAnalysis)
def analyze_talking_reference(payload: AnalyzeTalkingReferenceRequest) -> TalkingReferenceAnalysis:
    product = next((item for item in PRODUCTS if item.id == payload.product_id), PRODUCTS[0])
    profile = next((item for item in IP_PROFILES if item.id == payload.ip_profile_id), IP_PROFILES[0])
    return build_talking_reference_analysis(product, profile, payload)


@app.post("/api/ai/batch-talking-videos", response_model=BatchTalkingVideoResponse)
def batch_talking_videos(payload: BatchTalkingVideoRequest) -> BatchTalkingVideoResponse:
    product = next((item for item in PRODUCTS if item.id == payload.product_id), PRODUCTS[0])
    profile = next((item for item in IP_PROFILES if item.id == payload.ip_profile_id), IP_PROFILES[0])
    return build_batch_talking_videos(product, profile, payload)


@app.get("/api/creative-drafts", response_model=list[CreativeDraft])
def list_creative_drafts() -> list[CreativeDraft]:
    return sorted(CREATIVE_DRAFTS, key=lambda item: item.updated_at, reverse=True)


@app.post("/api/creative-drafts", response_model=CreativeDraft)
def save_creative_draft(payload: SaveCreativeDraftRequest) -> CreativeDraft:
    now = datetime.now(timezone.utc)
    existing = next((item for item in CREATIVE_DRAFTS if item.package.id == payload.package.id), None)
    if existing is not None:
        existing.package = payload.package
        existing.title = payload.package.cover_title
        existing.updated_at = now
        save_state()
        return existing

    draft = CreativeDraft(
        id=f"draft_{uuid4().hex[:10]}",
        title=payload.package.cover_title,
        package=payload.package,
        status="draft",
        createdAt=now,
        updatedAt=now,
    )
    CREATIVE_DRAFTS.append(draft)
    save_state()
    return draft


@app.post("/api/creative-drafts/{draft_id}/submit-review", response_model=ReviewItem)
def submit_creative_draft_review(draft_id: str) -> ReviewItem:
    draft = find_creative_draft(draft_id)
    now = datetime.now(timezone.utc)
    draft.status = "pending_review"
    draft.updated_at = now

    existing = next(
        (item for item in REVIEW_ITEMS if item.draft_id == draft_id and item.status == "pending"),
        None,
    )
    if existing is not None:
        save_state()
        return existing

    item = ReviewItem(
        id=f"review_{uuid4().hex[:10]}",
        draftId=draft.id,
        title=draft.title,
        platform=draft.package.platform,
        status="pending",
        submittedAt=now,
    )
    REVIEW_ITEMS.append(item)
    save_state()
    return item


@app.get("/api/review-queue", response_model=list[ReviewItem])
def review_queue() -> list[ReviewItem]:
    return sorted(REVIEW_ITEMS, key=lambda item: item.submitted_at, reverse=True)


@app.post("/api/review-items/{review_id}/decision", response_model=ReviewItem)
def review_decision(review_id: str, payload: ReviewDecisionRequest) -> ReviewItem:
    item = next((review for review in REVIEW_ITEMS if review.id == review_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Review item not found")

    now = datetime.now(timezone.utc)
    item.status = payload.decision
    item.reviewed_at = now
    item.reviewer = payload.reviewer
    item.note = payload.note

    draft = find_creative_draft(item.draft_id)
    draft.status = payload.decision
    draft.review_note = payload.note
    draft.updated_at = now
    save_state()
    return item


@app.get("/api/creative-drafts/{draft_id}/publish-package", response_model=PublishPackage)
def creative_publish_package(draft_id: str) -> PublishPackage:
    draft = find_creative_draft(draft_id)
    package = draft.package
    confirmation = next(
        (item for item in PUBLISH_PACKAGE_CONFIRMATIONS if item.draft_id == draft.id),
        None,
    )
    return PublishPackage(
        draftId=draft.id,
        title=package.cover_title,
        platform=package.platform,
        copy=package.advertorial,
        hashtags=[PLATFORM_LABELS[package.platform], package.product.destination, "旅行攻略"],
        coverTitle=package.cover_title,
        videoScript=package.video_script,
        imagePrompts=package.image_prompts,
        assetChecklist=[scene.asset_hint for scene in package.storyboard],
        complianceNotes=package.compliance_notes + ["导出后仍需运营人工确认最终发布内容。"],
        platformAdaptation=build_platform_adaptation(package.platform),
        operatorChecklist=[
            "标题和封面没有夸大承诺",
            "价格、库存、出行日期已人工确认",
            "人物、声音、数字人和素材授权已确认",
            "正文、口播稿、标签和评论引导已适配平台",
            "发布后需要回填链接和首日数据",
        ],
        finalStatus="confirmed" if confirmation else "needs_confirmation",
    )


@app.post(
    "/api/creative-drafts/{draft_id}/publish-package/confirm",
    response_model=PublishPackageConfirmation,
)
def confirm_publish_package(
    draft_id: str, payload: ConfirmPublishPackageRequest
) -> PublishPackageConfirmation:
    find_creative_draft(draft_id)
    if len(payload.checklist) < 3:
        raise HTTPException(status_code=400, detail="At least three checklist items must be confirmed")

    existing = next(
        (item for item in PUBLISH_PACKAGE_CONFIRMATIONS if item.draft_id == draft_id),
        None,
    )
    if existing is not None:
        existing.operator = payload.operator
        existing.checklist = payload.checklist
        existing.note = payload.note
        existing.confirmed_at = datetime.now(timezone.utc)
        save_state()
        return existing

    confirmation = PublishPackageConfirmation(
        id=f"confirm_{uuid4().hex[:10]}",
        draftId=draft_id,
        operator=payload.operator,
        checklist=payload.checklist,
        note=payload.note,
        confirmedAt=datetime.now(timezone.utc),
    )
    PUBLISH_PACKAGE_CONFIRMATIONS.append(confirmation)
    save_state()
    return confirmation


@app.get(
    "/api/creative-drafts/{draft_id}/publish-package/confirmations",
    response_model=list[PublishPackageConfirmation],
)
def list_publish_package_confirmations(draft_id: str) -> list[PublishPackageConfirmation]:
    find_creative_draft(draft_id)
    return [item for item in PUBLISH_PACKAGE_CONFIRMATIONS if item.draft_id == draft_id]


@app.post("/api/creative-drafts/{draft_id}/publish-task", response_model=PublishTask)
def create_publish_task_from_package(
    draft_id: str, payload: CreatePublishTaskFromPackageRequest
) -> PublishTask:
    draft = find_creative_draft(draft_id)
    confirmation = next(
        (item for item in PUBLISH_PACKAGE_CONFIRMATIONS if item.draft_id == draft_id),
        None,
    )
    if confirmation is None:
        raise HTTPException(status_code=400, detail="Publish package must be confirmed first")

    task = PublishTask(
        id=f"task_{uuid4().hex[:10]}",
        platform=draft.package.platform,
        accountName=payload.account_name,
        scheduledAt=payload.scheduled_at,
        publishMethod=payload.publish_method,
        status="scheduled",
        draftId=draft.id,
        packageTitle=draft.title,
    )
    PUBLISH_TASKS.append(task)
    save_state()
    return task


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
            packageTitle="演示发布包：亲子海岛攻略",
        ),
        PublishTask(
            id="task_douyin_001",
            platform="douyin",
            accountName="东南亚短视频账号",
            scheduledAt=now + timedelta(hours=5),
            publishMethod="manual_assist",
            status="scheduled",
            packageTitle="演示发布包：海岛短视频",
        ),
        PublishTask(
            id="task_weibo_001",
            platform="weibo",
            accountName="官方活动账号",
            scheduledAt=now + timedelta(hours=8),
            publishMethod="api",
            status="scheduled",
            packageTitle="演示发布包：微博活动文案",
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
        draftId=payload.draft_id,
        packageTitle=payload.package_title,
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
    task.published_url = payload.published_url
    task.result_note = payload.note
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


def build_creative_package(
    product: TravelProduct, payload: GenerateCreativePackageRequest
) -> CreativePackage:
    destination = product.destination
    selling_points = product.selling_points[:4]
    platform_label = PLATFORM_LABELS[payload.platform]
    scenes = [
        StoryboardScene(
            order=1,
            shot="开场近景 + 快切目的地画面",
            visualPrompt=f"{destination}旅行短视频开场，海岛阳光、自然真实、竖屏构图、适合{platform_label}",
            voiceover=f"第一次去{destination}，别先急着订行程。",
            subtitle=f"第一次去{destination}先看这条",
            assetHint="目的地大景、酒店外观、出海镜头",
        ),
        StoryboardScene(
            order=2,
            shot="卖点连拍",
            visualPrompt=f"{destination}旅行体验拼贴，包含{selling_points[0]}和{selling_points[1]}，明亮商业摄影风格",
            voiceover=f"这条{product.days}天线路把{selling_points[0]}、{selling_points[1]}这些重点体验放在前面。",
            subtitle="核心体验先安排",
            assetHint="产品卖点对应图片或短视频素材",
        ),
        StoryboardScene(
            order=3,
            shot="人群场景",
            visualPrompt=f"适合{product.target_audience}的{destination}旅行场景，人物自然、不夸张、真实游玩记录",
            voiceover=f"更适合{product.target_audience}，节奏不用赶。",
            subtitle="适合人群清楚说明",
            assetHint="亲子、情侣或轻户外人物素材，需确认授权",
        ),
        StoryboardScene(
            order=4,
            shot="咨询引导",
            visualPrompt=f"{destination}旅行攻略封面图，干净排版，标题留白，真实目的地背景",
            voiceover=f"价格以实际咨询为准，把人数和出行日期发来，先帮你看适合哪条线。",
            subtitle="人数 + 日期，先做方案",
            assetHint="封面图、品牌 logo、客服二维码占位",
        ),
    ]

    return CreativePackage(
        id=f"creative_{uuid4().hex[:10]}",
        product=product,
        platform=payload.platform,
        objective=payload.objective,
        hook=f"{destination}{product.days}天怎么玩更省心？先看这条路线逻辑。",
        coverTitle=f"{destination}{product.days}天省心玩法",
        videoScript="\n".join(scene.voiceover for scene in scenes),
        imagePrompts=[
            f"{destination}旅行封面图，真实自然光，清爽排版，突出“{destination}{product.days}天攻略”",
            f"{destination}旅游产品卖点图，展示{'、'.join(selling_points)}，商业旅拍质感",
            f"面向{product.target_audience}的旅行软文配图，真实体验、低营销感、竖版构图",
        ],
        advertorial=(
            f"如果你正在看{destination}行程，可以先按人群和节奏筛选。"
            f"{product.name}适合{product.target_audience}，主要亮点是{'、'.join(product.selling_points)}。"
            f"参考价格为{product.reference_price}。建议出发前确认酒店、车导、出海天气和素材授权，"
            "再根据平台语气改写成小红书笔记、短视频口播或公众号说明。"
        ),
        storyboard=scenes,
        complianceNotes=[
            "价格、库存、签证、安全等信息必须人工复核，避免绝对化承诺。",
            "含人物的视频、图片、数字人素材必须确认商业授权和使用期限。",
            "平台发布优先生成发布包，由运营人工确认后发布。",
        ],
    )


def build_talking_video_plan(
    product: TravelProduct, profile: IpProfile, payload: GenerateTalkingVideoRequest
) -> TalkingVideoPlan:
    destination = product.destination
    hook = payload.reference_hook or f"第一次去{destination}，最容易踩坑的不是景点，而是行程顺序。"
    structure = [
        "3秒痛点钩子：先说用户最担心的问题",
        "身份背书：用IP人设解释为什么可信",
        "避坑解释：拆一个常见错误",
        "方案给法：给出可执行的路线逻辑",
        "轻转化：引导用户带人数和日期咨询",
    ]
    teleprompter = [
        hook,
        f"我是{profile.name}，平时主要帮{profile.audience}做{destination}线路。",
        f"如果你看的是{product.name}，先别只比价格，先看节奏和服务边界。",
        f"这条线路的重点是{'、'.join(product.selling_points[:4])}，适合{product.target_audience}。",
        f"参考价格是{product.reference_price}。实际出行前，要按人数、日期、酒店和天气重新确认。",
        "你把出行日期、人数和预算发来，我先帮你判断哪条线更合适。",
    ]
    shot_plan = [
        StoryboardScene(
            order=1,
            shot="真人或数字人半身口播",
            visualPrompt=f"{profile.name}面对镜头讲解{destination}旅行避坑，干净背景，竖屏短视频",
            voiceover=teleprompter[0],
            subtitle=teleprompter[0],
            assetHint="IP形象、数字人或真人口播素材；必须确认肖像和声音授权",
        ),
        StoryboardScene(
            order=2,
            shot="路线卖点插入画面",
            visualPrompt=f"{destination}旅行卖点画面，包含{'、'.join(product.selling_points[:3])}，真实旅拍风格",
            voiceover=teleprompter[3],
            subtitle="先看节奏，再看价格",
            assetHint="目的地素材、酒店、出海、景点镜头",
        ),
        StoryboardScene(
            order=3,
            shot="提词器收口 + 咨询引导",
            visualPrompt=f"{destination}旅行咨询引导页，简洁文字，品牌可信感",
            voiceover=teleprompter[-1],
            subtitle="人数 + 日期 + 预算，先做方案",
            assetHint="品牌尾板、客服二维码、发布平台安全话术",
        ),
    ]
    return TalkingVideoPlan(
        id=f"talking_{uuid4().hex[:10]}",
        product=product,
        ipProfile=profile,
        platform=payload.platform,
        topic=payload.topic,
        titleOptions=[
            f"第一次去{destination}，先避开这个行程坑",
            f"{destination}{product.days}天怎么安排更省心？",
            f"别只比价格，{destination}行程先看这3点",
        ],
        viralStructure=structure,
        teleprompter=teleprompter,
        script="\n".join(teleprompter),
        shotPlan=shot_plan,
        coverText=f"{destination}避坑口播",
        callToAction="评论或私信发送人数、日期、预算，人工确认后给线路建议。",
        complianceNotes=[
            "口播不得承诺最低价、绝对安全、保证满意等绝对化结果。",
            "真人形象、数字人、声音克隆必须保留授权记录和使用期限。",
            "可学习爆款结构，但不能搬运他人原文、画面或专属人设。",
        ],
    )


def build_talking_reference_analysis(
    product: TravelProduct, profile: IpProfile, payload: AnalyzeTalkingReferenceRequest
) -> TalkingReferenceAnalysis:
    text = payload.reference_text.strip()
    sentences = [part.strip() for part in text.replace("！", "。").replace("？", "。").split("。") if part.strip()]
    first_line = sentences[0] if sentences else text[:32]
    has_question = "?" in text or "？" in payload.reference_text
    has_number = any(char.isdigit() for char in text) or any(char in text for char in "一二三四五六七八九十")

    hook_type = "问题钩子" if has_question else "数字清单钩子" if has_number else "痛点反差钩子"
    structure = [
        f"开头用{hook_type}制造停留：{first_line[:40]}",
        "中段用身份或经验建立可信度",
        "主体只讲一个核心误区，避免信息过散",
        "结尾给用户一个低门槛动作，例如评论人数、日期、预算",
    ]
    rhythm_notes = [
        "前 3 秒必须出现具体对象和具体痛点",
        "每 6 到 8 秒切一次信息点或画面",
        "字幕使用短句，不堆长段落",
        "转化句放在最后 5 秒，不要一开始就强营销",
    ]
    reusable_patterns = [
        "把“我发现很多人……”改成目标人群的真实场景",
        "把“不要这样做”改成“先确认这三件事”",
        "用案例解释路线逻辑，而不是直接堆卖点",
    ]
    warnings = [
        "只能学习结构，不直接复用参考原文、专属金句或独特人设。",
        "不得复刻他人画面、声音、数字人形象或账号包装。",
        "旅游价格、库存、安全和签证信息必须人工复核。",
    ]

    rewritten_payload = GenerateTalkingVideoRequest(
        productId=product.id,
        ipProfileId=profile.id,
        platform=payload.platform,
        topic=payload.topic,
        referenceHook=f"很多人第一次去{product.destination}，不是预算不够，而是行程顺序一开始就排错了。",
        durationSeconds=45,
    )
    rewritten_plan = build_talking_video_plan(product, profile, rewritten_payload)
    rewritten_plan.viral_structure = structure + rewritten_plan.viral_structure[-2:]
    rewritten_plan.teleprompter = [
        f"很多人第一次去{product.destination}，不是预算不够，而是行程顺序一开始就排错了。",
        f"我是{profile.name}，这条视频按{payload.platform}的短口播节奏，帮你把坑讲清楚。",
        f"如果你准备看{product.name}，先确认：每天路程、出海天气、酒店位置和中文服务。",
        f"它适合{product.target_audience}，亮点是{'、'.join(product.selling_points[:4])}。",
        f"价格参考：{product.reference_price}，最终以实际咨询和日期为准。",
        "把人数、日期和预算发来，我先帮你判断是不是适合这条线。",
    ]
    rewritten_plan.script = "\n".join(rewritten_plan.teleprompter)

    return TalkingReferenceAnalysis(
        id=f"analysis_{uuid4().hex[:10]}",
        platform=payload.platform,
        topic=payload.topic,
        hookType=hook_type,
        structure=structure,
        rhythmNotes=rhythm_notes,
        reusablePatterns=reusable_patterns,
        originalityWarnings=warnings,
        rewrittenPlan=rewritten_plan,
    )


def build_batch_talking_videos(
    product: TravelProduct, profile: IpProfile, payload: BatchTalkingVideoRequest
) -> BatchTalkingVideoResponse:
    default_angles = [
        "第一次出行避坑",
        "亲子家庭省心玩法",
        "情侣蜜月氛围感",
        "预算和价格说明",
        "酒店位置怎么选",
        "出海天气和行程顺序",
        "中文服务和接送安排",
        "轻户外体验推荐",
        "无购物纯玩解释",
        "出发前确认清单",
    ]
    angles = (payload.angles or default_angles)[: payload.count]
    while len(angles) < payload.count:
        angles.append(default_angles[len(angles) % len(default_angles)])

    items: list[TalkingVideoPlan] = []
    for index, angle in enumerate(angles, start=1):
        hook = build_angle_hook(product, angle)
        plan_payload = GenerateTalkingVideoRequest(
            productId=product.id,
            ipProfileId=profile.id,
            platform=payload.platform,
            topic=angle,
            referenceHook=hook,
            durationSeconds=45,
        )
        plan = build_talking_video_plan(product, profile, plan_payload)
        plan.title_options = [
            f"{index}. {angle}：{product.destination}怎么安排？",
            f"{product.destination}{product.days}天，{angle}先看这条",
            f"做{product.destination}攻略，别忽略{angle}",
        ]
        plan.cover_text = f"{product.destination}{angle}"
        plan.teleprompter[1] = f"我是{profile.name}，这条只讲{angle}，不堆复杂攻略。"
        plan.script = "\n".join(plan.teleprompter)
        items.append(plan)

    return BatchTalkingVideoResponse(
        batchId=f"batch_{uuid4().hex[:10]}",
        product=product,
        ipProfile=profile,
        platform=payload.platform,
        items=items,
        productionNotes=[
            "每条口播只保留一个核心角度，避免账号内容重复。",
            "批量生成后先进入草稿和审核，不直接发布。",
            "涉及价格、库存、签证、安全、人物授权的内容必须人工复核。",
        ],
    )


def build_angle_hook(product: TravelProduct, angle: str) -> str:
    destination = product.destination
    hooks = {
        "第一次出行避坑": f"第一次去{destination}，别先看景点，先看行程顺序。",
        "亲子家庭省心玩法": f"带孩子去{destination}，行程别排太满，先把酒店和车程定好。",
        "情侣蜜月氛围感": f"去{destination}过蜜月，真正影响体验的是酒店位置和留白时间。",
        "预算和价格说明": f"{destination}价格不要只看起价，要先确认日期、酒店和服务范围。",
        "酒店位置怎么选": f"{destination}酒店选错位置，后面每天都在路上消耗时间。",
        "出海天气和行程顺序": f"{destination}出海不是每天都适合，顺序排错很影响体验。",
        "中文服务和接送安排": f"第一次去{destination}，中文服务和接送细节比想象中更重要。",
        "轻户外体验推荐": f"想轻户外玩{destination}，别把所有项目塞进同一天。",
        "无购物纯玩解释": f"看{destination}纯玩线路，要确认时间花在体验上，不是购物点上。",
        "出发前确认清单": f"去{destination}前，先确认这几项，再决定要不要下单。",
    }
    return hooks.get(angle, f"{destination}{angle}怎么安排更省心？先看这条。")


def build_platform_adaptation(platform: Platform) -> list[str]:
    if platform == "xiaohongshu":
        return ["封面标题控制在 12 字左右", "正文保留真实体验感", "避免硬广语气，标签不堆砌"]
    if platform == "douyin":
        return ["前三秒必须出现痛点钩子", "字幕短句快切", "结尾使用评论/私信引导"]
    if platform == "wechat_channels":
        return ["语气更克制可信", "突出品牌和服务确定性", "发布前人工确认封面和视频号标题"]
    if platform == "toutiao":
        return ["正文增加行程、费用、注意事项", "标题明确攻略对象", "价格表达加确认提示"]
    if platform == "weibo":
        return ["文案短，适合活动和客服承接", "标签数量控制", "评论区准备客服回复话术"]
    return ["弱营销表达", "以经验分享角度组织内容", "避免复制平台外爆款原文"]


def find_creative_draft(draft_id: str) -> CreativeDraft:
    draft = next((item for item in CREATIVE_DRAFTS if item.id == draft_id), None)
    if draft is None:
        raise HTTPException(status_code=404, detail="Creative draft not found")
    return draft


def find_media_asset(asset_id: str) -> MediaAsset:
    asset = next((item for item in MEDIA_ASSETS if item.id == asset_id), None)
    if asset is None:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return asset


def is_asset_usable(asset: MediaAsset) -> bool:
    now = datetime.now(timezone.utc)
    if asset.license_status != "approved":
        return False
    if asset.consent_status not in {"not_applicable", "approved"}:
        return False
    if asset.expires_at is not None and asset.expires_at < now:
        return False
    return True


def load_state() -> None:
    if not STATE_FILE.exists():
        return

    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    MEDIA_ASSETS[:] = [MediaAsset.model_validate(item) for item in data.get("mediaAssets", [])] or MEDIA_ASSETS
    PUBLISH_TASKS[:] = [PublishTask.model_validate(item) for item in data.get("publishTasks", [])]
    METRICS[:] = [MetricRequest.model_validate(item) for item in data.get("metrics", [])]
    CREATIVE_DRAFTS[:] = [
        CreativeDraft.model_validate(item) for item in data.get("creativeDrafts", [])
    ]
    REVIEW_ITEMS[:] = [ReviewItem.model_validate(item) for item in data.get("reviewItems", [])]
    ASSET_USAGE_RECORDS[:] = [
        AssetUsageRecord.model_validate(item) for item in data.get("assetUsageRecords", [])
    ]
    PUBLISH_PACKAGE_CONFIRMATIONS[:] = [
        PublishPackageConfirmation.model_validate(item)
        for item in data.get("publishPackageConfirmations", [])
    ]


def save_state() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "mediaAssets": [item.model_dump(mode="json", by_alias=True) for item in MEDIA_ASSETS],
        "publishTasks": [item.model_dump(mode="json", by_alias=True) for item in PUBLISH_TASKS],
        "metrics": [item.model_dump(mode="json", by_alias=True) for item in METRICS],
        "creativeDrafts": [item.model_dump(mode="json", by_alias=True) for item in CREATIVE_DRAFTS],
        "reviewItems": [item.model_dump(mode="json", by_alias=True) for item in REVIEW_ITEMS],
        "assetUsageRecords": [
            item.model_dump(mode="json", by_alias=True) for item in ASSET_USAGE_RECORDS
        ],
        "publishPackageConfirmations": [
            item.model_dump(mode="json", by_alias=True) for item in PUBLISH_PACKAGE_CONFIRMATIONS
        ],
    }
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


load_state()
