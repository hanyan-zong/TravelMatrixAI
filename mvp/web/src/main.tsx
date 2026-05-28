import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BarChart3,
  CalendarDays,
  CheckCircle2,
  Clapperboard,
  FileText,
  Images,
  LayoutDashboard,
  Megaphone,
  Plane,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";
import "./styles.css";

type Platform = "小红书" | "抖音" | "视频号" | "今日头条" | "微博" | "豆瓣";
type ViewName =
  | "工作台"
  | "产品库"
  | "素材库"
  | "内容工厂"
  | "视频工厂"
  | "审核中心"
  | "发布日历"
  | "数据看板";
type ApiPlatform =
  | "xiaohongshu"
  | "douyin"
  | "wechat_channels"
  | "toutiao"
  | "weibo"
  | "douban";

type TravelProduct = {
  id: string;
  name: string;
  destination: string;
  days: number;
  target_audience: string;
  reference_price: string;
  selling_points: string[];
};

type IpProfile = {
  id: string;
  name: string;
  persona: string;
  audience: string;
  tone: string;
  signature: string;
  prohibitedClaims: string[];
};

type ApiVariant = {
  id: string;
  platform: ApiPlatform;
  title: string;
  body: string;
  hashtags: string[];
  coverText: string;
  riskLevel: "low" | "medium" | "high";
  status: string;
};

type PublishTask = {
  id: string;
  platform: ApiPlatform;
  accountName: string;
  scheduledAt: string;
  publishMethod: "api" | "enterprise_api" | "manual_assist";
  status: string;
  draftId?: string;
  packageTitle?: string;
  publishedUrl?: string;
  resultNote?: string;
};

type AnalyticsOverview = {
  totalViews: number;
  totalLeads: number;
  totalConversions: number;
  bestPlatform: string;
  recommendation: string;
};

type UserProfile = {
  id: string;
  name: string;
  role: string;
  workspace: string;
};

type MediaAsset = {
  id: string;
  type: "image" | "video" | "audio" | "document";
  title: string;
  destination?: string;
  scene?: string;
  licenseStatus: string;
  consentStatus: string;
  usageScope: string[];
  expiresAt?: string;
  source?: string;
  owner?: string;
  tags: string[];
  fileUrl: string;
};

type AssetComplianceSummary = {
  totalAssets: number;
  approvedAssets: number;
  pendingAssets: number;
  blockedAssets: number;
  expiringSoon: number;
};

type StoryboardScene = {
  order: number;
  shot: string;
  visualPrompt: string;
  voiceover: string;
  subtitle: string;
  assetHint: string;
};

type CreativePackage = {
  id: string;
  product: TravelProduct;
  platform: ApiPlatform;
  objective: string;
  hook: string;
  coverTitle: string;
  videoScript: string;
  imagePrompts: string[];
  advertorial: string;
  storyboard: StoryboardScene[];
  complianceNotes: string[];
};

type CreativeDraft = {
  id: string;
  title: string;
  package: CreativePackage;
  status: "draft" | "pending_review" | "approved" | "rejected";
  reviewNote?: string;
  createdAt: string;
  updatedAt: string;
};

type ReviewItem = {
  id: string;
  draftId: string;
  title: string;
  platform: ApiPlatform;
  status: "pending" | "approved" | "rejected";
  submittedAt: string;
  reviewedAt?: string;
  reviewer?: string;
  note?: string;
};

type PublishPackage = {
  draftId: string;
  title: string;
  platform: ApiPlatform;
  copy: string;
  hashtags: string[];
  coverTitle: string;
  videoScript: string;
  imagePrompts: string[];
  assetChecklist: string[];
  complianceNotes: string[];
  platformAdaptation: string[];
  operatorChecklist: string[];
  finalStatus: "needs_confirmation" | "confirmed";
};

type PublishPackageConfirmation = {
  id: string;
  draftId: string;
  operator: string;
  confirmedAt: string;
  checklist: string[];
  note?: string;
};

type TalkingVideoPlan = {
  id: string;
  product: TravelProduct;
  ipProfile: IpProfile;
  platform: ApiPlatform;
  topic: string;
  titleOptions: string[];
  viralStructure: string[];
  teleprompter: string[];
  script: string;
  shotPlan: StoryboardScene[];
  coverText: string;
  callToAction: string;
  complianceNotes: string[];
};

type TalkingReferenceAnalysis = {
  id: string;
  platform: ApiPlatform;
  topic: string;
  hookType: string;
  structure: string[];
  rhythmNotes: string[];
  reusablePatterns: string[];
  originalityWarnings: string[];
  rewrittenPlan: TalkingVideoPlan;
};

type BatchTalkingVideoResponse = {
  batchId: string;
  product: TravelProduct;
  ipProfile: IpProfile;
  platform: ApiPlatform;
  items: TalkingVideoPlan[];
  productionNotes: string[];
};

const platforms: Platform[] = ["小红书", "抖音", "视频号", "今日头条", "微博", "豆瓣"];

const navItems: Array<[React.ElementType, ViewName]> = [
  [LayoutDashboard, "工作台"],
  [Plane, "产品库"],
  [Images, "素材库"],
  [Sparkles, "内容工厂"],
  [Clapperboard, "视频工厂"],
  [ShieldCheck, "审核中心"],
  [CalendarDays, "发布日历"],
  [BarChart3, "数据看板"],
];

const platformMap: Record<ApiPlatform, Platform> = {
  xiaohongshu: "小红书",
  douyin: "抖音",
  wechat_channels: "视频号",
  toutiao: "今日头条",
  weibo: "微博",
  douban: "豆瓣",
};

const platformPayload: ApiPlatform[] = [
  "xiaohongshu",
  "douyin",
  "wechat_channels",
  "toutiao",
  "weibo",
  "douban",
];

const fallbackProduct: TravelProduct = {
  id: "bali-6d5n",
  name: "巴厘岛 6 天 5 晚纯玩",
  destination: "巴厘岛",
  days: 6,
  target_audience: "亲子、蜜月、第一次去海岛的客人",
  reference_price: "5899 元起，以实际咨询为准",
  selling_points: ["蓝梦岛出海", "乌布梯田", "海边酒店", "中文司导", "无购物纯玩"],
};

