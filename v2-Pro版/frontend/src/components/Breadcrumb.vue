<template>
  <nav class="breadcrumb" aria-label="面包屑导航">
    <router-link to="/" class="crumb home">🏠 首页</router-link>
    <template v-for="item in items" :key="item.to || item.label">
      <span class="crumb-sep">/</span>
      <router-link v-if="item.to" :to="item.to" class="crumb">{{ item.label }}</router-link>
      <span v-else class="crumb current">{{ item.label }}</span>
    </template>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const routeLabels = {
  dashboard: '仪表板',
  levels: '闯关学习',
  labs: '实验室',
  teams: '团队协作',
  testcases: '用例库',
  profile: '个人中心',
  admin: '管理面板',
  login: '登录',
}

const labLabels = {
  'sql-lab': 'SQL 练习场',
  'cmd-lab': 'Linux 日志分析',
  'api-lab': 'API 请求练习',
  'network-lab': '网络协议',
  'xpath-lab': 'XPath/CSS 选择器',
  'bug-lab': 'Bug 报告工坊',
  'security-lab': '安全靶场',
  'mobile-lab': '移动测试',
  'ai-lab': 'AI 测试',
  'visual-lab': '视觉回归',
  'a11y-lab': '无障碍测试',
  'exploratory-lab': '探索式测试',
  'performance-lab': '性能测试',
  'cicd-lab': 'CI/CD管道',
  'automation-lab': '自动化测试',
  'requirements-lab': '需求分析',
  'mock-lab': 'API虚拟化',
  'dbtest-lab': '数据库测试',
  'devtools-lab': 'DevTools',
  'datagen-lab': '测试数据生成',
  'mutation-lab': '变异测试',
}

const items = computed(() => {
  const name = route.name
  const path = route.path
  const crumbs = []

  if (name === 'level') {
    crumbs.push({ to: '/levels', label: '闯关学习' })
    crumbs.push({ label: `关卡 #${route.params.id}` })
  } else if (path.startsWith('/labs/')) {
    crumbs.push({ to: '/labs', label: '实验室' })
    crumbs.push({ label: labLabels[name] || name })
  } else if (name && name !== 'home') {
    const label = routeLabels[name]
    if (label) crumbs.push({ label })
  }

  return crumbs
})
</script>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 0 16px;
  font-size: .82rem;
  flex-wrap: wrap;
}
.crumb {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--fast);
}
.crumb:hover { color: var(--primary); }
.crumb.home { color: var(--text-muted); }
.crumb.current { color: var(--text); font-weight: 600; }
.crumb-sep { color: var(--text-muted); font-size: .7rem; }
</style>
