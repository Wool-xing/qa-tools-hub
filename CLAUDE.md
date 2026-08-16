# QA工具导航

测试工具一站式导航平台。仓库根即项目根：后端在 `backend/`，前端在 `frontend/`。⚠ 注意：项目索引所称 v1 单文件 HTML 版在仓库中不存在（无实体），只开发 v2。

## 技术栈
- 后端：FastAPI + SQLAlchemy(async) + aiosqlite + JWT + Alembic + Prometheus，入口 `backend/app/main.py`
- 前端：Vue3 + Vite + Pinia + vue-router + vue-i18n + CodeMirror + axios（`frontend/`）
- 数据库：SQLite（`sqlite+aiosqlite:///./data/qa_tools.db`，`backend/app/config.py` 可被 DATABASE_URL 覆盖）
- CI：`.github/workflows/ci.yml`（Python 3.12 + Node 22）

## 运行
- 后端：`cd backend && python -m uvicorn app.main:app --port 8005`
- 前端 dev：`cd frontend && npm run dev`（5173）
- 部署：`docker compose up`（多阶段 Dockerfile，构建上下文为仓库根，端口 8005）；或 `cd frontend && npm run build`，产物输出到 `backend/app/static/`（已 gitignore）

## 测试
- 后端：`cd backend && python -m pytest tests/`（7 个测试文件）
- 前端：`cd frontend && npm test`（vitest）
- 基线：228 passed，覆盖率 81%

## 数据
- 初始数据由 `backend/app/seed.py`（148KB，关卡 + 工具 seed）写入
- `backend/app/lab_data.py` 内置实验室场景；无独立 JSON 数据文件
- 运行期数据（`backend/data/`、`backend/logs/`、`backend/backups/`）不入 git

## 参考
`README.md`、`CONTRIBUTING.md`、`backend/requirements.txt`、`backend/pyproject.toml`、`backend/.env.example`