function App() {
  const [products, setProducts] = useState<TravelProduct[]>([fallbackProduct]);
  const [selectedProductId, setSelectedProductId] = useState(fallbackProduct.id);
  const [variants, setVariants] = useState<ApiVariant[]>([]);
  const [ipProfiles, setIpProfiles] = useState<IpProfile[]>([]);
  const [talkingVideo, setTalkingVideo] = useState<TalkingVideoPlan>(() =>
    buildFallbackTalkingVideo(fallbackProduct),
  );
  const [referenceText, setReferenceText] = useState(
    "第一次去海岛千万别只看价格？很多人踩坑都是因为行程顺序排错，先看酒店位置，再看出海天气，最后再看服务。",
  );
  const [referenceAnalysis, setReferenceAnalysis] = useState<TalkingReferenceAnalysis | null>(null);
  const [batchTalking, setBatchTalking] = useState<BatchTalkingVideoResponse | null>(null);
  const [creativePackage, setCreativePackage] = useState<CreativePackage>(() =>
    buildFallbackCreativePackage(fallbackProduct),
  );
  const [creativeDrafts, setCreativeDrafts] = useState<CreativeDraft[]>([]);
  const [reviewItems, setReviewItems] = useState<ReviewItem[]>([]);
  const [publishPackage, setPublishPackage] = useState<PublishPackage | null>(null);
  const [publishConfirmations, setPublishConfirmations] = useState<PublishPackageConfirmation[]>([]);
  const [publishResultForm, setPublishResultForm] = useState({
    taskId: "",
    publishedUrl: "",
    views: "1200",
    likes: "80",
    saves: "30",
    comments: "12",
    shares: "6",
    leads: "4",
    conversions: "1",
  });
  const [workflowMessage, setWorkflowMessage] = useState("创意包可保存后进入审核流程。");
  const [tasks, setTasks] = useState<PublishTask[]>([]);
  const [assets, setAssets] = useState<MediaAsset[]>([]);
  const [assetSummary, setAssetSummary] = useState<AssetComplianceSummary>({
    totalAssets: 0,
    approvedAssets: 0,
    pendingAssets: 0,
    blockedAssets: 0,
    expiringSoon: 0,
  });
  const [assetForm, setAssetForm] = useState({
    title: "",
    type: "image" as MediaAsset["type"],
    destination: "",
    scene: "",
    licenseStatus: "pending",
    consentStatus: "not_applicable",
    usageScope: "商业推广,小红书,抖音",
    source: "",
    owner: "",
    tags: "",
    fileUrl: "",
  });
  const [assetMessage, setAssetMessage] = useState("登记素材后，可在发布前检查授权和人物同意状态。");
  const [analytics, setAnalytics] = useState<AnalyticsOverview>({
    totalViews: 12860,
    totalLeads: 42,
    totalConversions: 6,
    bestPlatform: "小红书",
    recommendation: "下周继续增加海岛亲子攻略内容，标题保留价格确认提示，短视频重点优化前三秒钩子。",
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [apiStatus, setApiStatus] = useState<"连接中" | "已连接" | "离线演示">("连接中");
  const [activeView, setActiveView] = useState<ViewName>("工作台");
  const [user, setUser] = useState<UserProfile>({
    id: "demo",
    name: "运营管理员",
    role: "admin",
    workspace: "TravelMatrix Demo",
  });

  const selectedProduct = useMemo(
    () => products.find((item) => item.id === selectedProductId) ?? products[0] ?? fallbackProduct,
    [products, selectedProductId],
  );

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/travel-products")
      .then((response) => response.json())
      .then((data: TravelProduct[]) => {
        setProducts(data);
        setSelectedProductId(data[0]?.id ?? fallbackProduct.id);
        setApiStatus("已连接");
      })
      .catch(() => {
        setApiStatus("离线演示");
        setProducts([fallbackProduct]);
        setVariants(buildFallbackVariants());
      });

    fetch("http://127.0.0.1:8000/api/ip-profiles")
      .then((response) => response.json())
      .then((data: IpProfile[]) => setIpProfiles(data))
      .catch(() => setIpProfiles([buildFallbackIpProfile()]));

    fetch("http://127.0.0.1:8000/api/publish-tasks/calendar")
      .then((response) => response.json())
      .then((data: PublishTask[]) => setTasks(data))
      .catch(() => setTasks(buildFallbackTasks()));

    fetch("http://127.0.0.1:8000/api/analytics/overview")
      .then((response) => response.json())
      .then((data: AnalyticsOverview) => setAnalytics(data))
      .catch(() => undefined);

    fetch("http://127.0.0.1:8000/api/auth/me")
      .then((response) => response.json())
      .then((data: UserProfile) => setUser(data))
      .catch(() => undefined);

    void refreshAssets();

    void refreshCreativeWorkflow();
  }, []);

  useEffect(() => {
    void generatePosts(selectedProductId);
    void generateCreativePackage(selectedProductId);
    void generateTalkingVideo(selectedProductId);
  }, [selectedProductId]);

  async function generatePosts(productId: string) {
    setIsGenerating(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/ai/generate-posts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          productId,
          platforms: platformPayload,
          contentGoal: "lead_generation",
        }),
      });
      const data: { variants: ApiVariant[] } = await response.json();
      setVariants(data.variants);
      setApiStatus("已连接");
      setWorkflowMessage(`已生成 ${data.variants.length} 条平台内容，可在内容工厂保存为草稿。`);
    } catch {
      setApiStatus("离线演示");
      setVariants(buildFallbackVariants());
      setWorkflowMessage("内容生成失败，当前显示离线演示内容。请确认 API 已启动。");
    } finally {
      setIsGenerating(false);
    }
  }

  async function saveVariantAsDraft(variant: ApiVariant) {
    const packagePayload = postVariantToCreativePackage(variant, selectedProduct);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/creative-drafts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ package: packagePayload }),
      });
      const data: CreativeDraft = await response.json();
      setWorkflowMessage(`已保存内容草稿：${data.title}`);
      await refreshCreativeWorkflow();
    } catch {
      setWorkflowMessage("内容草稿保存失败：请确认 API 已启动。");
    }
  }

  async function saveAllVariantsAsDrafts() {
    const items = variants.length ? variants : buildFallbackVariants();
    for (const variant of items) {
      await saveVariantAsDraft(variant);
    }
    setWorkflowMessage(`已保存 ${items.length} 条平台内容草稿，可进入视频工厂或审核中心继续处理。`);
  }

  async function generateCreativePackage(productId: string) {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/ai/generate-creative-package", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          productId,
          platform: "douyin",
          objective: "短视频引流",
          durationSeconds: 30,
        }),
      });
      const data: CreativePackage = await response.json();
      setCreativePackage(data);
      setPublishPackage(null);
      setWorkflowMessage("已生成新的创意包，可以保存为草稿。");
    } catch {
      setCreativePackage(buildFallbackCreativePackage(selectedProduct));
      setWorkflowMessage("当前使用离线创意包，启动 API 后可保存和审核。");
    }
  }

  async function generateTalkingVideo(productId: string) {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/ai/generate-talking-video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          productId,
          ipProfileId: ipProfiles[0]?.id ?? "travel_consultant",
          platform: "douyin",
          topic: "第一次出行避坑",
          durationSeconds: 45,
        }),
      });
      const data: TalkingVideoPlan = await response.json();
      setTalkingVideo(data);
    } catch {
      setTalkingVideo(buildFallbackTalkingVideo(selectedProduct));
    }
  }

  async function analyzeTalkingReference() {
    if (referenceText.trim().length < 10) {
      setWorkflowMessage("参考口播至少输入 10 个字。");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/ai/analyze-talking-reference", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          productId: selectedProductId,
          ipProfileId: ipProfiles[0]?.id ?? "travel_consultant",
          platform: "douyin",
          topic: "参考爆款结构改写",
          referenceText,
        }),
      });
      const data: TalkingReferenceAnalysis = await response.json();
      setReferenceAnalysis(data);
      setTalkingVideo(data.rewrittenPlan);
      setWorkflowMessage("已拆解参考结构，并生成原创口播改写。");
    } catch {
      setWorkflowMessage("拆解失败：请确认 API 已启动。");
    }
  }

  async function generateBatchTalkingVideos() {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/ai/batch-talking-videos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          productId: selectedProductId,
          ipProfileId: ipProfiles[0]?.id ?? "travel_consultant",
          platform: "douyin",
          count: 10,
          angles: [
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
          ],
        }),
      });
      const data: BatchTalkingVideoResponse = await response.json();
      setBatchTalking(data);
      setWorkflowMessage(`已生成 ${data.items.length} 条批量口播，选择优质条目保存为草稿。`);
    } catch {
      setWorkflowMessage("批量口播生成失败：请确认 API 已启动。");
    }
  }

  async function saveTalkingVideoAsDraft(plan: TalkingVideoPlan) {
    const packagePayload = talkingVideoToCreativePackage(plan);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/creative-drafts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ package: packagePayload }),
      });
      const data: CreativeDraft = await response.json();
      setWorkflowMessage(`已保存口播草稿：${data.title}`);
      await refreshCreativeWorkflow();
    } catch {
      setWorkflowMessage("保存口播草稿失败：请确认 API 已启动。");
    }
  }

  async function refreshCreativeWorkflow() {
    try {
      const [draftResponse, reviewResponse] = await Promise.all([
        fetch("http://127.0.0.1:8000/api/creative-drafts"),
        fetch("http://127.0.0.1:8000/api/review-queue"),
      ]);
      setCreativeDrafts(await draftResponse.json());
      setReviewItems(await reviewResponse.json());
    } catch {
      setCreativeDrafts([]);
      setReviewItems([]);
    }
  }

  async function refreshAssets() {
    try {
      const [assetsResponse, summaryResponse] = await Promise.all([
        fetch("http://127.0.0.1:8000/api/media-assets"),
        fetch("http://127.0.0.1:8000/api/media-assets/compliance-summary"),
      ]);
      setAssets(await assetsResponse.json());
      setAssetSummary(await summaryResponse.json());
    } catch {
      setAssets([]);
      setAssetSummary({
        totalAssets: 0,
        approvedAssets: 0,
        pendingAssets: 0,
        blockedAssets: 0,
        expiringSoon: 0,
      });
    }
  }

  async function saveCurrentCreativeDraft() {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/creative-drafts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ package: creativePackage }),
      });
      const data: CreativeDraft = await response.json();
      setWorkflowMessage(`已保存草稿：${data.title}`);
      await refreshCreativeWorkflow();
    } catch {
      setWorkflowMessage("保存失败：请确认 API 已启动。");
    }
  }

  async function submitCreativeDraft(draftId: string) {
    try {
      await fetch(`http://127.0.0.1:8000/api/creative-drafts/${draftId}/submit-review`, {
        method: "POST",
      });
      setWorkflowMessage("已提交审核，审核中心可以处理。");
      await refreshCreativeWorkflow();
    } catch {
      setWorkflowMessage("提交审核失败：请确认 API 已启动。");
    }
  }

  async function decideReview(reviewId: string, decision: ReviewItem["status"]) {
    if (decision === "pending") return;
    try {
      await fetch(`http://127.0.0.1:8000/api/review-items/${reviewId}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision,
          note: decision === "approved" ? "内容、素材和价格提示已检查" : "需要修改标题、素材授权或价格表达",
          reviewer: user.name,
        }),
      });
      setWorkflowMessage(decision === "approved" ? "审核已通过。" : "审核已驳回，草稿需要修改。");
      await refreshCreativeWorkflow();
    } catch {
      setWorkflowMessage("审核操作失败：请确认 API 已启动。");
    }
  }

  async function exportPublishPackage(draftId: string) {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/creative-drafts/${draftId}/publish-package`);
      const data: PublishPackage = await response.json();
      setPublishPackage(data);
      await refreshPublishConfirmations(draftId);
      setWorkflowMessage(`已生成发布包：${data.title}`);
    } catch {
      setWorkflowMessage("发布包生成失败：请先保存草稿并启动 API。");
    }
  }

  async function refreshPublishConfirmations(draftId: string) {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/creative-drafts/${draftId}/publish-package/confirmations`,
      );
      setPublishConfirmations(await response.json());
    } catch {
      setPublishConfirmations([]);
    }
  }

  async function confirmPublishPackage() {
    if (!publishPackage) return;
    try {
      await fetch(
        `http://127.0.0.1:8000/api/creative-drafts/${publishPackage.draftId}/publish-package/confirm`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            operator: user.name,
            checklist: publishPackage.operatorChecklist,
            note: "运营已确认发布包内容、素材授权和平台适配。",
          }),
        },
      );
      await exportPublishPackage(publishPackage.draftId);
      setWorkflowMessage("发布包已人工确认，可以安排发布任务。");
    } catch {
      setWorkflowMessage("发布包确认失败：请确认 API 已启动。");
    }
  }

  async function createPublishTaskFromPackage() {
    if (!publishPackage) {
      setWorkflowMessage("请先生成并确认发布包。");
      return;
    }
    if (publishPackage.finalStatus !== "confirmed") {
      setWorkflowMessage("发布包需要人工确认后才能创建发布任务。");
      return;
    }
    try {
      const scheduledAt = new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString();
      const response = await fetch(
        `http://127.0.0.1:8000/api/creative-drafts/${publishPackage.draftId}/publish-task`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            accountName: `${platformMap[publishPackage.platform]}运营账号`,
            scheduledAt,
            publishMethod: "manual_assist",
          }),
        },
      );
      const data: PublishTask = await response.json();
      setTasks((current) => [data, ...current]);
      setPublishResultForm((current) => ({ ...current, taskId: data.id }));
      setWorkflowMessage(`已创建发布任务：${data.packageTitle ?? data.id}`);
    } catch {
      setWorkflowMessage("创建发布任务失败：请确认发布包已确认且 API 已启动。");
    }
  }

  async function recordPublishResult() {
    if (!publishResultForm.taskId.trim()) {
      setWorkflowMessage("请先选择或填写发布任务 ID。");
      return;
    }
    try {
      const resultResponse = await fetch(
        `http://127.0.0.1:8000/api/publish-tasks/${publishResultForm.taskId}/result`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            publishedUrl: publishResultForm.publishedUrl || "https://example.com/published/travel-post",
            status: "published",
            note: "运营手动回填发布结果",
          }),
        },
      );
      const updatedTask: PublishTask = await resultResponse.json();
      await fetch("http://127.0.0.1:8000/api/metrics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          publishTaskId: publishResultForm.taskId,
          views: Number(publishResultForm.views) || 0,
          likes: Number(publishResultForm.likes) || 0,
          saves: Number(publishResultForm.saves) || 0,
          comments: Number(publishResultForm.comments) || 0,
          shares: Number(publishResultForm.shares) || 0,
          leads: Number(publishResultForm.leads) || 0,
          conversions: Number(publishResultForm.conversions) || 0,
        }),
      });
      setTasks((current) => current.map((task) => (task.id === updatedTask.id ? updatedTask : task)));
      setWorkflowMessage("发布链接和首日数据已回填。");
    } catch {
      setWorkflowMessage("回填失败：请确认任务 ID 和 API 状态。");
    }
  }

  async function createAsset() {
    if (!assetForm.title.trim() || !assetForm.fileUrl.trim()) {
      setAssetMessage("请至少填写素材标题和文件地址。");
      return;
    }

    try {
      await fetch("http://127.0.0.1:8000/api/media-assets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: assetForm.type,
          title: assetForm.title,
          destination: assetForm.destination || undefined,
          scene: assetForm.scene || undefined,
          licenseStatus: assetForm.licenseStatus,
          consentStatus: assetForm.consentStatus,
          usageScope: splitList(assetForm.usageScope),
          source: assetForm.source || undefined,
          owner: assetForm.owner || undefined,
          tags: splitList(assetForm.tags),
          fileUrl: assetForm.fileUrl,
        }),
      });
      setAssetMessage("素材已登记，授权状态会进入合规汇总。");
      setAssetForm((current) => ({ ...current, title: "", fileUrl: "", tags: "" }));
      await refreshAssets();
    } catch {
      setAssetMessage("素材登记失败：请确认 API 已启动。");
    }
  }

  async function attachAssetToLatestDraft(assetId: string) {
    const latestDraft = creativeDrafts[0];
    if (!latestDraft) {
      setAssetMessage("请先在视频工厂保存一个创意草稿，再绑定素材。");
      return;
    }

    try {
      await fetch(`http://127.0.0.1:8000/api/media-assets/${assetId}/usage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draftId: latestDraft.id,
          usage: "reference",
          note: `素材绑定到草稿：${latestDraft.title}`,
        }),
      });
      setAssetMessage(`已绑定到最近草稿：${latestDraft.title}`);
    } catch {
      setAssetMessage("绑定失败：请确认素材已授权，人物同意已通过，且 API 已启动。");
    }
  }

  return (
    <main className="app">
      <aside className="sidebar">
        <div className="brand">
          <Plane size={24} />
          <div>
            <strong>TravelMatrix AI</strong>
            <span>旅游内容矩阵</span>
          </div>
        </div>
        <nav>
          {navItems.map(([Icon, label]) => (
            <button
              className={label === activeView ? "active" : ""}
              key={label}
              onClick={() => setActiveView(label)}
            >
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <h1>{activeView}</h1>
            <p>{viewSubtitle(activeView)}</p>
            <p className="status-line">{workflowMessage}</p>
          </div>
          <button className="primary" onClick={() => void generatePosts(selectedProductId)}>
            <Sparkles size={18} />
            {isGenerating ? "生成中" : "生成内容"}
          </button>
          <div className="user-badge">
            <strong>{user.name}</strong>
            <span>{user.workspace}</span>
          </div>
        </header>

        <section className="metrics">
          <Metric icon={<FileText />} label="内容草稿" value="18" note="6 个平台版本" />
          <Metric icon={<ShieldCheck />} label="待审核" value="7" note="2 条高风险" />
          <Metric icon={<CalendarDays />} label="今日发布" value="9" note="3 条需人工确认" />
          <Metric
            icon={<Users />}
            label="累计线索"
            value={String(analytics.totalLeads)}
            note={`成交 ${analytics.totalConversions} 单`}
          />
        </section>

        {activeView === "工作台" || activeView === "内容工厂" ? (
        <section className="workspace">
          <div className="panel large">
            <div className="panel-head">
              <div>
                <h2>AI 多平台内容生成</h2>
                <p>接口状态：{apiStatus}</p>
              </div>
              <span className="risk">中风险：价格需人工确认</span>
            </div>

            <div className="toolbar">
              <label>
                旅游产品
                <select
                  value={selectedProductId}
                  onChange={(event) => setSelectedProductId(event.target.value)}
                >
                  {products.map((item) => (
                    <option value={item.id} key={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </label>
              <button className="secondary" onClick={() => void generatePosts(selectedProductId)}>
                <Sparkles size={16} />
                重新生成
              </button>
              <button className="secondary" onClick={() => void saveAllVariantsAsDrafts()}>
                <FileText size={16} />
                保存全部草稿
              </button>
            </div>

            <div className="product-strip">
              <div>
                <span>目的地</span>
                <strong>{selectedProduct.destination}</strong>
              </div>
              <div>
                <span>人群</span>
                <strong>{selectedProduct.target_audience}</strong>
              </div>
              <div>
                <span>价格</span>
                <strong>{selectedProduct.reference_price}</strong>
              </div>
            </div>

            <div className="chips">
              {selectedProduct.selling_points.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>

            <div className="variant-grid">
              {(variants.length ? variants : buildFallbackVariants()).map((variant) => (
                <article key={variant.id} className="variant">
                  <div className="variant-head">
                    <h3>{platformMap[variant.platform]}</h3>
                    <span>{riskLabel(variant.riskLevel)}</span>
                  </div>
                  <strong>{variant.title}</strong>
                  <p>{variant.body}</p>
                  <button className="mini-action" onClick={() => void saveVariantAsDraft(variant)}>
                    保存草稿
                  </button>
                </article>
              ))}
            </div>
          </div>

          <div className="stack">
            <div className="panel">
              <div className="panel-head compact">
                <h2>发布日历</h2>
                <CalendarDays size={20} />
              </div>
              {(tasks.length ? tasks : buildFallbackTasks()).slice(0, 4).map((task) => (
                <div className="schedule-row" key={task.id}>
                  <time>{formatTime(task.scheduledAt)}</time>
                  <div>
                    <strong>{platformMap[task.platform]}</strong>
                    <span>{task.accountName}</span>
                  </div>
                  <em>{publishMethodLabel(task.publishMethod)}</em>
                </div>
              ))}
            </div>

            <div className="panel">
              <div className="panel-head compact">
                <h2>合规检查</h2>
                <CheckCircle2 size={20} />
              </div>
              <ul className="checks">
                <li>人物素材授权：通过</li>
                <li>价格表达：需确认</li>
                <li>平台敏感词：通过</li>
                <li>重复内容：需改写</li>
              </ul>
            </div>

            <div className="panel">
              <div className="panel-head compact">
                <h2>发布策略</h2>
                <Megaphone size={20} />
              </div>
              <p className="plain">
                {analytics.recommendation}
              </p>
            </div>
          </div>
        </section>
        ) : (
          <ModuleView
            view={activeView}
            products={products}
            tasks={tasks.length ? tasks : buildFallbackTasks()}
            assets={assets}
            assetSummary={assetSummary}
            assetForm={assetForm}
            assetMessage={assetMessage}
            analytics={analytics}
            selectedProduct={selectedProduct}
            creativePackage={creativePackage}
            talkingVideo={talkingVideo}
            referenceText={referenceText}
            referenceAnalysis={referenceAnalysis}
            batchTalking={batchTalking}
            creativeDrafts={creativeDrafts}
            reviewItems={reviewItems}
            publishPackage={publishPackage}
            publishConfirmations={publishConfirmations}
            publishResultForm={publishResultForm}
            workflowMessage={workflowMessage}
            onGenerateCreative={() => void generateCreativePackage(selectedProductId)}
            onGenerateTalkingVideo={() => void generateTalkingVideo(selectedProductId)}
            onReferenceTextChange={setReferenceText}
            onAnalyzeReference={() => void analyzeTalkingReference()}
            onGenerateBatchTalking={() => void generateBatchTalkingVideos()}
            onSaveTalkingDraft={(plan) => void saveTalkingVideoAsDraft(plan)}
            onSaveCreative={() => void saveCurrentCreativeDraft()}
            onSubmitCreative={(draftId) => void submitCreativeDraft(draftId)}
            onExportPublishPackage={(draftId) => void exportPublishPackage(draftId)}
            onConfirmPublishPackage={() => void confirmPublishPackage()}
            onCreatePublishTask={() => void createPublishTaskFromPackage()}
            onPublishResultFormChange={setPublishResultForm}
            onRecordPublishResult={() => void recordPublishResult()}
            onSaveVariantDraft={(variant) => void saveVariantAsDraft(variant)}
            onSaveAllVariantDrafts={() => void saveAllVariantsAsDrafts()}
            onReviewDecision={(reviewId, decision) => void decideReview(reviewId, decision)}
            onAssetFormChange={setAssetForm}
            onCreateAsset={() => void createAsset()}
            onAttachAsset={(assetId) => void attachAssetToLatestDraft(assetId)}
          />
        )}
      </section>
    </main>
  );
}

function riskLabel(level: ApiVariant["riskLevel"]) {
  return level === "high" ? "高风险" : level === "medium" ? "需复核" : "低风险";
}

function buildFallbackVariants(): ApiVariant[] {
  return platformPayload.map((platform) => ({
    id: `fallback-${platform}`,
    platform,
    title: `${platformMap[platform]}内容示例`,
    body: "后端未连接时显示离线演示内容。启动 API 后会自动加载真实接口返回的多平台版本。",
    hashtags: [platformMap[platform], "旅行攻略"],
    coverText: "旅游攻略",
    riskLevel: platform === "douban" || platform === "xiaohongshu" ? "medium" : "low",
    status: "draft",
  }));
}

function buildFallbackTasks(): PublishTask[] {
  const base = new Date();
  return [
    {
      id: "fallback-task-xhs",
      platform: "xiaohongshu",
      accountName: "亲子账号",
      scheduledAt: new Date(base.getTime() + 2 * 60 * 60 * 1000).toISOString(),
      publishMethod: "manual_assist",
      status: "manual_required",
    },
    {
      id: "fallback-task-dy",
      platform: "douyin",
      accountName: "海岛账号",
      scheduledAt: new Date(base.getTime() + 5 * 60 * 60 * 1000).toISOString(),
      publishMethod: "manual_assist",
      status: "scheduled",
    },
    {
      id: "fallback-task-wb",
      platform: "weibo",
      accountName: "官方账号",
      scheduledAt: new Date(base.getTime() + 8 * 60 * 60 * 1000).toISOString(),
      publishMethod: "api",
      status: "scheduled",
    },
  ];
}

function buildFallbackAssets(): MediaAsset[] {
  return [
    {
      id: "fallback-asset-image",
      type: "image",
      title: "巴厘岛海边酒店外景",
      destination: "巴厘岛",
      scene: "酒店",
      licenseStatus: "approved",
      consentStatus: "not_applicable",
      usageScope: ["商业推广", "小红书", "抖音"],
      source: "品牌自有素材",
      owner: "TravelMatrix",
      tags: ["海边", "酒店", "度假"],
      fileUrl: "/demo-assets/bali-beach.jpg",
    },
    {
      id: "fallback-asset-video",
      type: "video",
      title: "龙目岛出海短视频",
      destination: "龙目岛",
      scene: "出海",
      licenseStatus: "approved",
      consentStatus: "approved",
      usageScope: ["商业推广", "短视频", "发布包"],
      source: "供应商授权",
      owner: "龙目岛地接",
      tags: ["出海", "浮潜", "短视频"],
      fileUrl: "/demo-assets/lombok-boat.mp4",
    },
  ];
}

function buildFallbackCreativePackage(product: TravelProduct): CreativePackage {
  return {
    id: "fallback-creative",
    product,
    platform: "douyin",
    objective: "短视频引流",
    hook: `${product.destination}${product.days}天怎么玩更省心？先看这条路线逻辑。`,
    coverTitle: `${product.destination}${product.days}天省心玩法`,
    videoScript: [
      `第一次去${product.destination}，别先急着订行程。`,
      `这条线路把${product.selling_points.slice(0, 2).join("、")}放在前面。`,
      `适合${product.target_audience}，节奏不用赶。`,
      "人数和日期发来，先帮你看适合哪条线。",
    ].join("\n"),
    imagePrompts: [
      `${product.destination}旅行封面图，真实自然光，清爽排版，突出攻略标题`,
      `${product.destination}旅游产品卖点图，展示${product.selling_points.slice(0, 4).join("、")}，商业旅拍质感`,
      `面向${product.target_audience}的旅行软文配图，真实体验、低营销感、竖版构图`,
    ],
    advertorial: `${product.name}适合${product.target_audience}，亮点包括${product.selling_points.join("、")}。参考价格为${product.reference_price}，实际出行前建议确认酒店、车导、天气和可用名额。`,
    storyboard: [
      {
        order: 1,
        shot: "开场近景 + 快切目的地画面",
        visualPrompt: `${product.destination}旅行短视频开场，海岛阳光、自然真实、竖屏构图`,
        voiceover: `第一次去${product.destination}，别先急着订行程。`,
        subtitle: `第一次去${product.destination}先看这条`,
        assetHint: "目的地大景、酒店外观、出海镜头",
      },
      {
        order: 2,
        shot: "卖点连拍",
        visualPrompt: `${product.destination}旅行体验拼贴，包含${product.selling_points.slice(0, 2).join("和")}`,
        voiceover: `重点体验：${product.selling_points.slice(0, 3).join("、")}。`,
        subtitle: "核心体验先安排",
        assetHint: "产品卖点对应图片或短视频素材",
      },
      {
        order: 3,
        shot: "人群场景",
        visualPrompt: `适合${product.target_audience}的${product.destination}旅行场景`,
        voiceover: `更适合${product.target_audience}，节奏不用赶。`,
        subtitle: "适合人群清楚说明",
        assetHint: "人物素材需确认授权",
      },
      {
        order: 4,
        shot: "咨询引导",
        visualPrompt: `${product.destination}旅行攻略封面图，干净排版，标题留白`,
        voiceover: "把人数和出行日期发来，先帮你看适合哪条线。",
        subtitle: "人数 + 日期，先做方案",
        assetHint: "封面图、品牌 logo、客服二维码占位",
      },
    ],
    complianceNotes: [
      "价格、库存、签证、安全等信息必须人工复核。",
      "人物图片、视频、数字人素材必须确认商业授权。",
      "先生成发布包，由运营确认后再发布。",
    ],
  };
}

function buildFallbackIpProfile(): IpProfile {
  return {
    id: "travel_consultant",
    name: "东南亚旅行顾问",
    persona: "长期做海岛线路规划的旅行顾问，擅长把复杂行程讲清楚",
    audience: "第一次去东南亚、怕踩坑、需要中文服务的客人",
    tone: "专业、直接、低营销感",
    signature: "先讲避坑逻辑，再给省心方案",
    prohibitedClaims: ["保证最低价", "绝对安全", "100%满意"],
  };
}

function buildFallbackTalkingVideo(product: TravelProduct): TalkingVideoPlan {
  const ipProfile = buildFallbackIpProfile();
  const teleprompter = [
    `第一次去${product.destination}，最容易踩坑的不是景点，而是行程顺序。`,
    `我是${ipProfile.name}，平时主要帮${ipProfile.audience}做线路。`,
    `如果你看的是${product.name}，先别只比价格，先看节奏和服务边界。`,
    `这条线路的重点是${product.selling_points.slice(0, 4).join("、")}。`,
    "你把出行日期、人数和预算发来，我先帮你判断哪条线更合适。",
  ];
  return {
    id: "fallback-talking-video",
    product,
    ipProfile,
    platform: "douyin",
    topic: "第一次出行避坑",
    titleOptions: [
      `第一次去${product.destination}，先避开这个行程坑`,
      `${product.destination}${product.days}天怎么安排更省心？`,
      `别只比价格，${product.destination}行程先看这3点`,
    ],
    viralStructure: ["痛点钩子", "身份背书", "避坑解释", "方案给法", "轻转化"],
    teleprompter,
    script: teleprompter.join("\n"),
    shotPlan: [
      {
        order: 1,
        shot: "真人或数字人半身口播",
        visualPrompt: `${ipProfile.name}面对镜头讲解${product.destination}旅行避坑`,
        voiceover: teleprompter[0],
        subtitle: teleprompter[0],
        assetHint: "IP形象、数字人或真人口播素材；必须确认授权",
      },
      {
        order: 2,
        shot: "路线卖点插入画面",
        visualPrompt: `${product.destination}旅行卖点画面`,
        voiceover: teleprompter[3],
        subtitle: "先看节奏，再看价格",
        assetHint: "目的地素材、酒店、出海、景点镜头",
      },
    ],
    coverText: `${product.destination}避坑口播`,
    callToAction: "评论或私信发送人数、日期、预算，人工确认后给线路建议。",
    complianceNotes: [
      "不得承诺最低价、绝对安全、保证满意等绝对化结果。",
      "真人形象、数字人、声音克隆必须保留授权记录和使用期限。",
    ],
  };
}

function talkingVideoToCreativePackage(plan: TalkingVideoPlan): CreativePackage {
  return {
    id: `creative_${plan.id}`,
    product: plan.product,
    platform: plan.platform,
    objective: "IP口播引流",
    hook: plan.teleprompter[0] ?? plan.titleOptions[0],
    coverTitle: plan.coverText,
    videoScript: plan.script,
    imagePrompts: plan.shotPlan.map((scene) => scene.visualPrompt),
    advertorial: `${plan.titleOptions[0]}\n\n${plan.script}\n\n${plan.callToAction}`,
    storyboard: plan.shotPlan,
    complianceNotes: plan.complianceNotes,
  };
}

function postVariantToCreativePackage(variant: ApiVariant, product: TravelProduct): CreativePackage {
  return {
    id: `creative_${variant.id}`,
    product,
    platform: variant.platform,
    objective: "多平台内容引流",
    hook: variant.title,
    coverTitle: variant.coverText,
    videoScript: variant.body,
    imagePrompts: [
      `${product.destination}旅行封面图，标题为“${variant.coverText}”，真实旅拍风格`,
      `${product.destination}内容配图，突出${product.selling_points.slice(0, 3).join("、")}`,
    ],
    advertorial: `${variant.title}\n\n${variant.body}\n\n${variant.hashtags.map((tag) => `#${tag}`).join(" ")}`,
    storyboard: [
      {
        order: 1,
        shot: "平台内容封面",
        visualPrompt: `${product.destination}旅行封面图，适合${platformMap[variant.platform]}发布`,
        voiceover: variant.title,
        subtitle: variant.coverText,
        assetHint: "封面图、目的地素材、品牌标识",
      },
      {
        order: 2,
        shot: "正文内容展开",
        visualPrompt: `${product.destination}旅行内容配图，真实体验、低营销感`,
        voiceover: variant.body,
        subtitle: "行程亮点和咨询引导",
        assetHint: "产品卖点图片或短视频素材",
      },
    ],
    complianceNotes: [
      "价格、库存、签证、安全等信息需要人工复核。",
      "素材授权和人物授权必须确认后才能发布。",
      "平台内容需要人工确认后进入发布任务。",
    ],
  };
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

function publishMethodLabel(method: PublishTask["publishMethod"]) {
  if (method === "api") return "API";
  if (method === "enterprise_api") return "企业接口";
  return "人工确认";
}

function viewSubtitle(view: ViewName) {
  const subtitles: Record<ViewName, string> = {
    工作台: "今天优先处理待审核、待发布和素材授权风险。",
    产品库: "管理线路、价格、行程、卖点和适合人群。",
    素材库: "管理图片、视频、人物素材和授权状态。",
    内容工厂: "选择旅游产品并生成多平台内容版本。",
    视频工厂: "生成短视频脚本、分镜、配音、字幕和封面。",
    审核中心: "集中处理敏感词、版权、人物授权和发布风险。",
    发布日历: "按平台、账号和时间管理发布任务。",
    数据看板: "查看平台、账号、产品和线索转化效果。",
  };
  return subtitles[view];
}

function ModuleView({
  view,
  products,
  tasks,
  assets,
  assetSummary,
  assetForm,
  assetMessage,
  analytics,
  selectedProduct,
  creativePackage,
  talkingVideo,
  referenceText,
  referenceAnalysis,
  batchTalking,
  creativeDrafts,
  reviewItems,
  publishPackage,
  publishConfirmations,
  publishResultForm,
  workflowMessage,
  onGenerateCreative,
  onGenerateTalkingVideo,
  onReferenceTextChange,
  onAnalyzeReference,
  onGenerateBatchTalking,
  onSaveTalkingDraft,
  onSaveCreative,
  onSubmitCreative,
  onExportPublishPackage,
  onConfirmPublishPackage,
  onCreatePublishTask,
  onPublishResultFormChange,
  onRecordPublishResult,
  onSaveVariantDraft,
  onSaveAllVariantDrafts,
  onReviewDecision,
  onAssetFormChange,
  onCreateAsset,
  onAttachAsset,
}: {
  view: ViewName;
  products: TravelProduct[];
  tasks: PublishTask[];
  assets: MediaAsset[];
  assetSummary: AssetComplianceSummary;
  assetForm: {
    title: string;
    type: MediaAsset["type"];
    destination: string;
    scene: string;
    licenseStatus: string;
    consentStatus: string;
    usageScope: string;
    source: string;
    owner: string;
    tags: string;
    fileUrl: string;
  };
  assetMessage: string;
  analytics: AnalyticsOverview;
  selectedProduct: TravelProduct;
  creativePackage: CreativePackage;
  talkingVideo: TalkingVideoPlan;
  referenceText: string;
  referenceAnalysis: TalkingReferenceAnalysis | null;
  batchTalking: BatchTalkingVideoResponse | null;
  creativeDrafts: CreativeDraft[];
  reviewItems: ReviewItem[];
  publishPackage: PublishPackage | null;
  publishConfirmations: PublishPackageConfirmation[];
  publishResultForm: {
    taskId: string;
    publishedUrl: string;
    views: string;
    likes: string;
    saves: string;
    comments: string;
    shares: string;
    leads: string;
    conversions: string;
  };
  workflowMessage: string;
  onGenerateCreative: () => void;
  onGenerateTalkingVideo: () => void;
  onReferenceTextChange: (value: string) => void;
  onAnalyzeReference: () => void;
  onGenerateBatchTalking: () => void;
  onSaveTalkingDraft: (plan: TalkingVideoPlan) => void;
  onSaveCreative: () => void;
  onSubmitCreative: (draftId: string) => void;
  onExportPublishPackage: (draftId: string) => void;
  onConfirmPublishPackage: () => void;
  onCreatePublishTask: () => void;
  onPublishResultFormChange: React.Dispatch<React.SetStateAction<typeof publishResultForm>>;
  onRecordPublishResult: () => void;
  onSaveVariantDraft: (variant: ApiVariant) => void;
  onSaveAllVariantDrafts: () => void;
  onReviewDecision: (reviewId: string, decision: ReviewItem["status"]) => void;
  onAssetFormChange: React.Dispatch<React.SetStateAction<typeof assetForm>>;
  onCreateAsset: () => void;
  onAttachAsset: (assetId: string) => void;
}) {
  if (view === "产品库") {
    return (
      <section className="module-grid">
        {products.map((item) => (
          <article className="panel module-card" key={item.id}>
            <h2>{item.name}</h2>
            <p>{item.destination} · {item.days} 天 · {item.reference_price}</p>
            <div className="chips">
              {item.selling_points.map((point) => (
                <span key={point}>{point}</span>
              ))}
            </div>
          </article>
        ))}
      </section>
    );
  }

  if (view === "素材库") {
    return (
      <section className="asset-layout">
        <div className="panel large">
          <div className="panel-head">
            <div>
              <h2>素材登记</h2>
              <p>{assetMessage}</p>
            </div>
            <Images size={20} />
          </div>

          <div className="asset-form">
            <label>
              标题
              <input
                value={assetForm.title}
                onChange={(event) => onAssetFormChange((current) => ({ ...current, title: event.target.value }))}
                placeholder="例如：巴厘岛海边酒店封面图"
              />
            </label>
            <label>
              类型
              <select
                value={assetForm.type}
                onChange={(event) =>
                  onAssetFormChange((current) => ({
                    ...current,
                    type: event.target.value as MediaAsset["type"],
                  }))
                }
              >
                <option value="image">图片</option>
                <option value="video">视频</option>
                <option value="audio">音频</option>
                <option value="document">文档</option>
              </select>
            </label>
            <label>
              目的地
              <input
                value={assetForm.destination}
                onChange={(event) => onAssetFormChange((current) => ({ ...current, destination: event.target.value }))}
                placeholder="巴厘岛"
              />
            </label>
            <label>
              场景
              <input
                value={assetForm.scene}
                onChange={(event) => onAssetFormChange((current) => ({ ...current, scene: event.target.value }))}
                placeholder="酒店 / 出海 / 人物"
              />
            </label>
            <label>
              授权状态
              <select
                value={assetForm.licenseStatus}
                onChange={(event) =>
                  onAssetFormChange((current) => ({ ...current, licenseStatus: event.target.value }))
                }
              >
                <option value="pending">待确认</option>
                <option value="approved">已授权</option>
                <option value="restricted">限制使用</option>
                <option value="expired">已过期</option>
              </select>
            </label>
            <label>
              人物同意
              <select
                value={assetForm.consentStatus}
                onChange={(event) =>
                  onAssetFormChange((current) => ({ ...current, consentStatus: event.target.value }))
                }
              >
                <option value="not_applicable">无需人物授权</option>
                <option value="approved">人物已授权</option>
                <option value="pending">人物待确认</option>
                <option value="expired">人物授权过期</option>
              </select>
            </label>
            <label>
              使用范围
              <input
                value={assetForm.usageScope}
                onChange={(event) => onAssetFormChange((current) => ({ ...current, usageScope: event.target.value }))}
                placeholder="商业推广,小红书,抖音"
              />
            </label>
            <label>
              标签
              <input
                value={assetForm.tags}
                onChange={(event) => onAssetFormChange((current) => ({ ...current, tags: event.target.value }))}
                placeholder="海边,酒店,封面"
              />
            </label>
            <label>
              来源
              <input
                value={assetForm.source}
                onChange={(event) => onAssetFormChange((current) => ({ ...current, source: event.target.value }))}
                placeholder="品牌自有素材 / 供应商授权"
              />
            </label>
            <label>
              归属方
              <input
                value={assetForm.owner}
                onChange={(event) => onAssetFormChange((current) => ({ ...current, owner: event.target.value }))}
                placeholder="TravelMatrix / 地接社 / 摄影师"
              />
            </label>
            <label className="span-2">
              文件地址
              <input
                value={assetForm.fileUrl}
                onChange={(event) => onAssetFormChange((current) => ({ ...current, fileUrl: event.target.value }))}
                placeholder="/demo-assets/bali-cover.jpg"
              />
            </label>
            <button className="primary" onClick={onCreateAsset}>
              <Images size={16} />
              登记素材
            </button>
          </div>
        </div>

        <div className="stack">
          <div className="panel">
            <div className="panel-head compact">
              <h2>授权概览</h2>
              <ShieldCheck size={20} />
            </div>
            <div className="asset-summary">
              <span>总素材 <strong>{assetSummary.totalAssets}</strong></span>
              <span>已授权 <strong>{assetSummary.approvedAssets}</strong></span>
              <span>待确认 <strong>{assetSummary.pendingAssets}</strong></span>
              <span>不可发布 <strong>{assetSummary.blockedAssets}</strong></span>
            </div>
          </div>
        </div>

        <div className="asset-list span-2">
          {(assets.length ? assets : buildFallbackAssets()).map((asset) => (
            <article className="panel module-card" key={asset.id}>
              <div className="asset-head">
                <h2>{asset.title}</h2>
                <span>{assetStatusLabel(asset.licenseStatus)}</span>
              </div>
              <p>
                {asset.type} · {asset.destination ?? "未标目的地"} · {asset.scene ?? "未标场景"}
              </p>
              <p>
                {consentStatusLabel(asset.consentStatus)} · {asset.owner ?? "未标归属方"} · {asset.source ?? "未标来源"}
              </p>
              <div className="chips">
                {asset.usageScope.map((scope) => (
                  <span key={scope}>{scope}</span>
                ))}
                {asset.tags.map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>
              <div className="row-actions">
                <button onClick={() => onAttachAsset(asset.id)}>绑定最近草稿</button>
              </div>
            </article>
          ))}
        </div>
      </section>
    );
  }

  if (view === "发布日历") {
    return (
      <section className="publish-layout">
        <div className="panel">
          <div className="panel-head compact">
            <h2>近期发布任务</h2>
            <CalendarDays size={20} />
          </div>
          {tasks.map((task) => (
            <div className="schedule-row wide" key={task.id}>
              <time>{formatTime(task.scheduledAt)}</time>
              <div>
                <strong>{platformMap[task.platform]} · {task.accountName}</strong>
                <span>{task.packageTitle ?? task.status}</span>
                {task.publishedUrl ? <span>{task.publishedUrl}</span> : null}
              </div>
              <em>{publishMethodLabel(task.publishMethod)}</em>
            </div>
          ))}
        </div>

        <div className="panel">
          <div className="panel-head compact">
            <h2>结果与首日数据</h2>
            <BarChart3 size={20} />
          </div>
          <div className="result-form">
            <label>
              发布任务 ID
              <input
                value={publishResultForm.taskId}
                onChange={(event) =>
                  onPublishResultFormChange((current) => ({ ...current, taskId: event.target.value }))
                }
                placeholder="task_xxx"
              />
            </label>
            <label className="span-2">
              发布链接
              <input
                value={publishResultForm.publishedUrl}
                onChange={(event) =>
                  onPublishResultFormChange((current) => ({ ...current, publishedUrl: event.target.value }))
                }
                placeholder="https://..."
              />
            </label>
            {(["views", "likes", "saves", "comments", "shares", "leads", "conversions"] as const).map((key) => (
              <label key={key}>
                {metricInputLabel(key)}
                <input
                  value={publishResultForm[key]}
                  onChange={(event) =>
                    onPublishResultFormChange((current) => ({ ...current, [key]: event.target.value }))
                  }
                />
              </label>
            ))}
            <button className="primary" onClick={onRecordPublishResult}>
              <CheckCircle2 size={16} />
              回填发布结果
            </button>
          </div>
        </div>
      </section>
    );
  }

  if (view === "数据看板") {
    return (
      <section className="module-grid">
        <Metric icon={<BarChart3 />} label="总浏览" value={String(analytics.totalViews)} note={`最佳平台：${analytics.bestPlatform}`} />
        <Metric icon={<Users />} label="线索" value={String(analytics.totalLeads)} note={`成交 ${analytics.totalConversions} 单`} />
        <article className="panel module-card span-2">
          <h2>AI 复盘建议</h2>
          <p>{analytics.recommendation}</p>
        </article>
      </section>
    );
  }

  if (view === "视频工厂") {
    return (
      <section className="creative-layout">
        <div className="panel large">
          <div className="panel-head">
            <div>
              <h2>视频 / 图片 / 软文创意包</h2>
              <p>{selectedProduct.name} · {platformMap[creativePackage.platform]} · {creativePackage.objective}</p>
            </div>
            <button className="secondary" onClick={onGenerateCreative}>
              <Clapperboard size={16} />
              生成创意包
            </button>
          </div>

          <div className="workflow-actions">
            <span>{workflowMessage}</span>
            <button className="primary compact-button" onClick={onSaveCreative}>
              <FileText size={16} />
              保存草稿
            </button>
          </div>

          <div className="creative-summary">
            <div>
              <span>前三秒钩子</span>
              <strong>{creativePackage.hook}</strong>
            </div>
            <div>
              <span>封面标题</span>
              <strong>{creativePackage.coverTitle}</strong>
            </div>
          </div>

          <div className="storyboard">
            {creativePackage.storyboard.map((scene) => (
              <article className="scene-card" key={`${creativePackage.id}-${scene.order}`}>
                <span>{String(scene.order).padStart(2, "0")}</span>
                <div>
                  <h3>{scene.shot}</h3>
                  <p>{scene.voiceover}</p>
                  <em>{scene.subtitle}</em>
                  <small>{scene.assetHint}</small>
                </div>
              </article>
            ))}
          </div>
        </div>

        <div className="stack">
          <div className="panel ip-agent-panel">
            <div className="panel-head compact">
              <h2>IP口播智能体</h2>
              <Clapperboard size={20} />
            </div>
            <div className="ip-profile">
              <strong>{talkingVideo.ipProfile.name}</strong>
              <span>{talkingVideo.ipProfile.persona}</span>
              <em>{talkingVideo.ipProfile.signature}</em>
            </div>
            <button className="secondary full-button" onClick={onGenerateTalkingVideo}>
              <Sparkles size={16} />
              生成口播方案
            </button>
            <div className="script-block">
              <strong>爆款结构</strong>
              <ol>
                {talkingVideo.viralStructure.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ol>
            </div>
            <div className="script-block">
              <strong>提词器分段</strong>
              {talkingVideo.teleprompter.map((line) => (
                <p key={line}>{line}</p>
              ))}
            </div>
          </div>

          <div className="panel ip-agent-panel">
            <div className="panel-head compact">
              <h2>爆款结构拆解</h2>
              <Sparkles size={20} />
            </div>
            <label className="reference-box">
              参考口播文本
              <textarea
                value={referenceText}
                onChange={(event) => onReferenceTextChange(event.target.value)}
              />
            </label>
            <button className="secondary full-button" onClick={onAnalyzeReference}>
              <Sparkles size={16} />
              拆解并原创改写
            </button>
            {referenceAnalysis ? (
              <div className="script-block">
                <strong>{referenceAnalysis.hookType}</strong>
                <ol>
                  {referenceAnalysis.structure.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
                <strong>节奏提醒</strong>
                {referenceAnalysis.rhythmNotes.map((item) => (
                  <p key={item}>{item}</p>
                ))}
                <strong>原创边界</strong>
                {referenceAnalysis.originalityWarnings.map((item) => (
                  <p key={item}>{item}</p>
                ))}
              </div>
            ) : (
              <p className="plain">输入参考口播后，只学习结构和节奏，不复制原文。</p>
            )}
          </div>

          <div className="panel ip-agent-panel">
            <div className="panel-head compact">
              <h2>批量口播生产</h2>
              <FileText size={20} />
            </div>
            <button className="secondary full-button" onClick={onGenerateBatchTalking}>
              <Sparkles size={16} />
              生成10条口播
            </button>
            {batchTalking ? (
              <div className="batch-list">
                {batchTalking.items.map((item) => (
                  <article className="batch-item" key={item.id}>
                    <strong>{item.titleOptions[0]}</strong>
                    <span>{item.topic} · {item.coverText}</span>
                    <p>{item.teleprompter[0]}</p>
                    <button onClick={() => onSaveTalkingDraft(item)}>保存草稿</button>
                  </article>
                ))}
              </div>
            ) : (
              <p className="plain">一次生成不同角度的口播选题，优质条目可直接进入草稿审核流程。</p>
            )}
          </div>

          <div className="panel">
            <div className="panel-head compact">
              <h2>创意草稿</h2>
              <FileText size={20} />
            </div>
            <div className="draft-list">
              {creativeDrafts.length ? (
                creativeDrafts.slice(0, 5).map((draft) => (
                  <article className="draft-row" key={draft.id}>
                    <div>
                      <strong>{draft.title}</strong>
                      <span>{draftStatusLabel(draft.status)} · {formatDateTime(draft.updatedAt)}</span>
                    </div>
                    <div className="row-actions">
                      <button onClick={() => onSubmitCreative(draft.id)}>送审</button>
                      <button onClick={() => onExportPublishPackage(draft.id)}>发布包</button>
                    </div>
                  </article>
                ))
              ) : (
                <p className="plain">还没有保存的创意草稿。</p>
              )}
            </div>
          </div>

          {publishPackage ? (
            <div className="panel">
              <div className="panel-head compact">
                <h2>发布包详情</h2>
                <Megaphone size={20} />
              </div>
              <div className="publish-package">
                <strong>{publishPackage.title}</strong>
                <span>{platformMap[publishPackage.platform]} · {publishPackage.finalStatus === "confirmed" ? "已确认" : "待确认"}</span>
                <p>{publishPackage.copy}</p>
                <span>{publishPackage.hashtags.map((tag) => `#${tag}`).join(" ")}</span>
                <div className="package-section">
                  <b>平台适配</b>
                  {publishPackage.platformAdaptation.map((item) => (
                    <small key={item}>{item}</small>
                  ))}
                </div>
                <div className="package-section">
                  <b>素材清单</b>
                  {publishPackage.assetChecklist.map((item) => (
                    <small key={item}>{item}</small>
                  ))}
                </div>
                <div className="package-section">
                  <b>运营确认</b>
                  {publishPackage.operatorChecklist.map((item) => (
                    <small key={item}>✓ {item}</small>
                  ))}
                </div>
                {publishConfirmations.length ? (
                  <div className="package-section">
                    <b>确认记录</b>
                    {publishConfirmations.map((item) => (
                      <small key={item.id}>{item.operator} · {formatDateTime(item.confirmedAt)}</small>
                    ))}
                  </div>
                ) : null}
                <button className="secondary full-button" onClick={onConfirmPublishPackage}>
                  <CheckCircle2 size={16} />
                  人工确认发布包
                </button>
                <button className="primary compact-button" onClick={onCreatePublishTask}>
                  <CalendarDays size={16} />
                  创建发布任务
                </button>
              </div>
            </div>
          ) : null}

          <div className="panel">
            <div className="panel-head compact">
              <h2>图片提示词</h2>
              <Images size={20} />
            </div>
            <ul className="prompt-list">
              {creativePackage.imagePrompts.map((prompt) => (
                <li key={prompt}>{prompt}</li>
              ))}
            </ul>
          </div>

          <div className="panel">
            <div className="panel-head compact">
              <h2>软文草稿</h2>
              <FileText size={20} />
            </div>
            <p className="plain">{creativePackage.advertorial}</p>
          </div>

          <div className="panel">
            <div className="panel-head compact">
              <h2>合规提醒</h2>
              <ShieldCheck size={20} />
            </div>
            <ul className="checks">
              {creativePackage.complianceNotes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>
    );
  }

  if (view === "审核中心") {
    return (
      <section className="panel">
        <div className="panel-head compact">
          <h2>创意审核队列</h2>
          <ShieldCheck size={20} />
        </div>
        {reviewItems.length ? (
          reviewItems.map((item) => (
            <div className="review-row" key={item.id}>
              <div>
                <strong>{item.title}</strong>
                <span>{platformMap[item.platform]} · {reviewStatusLabel(item.status)} · {formatDateTime(item.submittedAt)}</span>
                {item.note ? <p>{item.note}</p> : null}
              </div>
              {item.status === "pending" ? (
                <div className="row-actions">
                  <button onClick={() => onReviewDecision(item.id, "approved")}>通过</button>
                  <button onClick={() => onReviewDecision(item.id, "rejected")}>驳回</button>
                </div>
              ) : (
                <em>{item.reviewer ?? "已处理"}</em>
              )}
            </div>
          ))
        ) : (
          <p className="plain">暂无待审核创意。先在视频工厂保存草稿并提交审核。</p>
        )}
      </section>
    );
  }

  const moduleCopy: Record<ViewName, string> = {
    工作台: "",
    产品库: "",
    素材库: "下一步会接入素材上传、标签筛选、授权状态和使用记录。",
    内容工厂: "",
    视频工厂: "下一步会接入短视频脚本、分镜、素材匹配、配音、字幕和多比例导出。",
    审核中心: "下一步会接入 AI 审核队列、人工通过、驳回原因和审计日志。",
    发布日历: "",
    数据看板: "",
  };

  return (
    <section className="panel empty-module">
      <h2>{view} MVP 模块</h2>
      <p>{moduleCopy[view]}</p>
    </section>
  );
}

