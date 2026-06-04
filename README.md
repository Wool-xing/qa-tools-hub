# QA工具导航 · QA通关

**测试工程师一站式学习与工具平台** — 102关学习 + 21个实验室 + 成就系统

[![GitHub](https://img.shields.io/badge/github-Wool--xing/qa--tools--hub-blue)](https://github.com/Wool-xing/qa-tools-hub)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 产品线

| 产品 | 路径 | 技术 | 启动 |
|------|------|------|------|
| **Lite** | `v1-单文件版/羊毛工具导航.html` | 单HTML (~3000行) | 双击打开 |
| **Pro API** | `v2-Pro版/app/` | FastAPI + SQLite + JWT | `python -m uvicorn app.main:app --port 8005` |
| **Pro 前端** | `v2-Pro版/frontend/` | Vue3 + Vite + Pinia | `npm run build` (已构建到 app/static/) |

## Pro 版功能

### 102关学习体系 (22个领域)
🌱 入门基础(8) · 🚀 进阶提升(3) · 🧠 专家进阶(4) · 🌐 Web测试(4) · 📡 API测试(3) · 📱 APP测试(4) · ⚡ 性能测试(3) · 🛡️ 安全测试(4) · 🚗 车载测试(2) · 📶 网络&抓包(3) · 🖥️ 运维&数据库(3) · 🔄 CI/CD(2)

### 21大实验室
1. **🗄️ SQL 练习场** — 3种数据库场景，SQLite安全沙箱（仅SELECT），表格展示结果
2. **💻 Linux 日志分析** — 模拟真实服务器，grep/tail/awk/sort/wc命令，VFS文件系统
3. **📮 API 请求练习** — 构造HTTP请求(GET/POST/PUT/DELETE)，Headers管理，响应断言
4. **📶 网络协议** — 7标签：TCP握手/HTTP演进/TLS加密/DNS解析/WebSocket/抓包分析/弱网测试
5. **🎯 XPath/CSS选择器** — 4个HTML场景，实时选择器解析，匹配高亮

### 成就系统
8个徽章：初出茅庐/小有所成/中流砥柱/半壁江山/入门毕业/Web专家/实验室新人/实验达人

### 代码沙箱安全
- AST验证：拦截 import/class/dunder/exec/eval/compile/__import__/open
- 子进程隔离 + 受限 builtins
- SQL注释绕过修复：先strip再检查

## API 端点
```
GET  /health                  — 健康检查
POST /api/auth/register       — 注册 (带验证)
POST /api/auth/login          — 登录 (JWT, 速率限制)
POST /api/auth/forgot-password — 忘记密码 (邮件重置)
POST /api/auth/reset-password  — 重置密码
GET  /api/auth/me             — 当前用户
GET  /api/levels              — 102关列表 + 进度
GET  /api/levels/{id}         — 关卡详情
POST /api/levels/submit       — 提交答案 (quiz/code/explore)
POST /api/levels/{id}/run     — 代码沙箱执行
POST /api/labs/sql/execute    — SQL安全沙箱
POST /api/labs/cmd/execute    — 命令行模拟器
```

## 生产特性
- **安全头**: X-Content-Type-Options, X-Frame-Options, CSP, HSTS, Referrer-Policy
- **速率限制**: 认证端点 5次/分钟/IP
- **请求追踪**: X-Request-Id 全链路追踪 + 响应时间
- **输入验证**: 用户名/邮箱/密码 Pydantic 校验 (8字符+字母+数字)
- **密码重置**: SMTP邮件重置流程 (可选启用)
- **Token管理**: JTI 黑名单 + 登出吊销
- **文件日志**: RotatingFileHandler 10MB×5, logs/app.log
- **Prometheus**: /metrics 端点 + 请求计数/延迟/并发
- **数据库迁移**: Alembic 自动迁移 (python -m alembic upgrade head)
- **Docker**: 多阶段构建 (Vue3 → Uvicorn, 8005端口, HEALTHCHECK)
- **备份**: `python scripts/backup.py backup|restore|list`
- **全局异常处理**: 不泄漏 traceback, 返回 request_id

## 测试账号

qatest / qa123456

## 技术指标

| 指标 | 值 |
|------|-----|
| 测试 | 140 passed |
| 覆盖率 | 95% |
| 前端构建 | ~300ms |

## 快速开始

```bash
cd v2-Pro版
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005
# 浏览器打开 http://localhost:8005
```
