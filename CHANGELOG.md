# Changelog

## v2.1.0 (2026-06-04) — 菜鸟教程风格重构

### UX 重构
- **左侧边栏导航** — runoob 风格可折叠分类菜单（主导航/学习领域/实操实验室/练习工具）
- **面包屑导航** — 自动路由感知面包屑，层级清晰
- **工具目录首页** — WelcomeView 重新设计为分类工具目录（学习关卡/实操实验室/更多实验室）
- **回到顶部按钮** — 滚动超过 400px 显示，平滑滚动
- **顶栏精简** — 登录后隐藏冗余导航链接，依赖侧栏导航
- **深色模式** — 未登录页面也可切换深色模式

### 技术改进
- Vite build 输出直接写入 `app/static/`
- 前端代理指向后端端口 8005
- 首页 Logo 根据登录状态跳转不同目标

### 新增组件
- `components/Sidebar.vue` — 250px 可折叠侧栏，移动端 fixed 定位
- `components/Breadcrumb.vue` — 自动路由感知的面包屑
- `components/BackToTop.vue` — 平滑滚动回到顶部
- 重构 `views/WelcomeView.vue` — 工具目录布局

## v2.0.0 (2026-05-19) — 生产就绪

### 优化 (Round 1)
- 删除死路由 `/metrics` 第一处理程序
- `import re` 从循环内提升至文件顶部 (levels.py)
- 排行榜实现 `period` 参数过滤 (weekly/monthly/alltime)
- 修复不一致的 `async_session` 直调 (analytics.py)
- 批量更新N+1消除 (testcases.py)
- 团队成员数N+1消除 (teams.py)
- 关卡排序N+1消除 (admin.py)

### 优化 (Round 2)
- 4处函数内import提升至文件顶部
- 成就检测逻辑抽取为 `_check_achievements` 辅助函数
- 前端leaderboard API补上period参数
- prometheus_client import提升至文件顶部
- achievement/team模型统一为 `Mapped[]` 风格
- 添加 `.gitignore` / `.dockerignore`
- 添加 `README.md` / `CHANGELOG.md`

### 落地验证
- Docker build ✓
- Frontend build ✓
- Backend startup ✓
- 146 tests ✓

## v1.0.0 (2026-05-18) — 初始发布

- 102关卡 × 22领域
- 6种任务类型
- 22实验室
- 40+ API端点
- JWT认证 + 速率限制
- Prometheus指标
- 成就系统
- 团队协作
- 测试用例CRUD + xlsx导入导出
- Docker部署
- 146 tests