function draftStatusLabel(status: CreativeDraft["status"]) {
  if (status === "pending_review") return "待审核";
  if (status === "approved") return "已通过";
  if (status === "rejected") return "已驳回";
  return "草稿";
}

function reviewStatusLabel(status: ReviewItem["status"]) {
  if (status === "approved") return "已通过";
  if (status === "rejected") return "已驳回";
  return "待审核";
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

function splitList(value: string) {
  return value
    .split(/[,，]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function assetStatusLabel(status: string) {
  if (status === "approved") return "已授权";
  if (status === "expired") return "已过期";
  if (status === "restricted") return "限制使用";
  return "待确认";
}

function consentStatusLabel(status: string) {
  if (status === "approved") return "人物已授权";
  if (status === "pending") return "人物待确认";
  if (status === "expired") return "人物授权过期";
  return "无需人物授权";
}

function metricInputLabel(key: keyof typeof metricLabels) {
  return metricLabels[key];
}

const metricLabels = {
  views: "浏览",
  likes: "点赞",
  saves: "收藏",
  comments: "评论",
  shares: "分享",
  leads: "线索",
  conversions: "成交",
};

function Metric({
  icon,
  label,
  value,
  note,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  note: string;
}) {
  return (
    <article className="metric">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{note}</p>
    </article>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
