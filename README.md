# QA工具导航 · QA通关

**测试工程师一站式学习与工具平台** — 102关学习 + 21个实验室 + 成就系统

[![GitHub](https://img.shields.io/badge/github-Wool--xing/qa--tools--hub-blue)](https://github.com/Wool-xing/qa-tools-hub)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 技术栈

| 层 | 路径 | 技术 |
|------|------|------|
| **后端** | `backend/app/` | FastAPI + SQLAlchemy 2.0 + aiosqlite + JWT + Alembic + Prometheus |
| **前端** | `frontend/` | Vue3 + Vite + Pinia + vue-router + vue-i18n + CodeMirror |
| **部署** | `deploy/` | Docker multi-stage + docker-compose + Nginx + systemd |
| **测试** | `backend/tests/` | pytest + httpx（228 passed，覆盖率 81%） |

## 功能

### 102关学习体系 (22个领域)
🌱 入门基础(8) · 🚀 进阶提升(3) · 🧠 专家进阶(4) · 🌐 Web测试(4) · 📡 API测试(3) · 📱 APP测试(4) · ⚡ 性能测试(3) · 🛡️ 安全测试(4) · 🚗 车载测试(2) · 📶 网络&抓包(3) · 🖥️ 运维&数据库(3) · 🔄 CI/CD(2)

- **6种任务类型** — quiz / code / debug / scenario / explore / analyze
- **成就系统** — 8个徽章，自动检测+颁发，服务端持久化
- **团队协作** — 创建/加入团队、邀请码、团队仪表板
- **测试用例管理** — CRUD + xlsx导入导出 + 批量操作
- **学习分析** — 进度时间线、技能缺口识别、排行榜(周/月/总计)
- **暗黑模式** — 跟随 OS 偏好
- **菜鸟教程式导航** — 左侧分类侧栏 + 面包屑 + 工具目录首页

### 21大实验室
1. **🗄️ SQL 练习场** — 3种数据库场景，SQLite安全沙箱（仅SELECT），表格展示结果
2. **💻 Linux 日志分析** — 模拟真实服务器，grep/tail/awk/sort/wc命令，VFS文件系统
3. **📮 API 请求练习** — 构造HTTP请求(GET/POST/PUT/DELETE)，Headers管理，响应断言
4. **📶 网络协议** — 7标签：TCP握手/HTTP演进/TLS加密/DNS解析/WebSocket/抓包分析/弱网测试
5. **🎯 XPath/CSS选择器** — 4个HTML场景，实时选择器解析，匹配高亮
+ 安全靶场、性能k6、API虚拟化、视觉回归等共21个

### 代码沙箱安全
- AST验证：拦截 import/class/dunder/exec/eval/compile/__import__/open
- 子进程隔离 + 受限 builtins
- SQL注释绕过修复：先strip再检查

## API 端点

```
GET  /health                    — 健康检查
POST /api/auth/register         — 注册 (带验证)
POST /api/auth/login            — 登录 (JWT, 速率限制)
POST /api/auth/forgot-password  — 忘记密码 (邮件重置)
POST /api/auth/reset-password   — 重置密码
GET  /api/auth/me               — 当前用户
GET  /api/levels                — 102关列表 + 进度
GET  /api/levels/{id}           — 关卡详情
POST /api/levels/submit         — 提交答案 (quiz/code/explore)
POST /api/levels/{id}/run       — 代码沙箱执行
POST /api/labs/sql/execute      — SQL安全沙箱
POST /api/labs/cmd/execute      — 命令行模拟器
```

| 前缀 | 端点数 | 说明 |
|------|--------|------|
| `/api/auth` | 8 | 注册/登录/登出/密码重置/个人信息 |
| `/api/levels` | 5 | 关卡列表/详情/提交/代码运行 |
| `/api/labs` | 12+ | SQL/命令/安全/性能/Mock |
| `/api/admin` | 7 | 统计/用户/关卡CRUD/排序 |
| `/api/testcases` | 8 | CRUD/批量/xlsx导入导出/测试运行 |
| `/api/analytics` | 4 | 进度时间线/技能缺口/成就/排行榜 |
| `/api/teams` | 5 | 创建/加入/列表/成员/仪表板 |
| `/health` | 1 | 健康检查(含DB探针) |
| `/metrics` | 1 | Prometheus指标 |

## 生产特性
- **安全头**: X-Content-Type-Options, X-Frame-Options, CSP, HSTS, Referrer-Policy
- **速率限制**: 认证端点 5次/分钟/IP
- **请求追踪**: X-Request-Id 全链路追踪 + 响应时间
- **输入验证**: 用户名/邮箱/密码 Pydantic 校验 (8字符+字母+数字)
- **密码重置**: SMTP邮件重置流程 (可选启用)
- **Token管理**: JTI 黑名单 + 登出吊销
- **文件日志**: RotatingFileHandler 10MB×5, `backend/logs/app.log`
- **Prometheus**: /metrics 端点 + 请求计数/延迟/并发
- **数据库迁移**: Alembic（`cd backend && python -m alembic upgrade head`）
- **Docker**: 多阶段构建 (Vue3 → Uvicorn, 8005端口, HEALTHCHECK)
- **备份**: `cd backend && python scripts/backup.py backup|restore|list`
- **全局异常处理**: 不泄漏 traceback, 返回 request_id

## 快速开始

### Docker (推荐)
```bash
docker compose up -d
```
访问 http://localhost:8005

### 本地开发
```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8005

# 前端 (另开终端)
cd frontend
npm install
npm run dev   # http://localhost:5173
```

## 测试

```bash
# 后端 (228 passed)
cd backend
python -m pytest tests/ -v

# 前端 (vitest)
cd frontend
npm test
```

## 项目结构

```
.
├── backend/                    # FastAPI 后端（工作目录）
│   ├── app/
│   │   ├── main.py             # FastAPI 入口 + 中间件 + Prometheus
│   │   ├── config.py           # 环境变量 + 配置校验
│   │   ├── database.py         # SQLAlchemy 引擎 + 会话
│   │   ├── seed.py             # 102关 + 成就 + 工具种子数据
│   │   ├── sandbox.py          # Python 代码沙盒（AST校验+子进程隔离）
│   │   ├── lab_data.py         # 实验室场景数据
│   │   ├── mail.py             # SMTP 邮件服务
│   │   ├── routers/            # API 路由 (auth/levels/labs/admin/testcases/analytics/teams)
│   │   ├── models/             # SQLAlchemy 模型
│   │   └── static/             # 前端构建产物（vite build 输出，gitignored）
│   ├── migrations/             # Alembic 迁移
│   ├── tests/                  # pytest 测试
│   ├── scripts/                # backup.py / e2e_verify.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                    # 本地配置（gitignored）
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── views/              # 30+ 页面组件
│   │   ├── components/         # 通用组件 + __tests__
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── router/             # 路由
│   │   ├── locales/            # i18n
│   │   ├── api.js              # API 客户端
│   │   └── main.js
│   ├── public/
│   ├── vite.config.js          # build 输出到 ../backend/app/static
│   └── package.json
├── deploy/                     # 生产部署（Nginx/systemd/setup.sh/CHECKLIST）
├── .github/workflows/          # CI（Python 3.12 + Node 22）
├── Dockerfile                  # 多阶段构建（构建上下文=仓库根）
├── docker-compose.yml
├── README.md · CONTRIBUTING.md · CHANGELOG.md · SECURITY.md · PRIVACY.md
├── LICENSE
└── .gitignore
```

## 测试账号

qatest / qa123456

## 技术指标

| 指标 | 值 |
|------|-----|
| 测试 | 228 passed (183后端 + 19前端 + 26 E2E) |
| 覆盖率 | 81% |
| CI | 全绿 |
| 前端构建 | ~500ms |

## 许可证

MIT
