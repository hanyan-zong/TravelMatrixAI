# MVP 工程交付说明

## 1. 工程位置

MVP 工程已创建在：

```text
C:\Users\001\Documents\Codex\TravelMatrixAI\mvp
```

## 2. 已完成内容

### 前端

位置：

```text
mvp\web
```

已实现：

- React + Vite + TypeScript
- 运营工作台
- 左侧模块导航
- 产品库视图
- 内容工厂视图
- 发布日历视图
- 数据看板视图
- API 连接状态显示
- 旅游产品选择
- 调用后端生成多平台内容
- 发布日历和数据看板读取 API
- 离线演示兜底

### 后端

位置：

```text
mvp\api
```

已实现：

- FastAPI
- 演示登录接口
- 当前用户接口
- 健康检查
- 旅游产品列表
- AI 多平台内容生成模拟接口
- 素材列表和新增
- 合规审核接口
- 发布日历接口
- 发布任务新增
- 发布结果记录
- 数据指标录入
- 数据看板接口
- 本地 JSON 运行态存储
- API 自检脚本

### 共享包

位置：

```text
mvp\packages
```

已实现：

- AI 提示词模板包
- 平台连接器类型定义
- 人工发布适配器

### 基础设施

位置：

```text
mvp\infra
```

已实现：

- PostgreSQL docker compose 配置
- Redis docker compose 配置
- MinIO docker compose 配置

## 3. 启动方式

启动 API：

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp
.\start-api.ps1
```

启动前端静态预览：

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp
.\start-web-static.ps1
```

访问：

```text
http://127.0.0.1:4181
```

API：

```text
http://127.0.0.1:8000/api/health
```

## 4. 验证命令

后端：

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp\api
.\.venv\Scripts\python.exe check_api.py
```

前端：

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp\web
npm.cmd run build
```

当前验证结果：

- API checks passed
- 前端 TypeScript 和 Vite build 通过

## 5. 下一步建议

建议下一轮优先做：

1. 接入真实数据库 PostgreSQL。
2. 把当前内存模型迁移到 ORM。
3. 增加登录和角色权限。
4. 增加真实素材上传。
5. 增加内容草稿编辑和保存。
6. 增加审核队列页面。
7. 增加发布包导出。
8. 接入真实 AI 模型。
