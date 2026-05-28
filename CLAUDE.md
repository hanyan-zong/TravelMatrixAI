# BWS 印尼旅游 · 小红书自动内容生成系统

## 项目目标

把 BWS 旅行社的产品资源（酒店、一日游、包车、疗愈等 153 条），自动拼装成每天一组小红书可直发的内容包：封面图 + 展开图 + 文案 + 标签。

## 架构

```
Excel 原始表 (9 sheet)
  ↓  parsers/*
data/*.json (153 条结构化资源)
  ↓
清洗版 Excel (辅助 sheet: 资源库/主题库/排期/模板)
  ↓  content_pipeline/
output/YYYY-MM-DD/ (content_data.json, post_text.txt, image_prompts.txt, preview.html, poster.jpg)
```

三条访问路径：
- `daily_post_generator.py` — 旧版 CLI，模板规则填充
- `generate_daily_content.py` — 新版 CLI，支持规则 / AI 策划 / AI 图片 / 海报
- `api.py` — FastAPI HTTP 接口，包装 content_pipeline，部署在 Fly.io

## 关键文件

| 文件 | 用途 |
|------|------|
| `models.py` | Pydantic v2 数据模型（8 种资源类型） |
| `parse_excel.py` | Excel → `data/*.json` |
| `parsers/` | 每个 sheet 的独立 parser，通过 `PARSERS` 字典注册 |
| `content_pipeline/` | 新管线：config / data_loader / selection / copywriter / prompt_builder / ai_planner / image_generator / poster / generator |
| `api.py` | FastAPI 接口层，包装 content_pipeline 为 HTTP API |
| `frontend/` | React + Vite + Tailwind 前端 SPA |
| `Dockerfile` | 后端容器化部署配置 |
| `fly.toml` | Fly.io 部署配置 |
| `data/all_resources.json` | 合并后 153 条资源 |
| `output/` | 每日生成结果 |

## 运行命令

```powershell
# 解析 Excel → JSON
python parse_excel.py

# 生成指定日期（规则模式 + 海报）
python generate_daily_content.py --date 2026-05-28 --poster

# AI 策划 + 图片 + 海报（需 OpenAI API）
python generate_daily_content.py --date 2026-05-28 --ai-plan --generate-images --poster

# 批量全部排期
python generate_daily_content.py --all --poster
```

## Excel 文件

| 文件 | 角色 |
|------|------|
| `BWS碎片化整理 - 适配AI模板.xlsx` | 原始产品数据，`parse_excel.py` 读取 |
| `BWS碎片化整理 - 2026年05月25日 chatGPT清洗过的.xlsx` | 含辅助 sheet（资源库/主题库/排期/模板），内容生成读取 |

## 技术栈

- 后端：Python 3.12 / FastAPI / Pydantic v2 / openpyxl / Pillow / OpenAI API（可选）
- 前端：React 18 / Vite 6 / TypeScript / Tailwind CSS 3
- 部署：后端 Fly.io（Docker） / 前端 Cloudflare Pages

## 部署

| 组件 | 地址 | 部署方式 |
|------|------|---------|
| 后端 API | https://bws-social-content.fly.dev | `fly deploy`（需 flyctl） |
| 前端 UI | https://bws-social-content.pages.dev | `wrangler pages deploy dist`（需 wrangler） |
| Swagger 文档 | https://bws-social-content.fly.dev/docs | 自动生成 |

OpenAI API Key 通过 `fly secrets set OPENAI_API_KEY=sk-xxx` 配置。

## API 端点

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/schedule` | 排期列表 + 主题 + 生成状态 |
| GET | `/resources?type=&area=&limit=&offset=` | 资源库查询 |
| GET | `/content/{date}` | 获取已生成内容（含 base64 图片） |
| POST | `/generate` | 生成指定日期内容 |
| POST | `/reload` | 重新加载 Excel 数据 |

## 当前状态

- 数据层：完成，153 条资源已解析
- 规则生成：完成，14 天排期可跑通
- API 层：完成，6 个端点已部署
- 前端：MVP 完成，排期查看 / 生成 / 预览 / 复制下载
- AI 策划 / 图片：代码就绪，需配置 OpenAI API Key
- 海报：Pillow fallback 可用，待视觉优化

## 设计约定

- 小红书竖版尺寸 1080×1440（海报目前用 1024×1536，待调整）
- 每天固定随机种子，保证同一天重复生成结果一致
- 主题 T001–T007 各对应不同资源类型和搭配规则
- 封面图 = 1.png 风格（AI 生成氛围图 + 文字叠加），展开图 = 2.png/3.png 风格（纯场景图）
