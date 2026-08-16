# Contributing to QA通关

感谢你对 QA通关 的关注！欢迎贡献代码、报告 Bug、提出新功能建议。

## 技术栈
- 后端: Python 3.12+ / FastAPI / SQLAlchemy / SQLite（`backend/`）
- 前端: Vue 3 / Vite / Pinia / CodeMirror 6（`frontend/`）
- 部署: Docker / Nginx / systemd（`deploy/`）

## 行为准则
- 保持尊重和专业
- 建设性反馈，不人身攻击
- 帮助新人融入社区

## 如何贡献

### 报告 Bug
1. 使用 [Bug Report](https://github.com/Wool-xing/qa-tools-hub/issues/new?template=bug_report.md) 模板
2. 描述复现步骤、预期行为、实际行为
3. 附上环境信息（OS、浏览器、Python 版本）

### 提交功能建议
1. 使用 [Feature Request](https://github.com/Wool-xing/qa-tools-hub/issues/new?template=feature_request.md) 模板
2. 描述使用场景和期望效果
3. 如有参考实现，附上链接

### 提交代码
1. Fork 仓库
2. 创建 feature 分支：`git checkout -b feat/your-feature`
3. 遵循 Conventional Commits：`feat:` / `fix:` / `docs:` / `test:` / `refactor:`
4. 写测试——新功能需要测试覆盖
5. 确保后端 pytest 与前端 vitest 全部通过
6. 提交 PR 到 `master` 分支

## 开发环境

```bash
# 后端
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # 编辑配置
python -m uvicorn app.main:app --reload --port 8005

# 前端
cd frontend
npm ci
npm run dev                      # http://localhost:5173

# 测试
cd backend && python -m pytest tests/ -v
cd frontend && npm test
```

## 项目结构

```
.
├── backend/            # FastAPI 后端（app/routers/models + migrations + tests + scripts）
├── frontend/           # Vue3 前端（src/views + components + stores + router）
├── deploy/             # 生产部署（Nginx / systemd / setup.sh）
├── .github/workflows/  # CI（后端 pytest + 前端 vitest）
├── Dockerfile          # 多阶段构建
└── docker-compose.yml
```

## 提交规范

```
feat: 新功能
fix: 修复
refactor: 重构
docs: 文档
test: 测试
chore: 构建/工具
```

## 分支策略
- `master` — 生产分支
- `feat/*` — 功能分支
- `fix/*` — 修复分支
- PR 合并需 CI 通过

## 代码风格
- **Python**: PEP 8 + Type Hints，ruff (line-length=100)
- **Vue 3**: Composition API + `<script setup>` + Pinia
- **CSS**: 使用 CSS 自定义属性（`var(--primary)` 等）
- **命名**: camelCase（JS）, PascalCase（组件）, UPPER_SNAKE_CASE（常量）
- 提交前: `cd backend && python -m pytest tests/ && cd ../frontend && npm test && npm run build`
