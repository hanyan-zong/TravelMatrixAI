# Infrastructure

本目录用于后续启动本地基础设施。

```powershell
cd C:\Users\001\Documents\Codex\TravelMatrixAI\mvp\infra
docker compose up -d
```

服务：

- PostgreSQL: `127.0.0.1:5432`
- Redis: `127.0.0.1:6379`
- MinIO API: `127.0.0.1:9000`
- MinIO Console: `127.0.0.1:9001`

当前 API 仍使用内存和 JSON 文件存储。接入数据库时，优先把 `15-数据库SQL草案.md` 的核心表迁移到正式 migration。
