# TravelMatrix AI MVP

这是 TravelMatrix AI 的第一版可运行工程骨架。

## 目录

- `web`：React + Vite 前端。
- `api`：FastAPI 后端。
- `packages/prompts`：后续放 AI 提示词模板。
- `packages/platform-adapters`：平台发布连接器接口和人工发布适配器。
- `infra`：PostgreSQL、Redis、MinIO 本地基础设施配置。

## 启动后端

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp\api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

或直接运行：

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp
.\start-api.ps1
```

## 启动前端

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp\web
npm.cmd install
npm.cmd run dev
```

当前 Windows 沙箱下，Vite dev 模式可能因为父目录权限扫描报错。稳定预览方式是：

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp
.\start-web-static.ps1
```

前端地址：

```text
http://127.0.0.1:4181
```

后端健康检查：

```text
http://127.0.0.1:8000/api/health
```

## 已实现的 MVP 接口

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/travel-products`
- `POST /api/ai/generate-posts`
- `GET /api/media-assets`
- `POST /api/media-assets`
- `POST /api/ai/compliance-check`
- `GET /api/publish-tasks/calendar`
- `POST /api/publish-tasks`
- `POST /api/publish-tasks/{task_id}/result`
- `POST /api/metrics`
- `GET /api/analytics/overview`

## 接口自检

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp\api
.\.venv\Scripts\python.exe check_api.py
```

## 当前数据存储

MVP 后端默认使用内存数据，并在新增素材、发布任务、数据指标时写入：

```text
api/data/state.json
```

该文件属于运行态数据，已加入 `.gitignore`。后续接 PostgreSQL 时，可以把这些模型迁移成数据库表。
