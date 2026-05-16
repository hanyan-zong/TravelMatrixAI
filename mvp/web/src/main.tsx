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
  tags: string[];
  fileUrl: string;
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
  const [tasks, setTasks] = useState<PublishTask[]>([]);
  const [assets, setAssets] = useState<MediaAsset[]>([]);
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

    fetch("http://127.0.0.1:8000/api/media-assets")
      .then((response) => response.json())
      .then((data: MediaAsset[]) => setAssets(data))
      .catch(() => setAssets([]));
  }, []);

  useEffect(() => {
    void generatePosts(selectedProductId);
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
    } catch {
      setApiStatus("离线演示");
      setVariants(buildFallbackVariants());
    } finally {
      setIsGenerating(false);
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
            analytics={analytics}
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
      tags: ["出海", "浮潜", "短视频"],
      fileUrl: "/demo-assets/lombok-boat.mp4",
    },
  ];
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
  analytics,
}: {
  view: ViewName;
  products: TravelProduct[];
  tasks: PublishTask[];
  assets: MediaAsset[];
  analytics: AnalyticsOverview;
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
      <section className="module-grid">
        {(assets.length ? assets : buildFallbackAssets()).map((asset) => (
          <article className="panel module-card" key={asset.id}>
            <div className="asset-head">
              <h2>{asset.title}</h2>
              <span>{asset.licenseStatus === "approved" ? "已授权" : "待确认"}</span>
            </div>
            <p>
              {asset.type} · {asset.destination ?? "未标目的地"} · {asset.scene ?? "未标场景"}
            </p>
            <div className="chips">
              {asset.tags.map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>
          </article>
        ))}
      </section>
    );
  }

  if (view === "发布日历") {
    return (
      <section className="panel">
        <div className="panel-head compact">
          <h2>近期发布任务</h2>
          <CalendarDays size={20} />
        </div>
        {tasks.map((task) => (
          <div className="schedule-row wide" key={task.id}>
            <time>{formatTime(task.scheduledAt)}</time>
            <div>
              <strong>{platformMap[task.platform]} · {task.accountName}</strong>
              <span>{task.status}</span>
            </div>
            <em>{publishMethodLabel(task.publishMethod)}</em>
          </div>
        ))}
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
