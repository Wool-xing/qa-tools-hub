# 贡献指南

## 技术栈

- 后端: Python 3.12+ / FastAPI / SQLAlchemy / SQLite
- 前端: Vue 3 / Vite / Pinia / CodeMirror 6
- 部署: Docker / Nginx / systemd

## 开发环境

```bash
cd v2-Pro版
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 编辑配置

cd frontend && npm ci
```

## 运行

```bash
# 后端
python -m uvicorn app.main:app --reload --port 8005

# 前端开发
cd frontend && npm run dev

# 测试
python -m pytest tests/ -v
cd frontend && npm test
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

- Python: ruff (line-length=100)
- 前端: 遵循现有 Vue 3 Composition API 风格
- 提交前: `python -m pytest tests/ && cd frontend && npm test && npm run build`
