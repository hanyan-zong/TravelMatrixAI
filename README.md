# TravelMatrixAI — 旅行社小红书内容自动生成平台

把你的旅行产品表，变成每天可直发的小红书图文内容。

## 快速体验

- **在线工作台**：https://bws-content-web.pages.dev
- **API 文档**：https://bws-social-content.fly.dev/docs

打开工作台 → 选一个日期 → 点"生成内容" → 得到文案 + 海报 → 复制/下载 → 发小红书。

## 它能做什么

1. **自动选品**：根据每天的主题，从你的产品库里自动挑选主推产品 + 2 个搭配产品
2. **生成文案**：填充小红书风格模板，生成标题、正文、标签、CTA
3. **生成海报**：自动拼装竖版海报（1024×1536），含标题、价格、品牌名
4. **AI 增强**（可选）：接入 OpenAI API 后，可用 AI 智能选品 + gpt-image-1 生成氛围图

## 怎么用你自己的产品数据

### 准备 Excel

参照 `BWS碎片化整理 - 适配AI模板.xlsx` 的格式，准备你的产品 Excel。需要这些 sheet：

| Sheet | 内容 |
|-------|------|
| 统一资源库 | 所有产品（酒店、一日游、包车等），每行一个 |
| 内容主题库 | 7 个轮播主题（如"海岛一日游"、"高端蜜月"） |
| 每日选题模板 | 每天发什么主题（排期表） |
| 图片Prompt模板 | AI 图片的提示词模板 |
| 小红书文案模板 | 文案各模块的模板 |

### 部署后端

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 本地测试
uvicorn api:app --reload --port 8080
# 打开 http://localhost:8080/docs 查看 API

# 3. 部署到 Fly.io
fly launch --name your-app-name --region sin
fly deploy

# 4. 配置 OpenAI（可选，用于 AI 选品和图片生成）
fly secrets set OPENAI_API_KEY=sk-xxx
```

### 部署前端

```bash
cd frontend
npm install
npm run build

# 部署到 Cloudflare Pages
wrangler pages project create your-project-name --production-branch main
wrangler pages deploy dist --project-name your-project-name
```

前端默认连接 `https://bws-social-content.fly.dev`。要改后端地址，构建时设置环境变量：

```bash
VITE_API_URL=https://your-backend.fly.dev npm run build
```

## 技术架构

```
Excel 产品表
  ↓  parsers/ (解析)
结构化数据
  ↓  content_pipeline/ (选品 + 文案 + 图片 + 海报)
  ↓  api.py (FastAPI)
HTTP API ←→ React 前端
```

- **后端**：Python 3.12 / FastAPI / Pillow / OpenAI API
- **前端**：React 18 / Vite / TypeScript / Tailwind CSS
- **部署**：后端 Fly.io / 前端 Cloudflare Pages

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/schedule` | 查看排期和生成状态 |
| GET | `/resources` | 浏览产品库 |
| GET | `/content/{date}` | 获取已生成的内容 |
| POST | `/generate` | 生成指定日期的内容 |
| POST | `/reload` | 重新加载 Excel 数据 |

## 设计文档

项目的产品设计和技术规划文档见仓库根目录：

1. [00-产品总览.md](00-产品总览.md) — 系统做什么、给谁用
2. [01-功能模块设计.md](01-功能模块设计.md) — 功能模块划分
3. [07-PRD产品需求说明书.md](07-PRD产品需求说明书.md) — 产品需求
4. [08-技术架构设计.md](08-技术架构设计.md) — 技术架构
5. [12-接口草案.md](12-接口草案.md) — API 接口设计

完整文档列表见 `00-*.md` 到 `20-*.md`。

## License

MIT
