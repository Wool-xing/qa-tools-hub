<template>
  <div class="welcome">
    <!-- Hero -->
    <section class="hero">
      <h1>QA通关</h1>
      <p class="hero-sub">测试工程师一站式学习与工具平台</p>
      <p class="hero-desc">102 个实战关卡 · 21 个交互实验室 · 22 个测试领域覆盖</p>
      <div class="hero-actions">
        <router-link to="/login" class="cta-btn">开始学习</router-link>
        <a href="#tools" class="cta-outline">浏览工具</a>
      </div>
    </section>

    <!-- Stats bar -->
    <section class="stats-bar">
      <div class="stat-item"><span class="stat-num">102</span><span class="stat-label">学习关卡</span></div>
      <div class="stat-item"><span class="stat-num">22</span><span class="stat-label">测试领域</span></div>
      <div class="stat-item"><span class="stat-num">21</span><span class="stat-label">交互实验室</span></div>
      <div class="stat-item"><span class="stat-num">8</span><span class="stat-label">成就徽章</span></div>
    </section>

    <!-- Tool Directory (runoob style) -->
    <section id="tools" class="tools-section">
      <h2>学习与工具目录</h2>

      <div v-for="cat in categories" :key="cat.key" class="tool-category">
        <h3 class="cat-title">
          <span class="cat-icon">{{ cat.icon }}</span>
          {{ cat.name }}
          <span class="cat-count">{{ cat.items.length }} 项</span>
        </h3>
        <div class="tool-grid">
          <router-link
            v-for="item in cat.items"
            :key="item.to"
            :to="auth.isLoggedIn ? item.to : '/login?redirect=' + encodeURIComponent(item.to)"
            class="tool-card"
          >
            <span v-if="item.icon" class="tool-icon">{{ item.icon }}</span>
            <div class="tool-info">
              <span class="tool-name">{{ item.name }}</span>
              <span class="tool-desc">{{ item.desc }}</span>
            </div>
            <span v-if="item.tag" :class="['tool-tag', 'tag-' + item.tagColor]">{{ item.tag }}</span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Bottom CTA -->
    <section class="bottom-cta">
      <div class="cta-card">
        <h2>准备好开始了吗？</h2>
        <p>从零到测试专家，只需每天 30 分钟</p>
        <router-link to="/login" class="cta-btn">免费开始学习</router-link>
      </div>
    </section>

    <!-- Footer -->
    <footer class="site-footer">
      <p>QA通关 © 2026 · 测试工程师学习平台 · 参照菜鸟教程风格</p>
    </footer>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()

