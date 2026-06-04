<template>
  <div>
    <div class="page-header">
      <h1>实操实验室</h1>
      <p>动手练习——把测试技能练成肌肉记忆</p>
    </div>
    <div class="lab-grid">
      <router-link to="/labs/sql" class="lab-card">
        <span class="lab-icon">🗄️</span>
        <h3>SQL 练习场</h3>
        <p>在安全沙箱中练习数据查询与验证</p>
        <span class="tag tag-primary">SELECT · JOIN · GROUP BY</span>
      </router-link>
      <router-link to="/labs/linux" class="lab-card">
        <span class="lab-icon">💻</span>
        <h3>Linux 日志分析</h3>
        <p>模拟真实服务器日志，用命令行排查问题</p>
        <span class="tag tag-primary">grep · tail · awk · sort</span>
      </router-link>
      <router-link to="/labs/api" class="lab-card">
        <span class="lab-icon">📮</span>
        <h3>API 请求练习</h3>
        <p>构造 HTTP 请求、查看响应、编写断言</p>
        <span class="tag tag-primary">GET · POST · Assert</span>
      </router-link>
      <router-link to="/labs/requirements" class="lab-card">
        <span class="lab-icon">📋</span>
        <h3>需求分析实验室</h3>
        <p>审查需求文档 · 发现歧义与矛盾 · 训练分析思维</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/network" class="lab-card">
        <span class="lab-icon">📶</span>
        <h3>网络协议</h3>
        <p>TCP 握手 · HTTP 演进 · TLS · DNS · WebSocket</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/xpath" class="lab-card">
        <span class="lab-icon">🎯</span>
        <h3>XPath / CSS 选择器</h3>
        <p>写选择器定位元素，实时高亮匹配结果</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/bugreport" class="lab-card">
        <span class="lab-icon">🐛</span>
        <h3>Bug 报告工坊</h3>
        <p>写 Bug 报告 — QA 最核心的职业输出技能</p>
        <span class="tag tag-primary">标题·步骤·严重度</span>
      </router-link>
      <router-link to="/labs/security" class="lab-card">
        <span class="lab-icon">🛡️</span>
        <h3>安全靶场</h3>
        <p>在漏洞环境中练习 XSS 注入 · SQL 注入</p>
        <span class="tag tag-danger">XSS · SQLi</span>
      </router-link>
      <router-link to="/labs/mobile" class="lab-card">
        <span class="lab-icon">📱</span>
        <h3>移动测试模拟器</h3>
        <p>ADB 命令实战 + 设备模拟器 + 崩溃分析</p>
        <span class="tag tag-primary">ADB · logcat · dumpsys</span>
      </router-link>
      <router-link to="/labs/ai" class="lab-card">
        <span class="lab-icon">🤖</span>
        <h3>AI 测试实验室</h3>
        <p>Prompt 工程 · AI 输出验证 · 测试 AI 系统</p>
        <span class="tag tag-warning">2026 趋势</span>
      </router-link>
      <router-link to="/labs/exploratory" class="lab-card">
        <span class="lab-icon">🗺️</span>
        <h3>探索式测试实验室</h3>
        <p>制定 Charter · 限时会话 · 记录发现</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/performance" class="lab-card">
        <span class="lab-icon">📈</span>
        <h3>性能测试实验室</h3>
        <p>编写 k6 脚本 · 模拟负载 · 分析延迟分位数</p>
        <span class="tag tag-danger">k6</span>
      </router-link>
      <router-link to="/labs/cicd" class="lab-card">
        <span class="lab-icon">🔄</span>
        <h3>CI/CD 管道实验室</h3>
        <p>构建管道 · 检测 Flaky 测试 · 故障根因分析</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/a11y" class="lab-card">
        <span class="lab-icon">♿</span>
        <h3>无障碍测试实验室</h3>
        <p>输入 HTML，自动检测 WCAG 违规项</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/visual" class="lab-card">
        <span class="lab-icon">🔍</span>
        <h3>视觉回归实验室</h3>
        <p>对比截图找差异——训练你的像素眼</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/automation" class="lab-card">
        <span class="lab-icon">🤖</span>
        <h3>测试自动化游乐场</h3>
        <p>编写 Playwright/Cypress/Selenium 脚本 · 逐步执行 · 即时验证</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/mock" class="lab-card">
        <span class="lab-icon">🎭</span>
        <h3>API Mock & 服务虚拟化</h3>
        <p>创建模拟端点 · 故障注入 · 依赖隔离测试</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/dbtest" class="lab-card">
        <span class="lab-icon">🗄️</span>
        <h3>数据库测试进阶</h3>
        <p>JOINs · 子查询 · 窗口函数 · 数据质量校验</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/datagen" class="lab-card">
        <span class="lab-icon">🎲</span>
        <h3>测试数据生成实验室</h3>
        <p>Faker · Pairwise · 数据脱敏 · 边界值 · SQL工厂</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/devtools" class="lab-card">
        <span class="lab-icon">🔧</span>
        <h3>浏览器DevTools实验室</h3>
        <p>Network/Performance/Console · 诊断真实性能问题</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
      <router-link to="/labs/mutation" class="lab-card">
        <span class="lab-icon">🧬</span>
        <h3>变异测试实验室</h3>
        <p>注入代码变异 · 评估测试质量 · 训练杀灭率思维</p>
        <span class="tag tag-warning">NEW</span>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.lab-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.lab-card {
  display: flex; flex-direction: column; gap: 10px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 28px 24px;
  text-decoration: none; color: var(--text);
  transition: all var(--fast); box-shadow: var(--shadow-xs);
}
.lab-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); border-color: var(--primary); }
.lab-icon { font-size: 2.2rem; }
.lab-card h3 { font-size: 1.05rem; font-weight: 650; }
.lab-card p { font-size: .82rem; color: var(--text-secondary); line-height: 1.55; flex: 1; }
</style>
