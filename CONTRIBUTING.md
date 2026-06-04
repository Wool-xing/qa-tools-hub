# Contributing to QA通关

感谢你对 QA通关 的关注！欢迎贡献代码、报告 Bug、提出新功能建议。

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
5. 确保 `pytest tests/ -v` 和 `cd frontend && npm test` 通过
6. 提交 PR 到 `master` 分支

## 开发环境

```bash
# 后端
cd v2-Pro版
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8005

# 前端
cd v2-Pro版/frontend
npm install
npm run dev

# 测试
cd v2-Pro版
pytest tests/ -v           # 后端 146 tests
cd frontend && npm test    # 前端 19 tests
```

## 项目结构

```
├── v1-单文件版/        # Lite 版（单HTML）
├── v2-Pro版/           # Pro 版（FastAPI + Vue3）
│   ├── app/            # 后端 API
│   ├── frontend/       # Vue3 前端
│   ├── tests/          # 后端测试
│   └── migrations/     # Alembic 数据库迁移
```

## 代码风格

- **Python**: 遵循 PEP 8，Type Hints
- **Vue 3**: Composition API + `<script setup>` + Pinia
- **CSS**: 使用 CSS 自定义属性（`var(--primary)` 等）
- **命名**: camelCase（JS）, PascalCase（组件）, UPPER_SNAKE_CASE（常量）