const categories = [
  {
    key: 'learn',
    icon: '🎯',
    name: '学习关卡',
    items: [
      { name: '入门', desc: '测试理论 · 用例设计 · 缺陷管理', to: '/levels?stage=beginner', tag: '8关', tagColor: 'primary' },
      { name: '进阶', desc: '自动化 · 持续集成 · 测试架构', to: '/levels?stage=intermediate', tag: '3关', tagColor: 'primary' },
      { name: '专家', desc: '性能调优 · 安全渗透 · 测试策略', to: '/levels?stage=advanced', tag: '4关', tagColor: 'primary' },
      { name: 'Web 测试', desc: '浏览器工具 · 兼容性 · 自动化', to: '/levels?stage=web', tag: '4关', tagColor: 'primary' },
      { name: 'API 测试', desc: 'REST · GraphQL · 契约测试', to: '/levels?stage=api', tag: '3关', tagColor: 'primary' },
      { name: 'APP 测试', desc: '移动端 · 专项 · 兼容性', to: '/levels?stage=mobile', tag: '4关', tagColor: 'primary' },
      { name: '性能测试', desc: 'k6 · 基准 · 负载测试', to: '/levels?stage=performance', tag: '3关', tagColor: 'primary' },
      { name: '安全测试', desc: 'OWASP · 渗透 · 安全扫描', to: '/levels?stage=security', tag: '4关', tagColor: 'danger' },
      { name: '网络 & 抓包', desc: 'TCP/IP · HTTP · 代理工具', to: '/levels?stage=network', tag: '3关', tagColor: 'primary' },
      { name: 'CI/CD', desc: '流水线 · 自动化集成', to: '/levels?stage=cicd', tag: '2关', tagColor: 'primary' },
    ],
  },
  {
    key: 'labs',
    icon: '🧪',
    name: '实操实验室',
    items: [
      { icon: '🗄️', name: 'SQL 练习场', desc: '在线 SQL 查询练习，安全沙箱环境', to: '/labs/sql', tag: '热门', tagColor: 'warning' },
      { icon: '💻', name: 'Linux 日志分析', desc: 'grep · tail · awk 命令实战', to: '/labs/linux', tag: '热门', tagColor: 'warning' },
      { icon: '📮', name: 'API 请求练习', desc: '构造 HTTP 请求，编写响应断言', to: '/labs/api', tagColor: 'primary' },
      { icon: '📶', name: '网络协议实验室', desc: 'TCP 握手 · TLS 加密 · WebSocket', to: '/labs/network', tag: 'NEW', tagColor: 'warning' },
      { icon: '🎯', name: 'XPath/CSS 选择器', desc: '实时选择器解析与匹配高亮', to: '/labs/xpath', tag: 'NEW', tagColor: 'warning' },
      { icon: '🤖', name: 'AI 测试实验室', desc: 'Prompt 工程 · AI 输出验证', to: '/labs/ai', tag: '2026', tagColor: 'warning' },
      { icon: '🛡️', name: '安全靶场', desc: 'XSS · SQLi 漏洞环境练习', to: '/labs/security', tagColor: 'danger' },
      { icon: '📈', name: '性能测试实验室', desc: 'k6 脚本 · 负载模拟 · 延迟分析', to: '/labs/performance', tagColor: 'primary' },
      { icon: '🐛', name: 'Bug 报告工坊', desc: '编写高质量 Bug 报告', to: '/labs/bugreport', tagColor: 'primary' },
      { icon: '🤖', name: '自动化游乐场', desc: 'Playwright · Selenium 实战', to: '/labs/automation', tag: 'NEW', tagColor: 'warning' },
      { icon: '🎲', name: '测试数据生成', desc: 'Faker · Pairwise · 脱敏', to: '/labs/datagen', tag: 'NEW', tagColor: 'warning' },
      { icon: '🎭', name: 'API 虚拟化', desc: 'Mock 端点 · 故障注入', to: '/labs/mock', tag: 'NEW', tagColor: 'warning' },
    ],
  },
  {
    key: 'tools',
    icon: '🔧',
    name: '更多实验室',
    items: [
      { icon: '📱', name: '移动测试', desc: 'ADB 命令 · 崩溃日志分析', to: '/labs/mobile', tagColor: 'primary' },
      { icon: '🔄', name: 'CI/CD 管道', desc: '构建管道 · Flaky 检测', to: '/labs/cicd', tag: 'NEW', tagColor: 'warning' },
      { icon: '♿', name: '无障碍测试', desc: 'WCAG 违规自动检测', to: '/labs/a11y', tag: 'NEW', tagColor: 'warning' },
      { icon: '🔍', name: '视觉回归', desc: '截图对比 · 像素级差异', to: '/labs/visual', tag: 'NEW', tagColor: 'warning' },
      { icon: '🗺️', name: '探索式测试', desc: 'Charter · 限时会话', to: '/labs/exploratory', tag: 'NEW', tagColor: 'warning' },
      { icon: '📋', name: '需求分析', desc: '审查需求 · 发现歧义', to: '/labs/requirements', tag: 'NEW', tagColor: 'warning' },
      { icon: '🧬', name: '变异测试', desc: '代码变异 · 测试质量评估', to: '/labs/mutation', tag: 'NEW', tagColor: 'warning' },
      { icon: '🗄️', name: '数据库测试进阶', desc: 'JOIN · 窗口函数 · 数据质量', to: '/labs/dbtest', tag: 'NEW', tagColor: 'warning' },
      { icon: '🔧', name: 'DevTools', desc: '浏览器开发者工具实战', to: '/labs/devtools', tag: 'NEW', tagColor: 'warning' },
    ],
  },
]
</script>

