# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

QA Tools Hub — 单文件 HTML 测试工具导航站（`羊毛工具导航.html`）。覆盖 ISTQB 7 原则、测试金字塔、5 维度、7 流程、16 术语、60 工具。

## 技术栈

- 纯 HTML + CSS + JS（无框架，无构建工具）
- CSS 自定义属性（Design Tokens）：亮/暗双主题
- localStorage 持久化：收藏、笔记、已掌握、主题
- URL hash 同步（`#tools&cat=XXX&q=YYY`）
- Playwright E2E 测试

## 常用命令

```bash
# 运行 E2E 测试
cd "D:\项目文件\QA工具导航\v1-单文件版" && npx playwright test tests/qa-tools-hub.spec.ts

# 调试 E2E 测试（headed 模式）
npx playwright test --headed tests/qa-tools-hub.spec.ts

# 语法检查（括号平衡验证）
node -e "
const fs = require('fs');
const html = fs.readFileSync('羊毛工具导航.html', 'utf8');
const js = html.match(/<script>([\\s\\S]*?)<\\/script>/)[1];
const o = (js.match(/\\{/g)||[]).length;
const c = (js.match(/\\}/g)||[]).length;
console.log('Braces balanced:', o === c, '(open=' + o + ' close=' + c + ')');
"
```

## 文件结构

```
v1-单文件版\
├── 羊毛工具导航.html        # 主文件（~2000行，内嵌CSS+JS）
├── package.json              # npm 配置（仅用于 Playwright 测试）
├── package-lock.json
├── node_modules/
├── manifest.json             # PWA manifest
├── sw.js                     # Service Worker
├── tests/
│   └── qa-tools-hub.spec.ts  # 26 个 E2E 测试用例
├── test-results/             # Playwright 测试结果
└── CLAUDE.md                 # 本文件
```

## 代码架构

HTML 内部分为三个区域：
1. **`<style>`** — CSS Design Tokens (`:root` / `body.dark`) + 组件样式（导航、Hero、轮播、金字塔、时间轴、工具卡片、抽屉、对比栏）
2. **`<body>`** — 静态 HTML 骨架（导航栏、Hero、各 Section 容器）
3. **`<script>`** — IIFE 包裹的 JS，核心模块：
   - 数据层：`toolsData[]`（60工具）、`theoryPrinciples[]`、`dimensionBlocks[]`、`processSteps[]`
   - 渲染层：`renderTools()`、`renderTheory()`、`renderRoadmap()`、`renderDimensions()`、`renderProcess()`、`renderGlossary()`、`renderFilterButtons()`
   - 筛选层：`filterAndRenderTools()` — 搜索 + 分类 + 难度 + 收藏 + 排序
   - 持久化：`localStorage` 键 `qa-tools-fav`、`qa-tools-tried`、`qa-tools-notes`、`qa-tools-theme`
   - 交互：抽屉 `openDrawer()`/`closeDrawer()`、轮播、主题切换、键盘快捷键、URL hash 同步
   - 新增：导出/导入 `exportBtn`/`importBtn`、工具对比 `compareSet`/`showCompare()`

## 修改注意事项

1. **`renderFilterButtons()` 选择器** — 只移除 `[data-category]` 或 `[data-level]` 的 filter-btn，勿影响 `#sortSelect`、`#exportBtn`、`#importBtn`
2. **重复数据已修复** — LoadRunner (id:18) 和 SoapUI (id:23) 曾重复，当前 60 唯一工具
3. **搜索防抖 200ms** — `searchInput` 使用 `debounce(fn, 200)`
4. **测试** — 修改后运行 `npx playwright test` 确认无回归（当前 26 tests, all passing）
5. **`file://` 协议限制** — E2E 测试使用 `file://` URL，部分 Web API 行为可能不同（如 download event、sticky 定位）
6. **工具对比状态** — `compareSet` 是 `Set<number>`，最多 3 个，修改时同步更新 `updateCompareBar()` + `filterAndRenderTools()`
