# QA通关 — 测试工程师学习平台

QA技能学习与通关平台，102关覆盖22个领域，从ISTQB基础到金融安全合规。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI (Python 3.12) + SQLAlchemy 2.0 + aiosqlite |
| 前端 | Vue 3 + Vite + Pinia + Vue Router |
| 部署 | Docker multi-stage + docker-compose |
| 监控 | Prometheus metrics + 旋转日志 |
| 测试 | pytest + httpx (146 tests) |

## 快速开始

### Docker (推荐)

```bash
docker compose up -d
```

访问 http://localhost:8005

### 本地开发

```bash
# 后端
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8005

# 前端 (另开终端)
cd frontend
npm install
npx vite --port 5173
```

访问 http://localhost:5173 (前端) 或 http://localhost:8005/docs (API文档)

### 测试账户

**管理员**: `qatest` / `qa123456`

注册新账户即可作为普通用户使用。

## 功能

- **102关卡 × 22领域** — ISTQB基础、API、Web、移动、性能、安全、车载、金融、合规...
- **6种任务类型** — quiz / code / debug / scenario / explore / analyze
- **22实验室** — SQL沙盒、Linux日志分析、安全靶场、性能k6、XPath/CSS、API虚拟化、视觉回归...
- **成就系统** — 自动检测+颁发，服务端持久化
- **团队协作** — 创建/加入团队、邀请码、团队仪表板
- **测试用例管理** — CRUD + xlsx导入导出 + 批量操作
- **学习分析** — 进度时间线、技能缺口识别、排行榜(周/月/总计)
- **暗黑模式** — OS偏好自动跟随
- **菜鸟教程式导航** — 左侧分类侧栏 + 面包屑 + 工具目录首页
- **Docker一键部署** — multi-stage构建，单容器运行

## API概览

| 前缀 | 端点 | 说明 |
|------|------|------|
| `/api/auth` | 8 | 注册/登录/登出/密码重置/个人信息 |
| `/api/levels` | 5 | 关卡列表/详情/提交/代码运行 |
| `/api/labs` | 12+ | SQL/命令/安全/性能/Mock |
| `/api/admin` | 7 | 统计/用户/关卡CRUD/排序 |
| `/api/testcases` | 8 | CRUD/批量/xlsx导入导出/测试运行 |
| `/api/analytics` | 4 | 进度时间线/技能缺口/成就/排行榜 |
| `/api/teams` | 5 | 创建/加入/列表/成员/仪表板 |
| `/health` | 1 | 健康检查(含DB探针) |
| `/metrics` | 1 | Prometheus指标 |

## 配置

环境变量 (Docker通过 `docker-compose.yml` 配置):

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./qa_tools.db` | 数据库连接 |
| `SECRET_KEY` | (dev默认) | **生产必改** |
| `CORS_ORIGINS` | `http://localhost:5173,...` | 允许的跨域来源 |
| `SMTP_HOST` | (空) | SMTP服务器 (密码重置邮件) |
| `HSTS_MAX_AGE` | `31536000` | HSTS有效期(秒) |

## 测试

```bash
pytest tests/ -v
```

## 项目结构

```
├── app/
│   ├── main.py          # FastAPI入口 + 中间件 + Prometheus
│   ├── config.py        # 环境变量 + 配置校验
│   ├── database.py      # SQLAlchemy引擎 + 会话
│   ├── seed.py          # 102关 + 8成就 + 8工具种子数据
│   ├── sandbox.py       # Python代码沙盒(AST校验+子进程隔离)
│   ├── lab_data.py      # SQL场景/VFS/命令模拟器/k6模拟
│   ├── mail.py          # SMTP邮件服务
│   ├── routers/         # API路由
│   │   ├── auth.py      # 认证(JWT+限流+黑名单)
│   │   ├── levels.py    # 关卡(提交+评分+成就)
│   │   ├── labs.py      # 实验室(SQL/命令/安全/性能/Mock)
│   │   ├── admin.py     # 管理(统计/用户/关卡管理)
│   │   ├── testcases.py # 测试用例(CRUD+xlsx+批量)
│   │   ├── analytics.py # 分析(进度/技能缺口/成就/排行)
│   │   └── teams.py     # 团队协作
│   └── models/          # SQLAlchemy模型
├── frontend/src/        # Vue3前端
│   ├── views/           # 30+页面组件
│   ├── components/      # 通用组件
│   │   ├── Sidebar.vue        # 菜鸟教程式左侧分类导航
│   │   ├── Breadcrumb.vue     # 自动路由感知面包屑
│   │   ├── BackToTop.vue      # 回到顶部浮动按钮
│   │   ├── ErrorBoundary.vue  # 错误边界
│   │   └── AchievementToast.vue # 成就弹窗
│   ├── stores/          # Pinia状态管理
│   ├── router/          # 40+路由
│   └── api.js           # API客户端
├── tests/               # pytest测试 (146)
├── Dockerfile           # Multi-stage构建
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

## 许可证

MIT