<style scoped>
.welcome { max-width: 960px; margin: 0 auto; padding: 0 var(--space-lg); }

/* Hero */
.hero { text-align: center; padding: 64px 20px 40px; }
.hero h1 { font-size: 2.4rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 10px; background: linear-gradient(135deg, var(--primary), #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1.05rem; color: var(--text-secondary); margin-bottom: 6px; }
.hero-desc { font-size: .88rem; color: var(--text-muted); margin-bottom: 28px; }
.hero-actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.cta-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 14px 36px; border-radius: var(--radius); text-decoration: none;
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  color: #fff; font-weight: 700; font-size: .95rem;
  box-shadow: 0 4px 20px rgba(99,102,241,.35);
  transition: all var(--fast);
}
.cta-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 28px rgba(99,102,241,.45); }
.cta-outline {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 14px 36px; border-radius: var(--radius); text-decoration: none;
  border: 2px solid var(--border); color: var(--text-secondary);
  font-weight: 600; font-size: .95rem; transition: all var(--fast);
}
.cta-outline:hover { border-color: var(--primary); color: var(--primary); }

/* Stats bar */
.stats-bar {
  display: flex; justify-content: center; gap: 48px;
  padding: 28px 20px; margin-bottom: 48px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); box-shadow: var(--shadow-xs);
}
.stat-item { text-align: center; }
.stat-num { display: block; font-size: 1.6rem; font-weight: 800; color: var(--primary); line-height: 1.1; }
.stat-label { font-size: .78rem; color: var(--text-muted); font-weight: 500; }

/* Tool directory */
.tools-section { margin-bottom: 48px; }
.tools-section > h2 { font-size: 1.2rem; margin-bottom: 24px; text-align: center; }

.tool-category { margin-bottom: 32px; }
.cat-title {
  font-size: .95rem; font-weight: 650; margin-bottom: 12px;
  display: flex; align-items: center; gap: 8px;
  padding-bottom: 8px; border-bottom: 2px solid var(--primary-light);
}
.cat-icon { font-size: 1rem; }
.cat-count { font-size: .72rem; color: var(--text-muted); font-weight: 400; margin-left: auto; }

.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
}

.tool-card {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px; border-radius: var(--radius);
  border: 1px solid var(--border); background: var(--surface);
  text-decoration: none; color: var(--text);
  transition: all var(--fast); box-shadow: var(--shadow-xs);
}
.tool-card:hover {
  border-color: var(--primary); box-shadow: var(--shadow);
  transform: translateY(-1px);
}
.tool-icon { font-size: 1.4rem; flex-shrink: 0; width: 36px; text-align: center; }
.tool-info { flex: 1; min-width: 0; }
.tool-name { display: block; font-size: .85rem; font-weight: 600; line-height: 1.3; }
.tool-desc { display: block; font-size: .74rem; color: var(--text-muted); line-height: 1.4; margin-top: 2px; }
.tool-tag {
  font-size: .65rem; padding: 2px 8px; border-radius: var(--radius-full);
  font-weight: 600; flex-shrink: 0;
}
.tag-primary { background: var(--primary-light); color: var(--primary); }
.tag-warning { background: var(--warning-light); color: var(--warning); }
.tag-danger { background: var(--danger-light); color: var(--danger); }

/* Bottom CTA */
.bottom-cta { margin-bottom: 48px; }
.cta-card {
  text-align: center; padding: 48px 20px;
  background: linear-gradient(135deg, var(--primary-light), var(--primary-light));
  border-radius: var(--radius-xl); border: 1px solid var(--border);
}
.cta-card h2 { font-size: 1.3rem; margin-bottom: 8px; }
.cta-card p { font-size: .88rem; color: var(--text-secondary); margin-bottom: 20px; }

/* Footer */
.site-footer { text-align: center; padding: 24px 20px 40px; color: var(--text-muted); font-size: .78rem; border-top: 1px solid var(--border); }
</style>
