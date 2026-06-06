<template>
  <aside class="sidebar" :class="{ collapsed: !open }">
    <div class="sidebar-inner">
      <!-- Search -->
      <div class="sidebar-search">
        <span class="search-icon">🔍</span>
        <input
          v-model="search"
          placeholder="搜索关卡、实验室..."
          class="search-input"
          @keydown.enter="doSearch"
        />
      </div>

      <!-- Nav sections -->
      <nav class="sidebar-nav">
        <div v-for="section in sections" :key="section.key" class="nav-section">
          <button
            class="nav-section-title"
            @click="toggleSection(section.key)"
            :class="{ open: openSections[section.key] }"
          >
            <span class="section-chevron">▸</span>
            <span>{{ section.label }}</span>
          </button>
          <div v-show="openSections[section.key]" class="nav-section-items">
            <a
              v-for="item in section.items"
              :key="item.to"
              :href="item.to"
              class="nav-section-item"
              :class="{ active: isActive(item.to, item.match) }"
              @click.prevent="navigateTo(item.to)"
            >
              <span v-if="item.icon" class="item-icon">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
              <span v-if="item.badge" class="item-badge">{{ item.badge }}</span>
            </a>
          </div>
        </div>
      </nav>
    </div>

    <!-- Mobile toggle -->
    <button class="sidebar-toggle" @click="open = !open" :title="open ? '收起侧栏' : '展开侧栏'">
      {{ open ? '◀' : '▶' }}
    </button>
  </aside>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const search = ref('')
const open = ref(window.innerWidth > 768)

function navigateTo(to) {
  if (to.includes('?stage=') && route.path === '/levels') {
    // Same page: replace query without re-render, just trigger watch
    const params = new URLSearchParams(to.split('?')[1])
    router.replace({ query: Object.fromEntries(params) })
  } else {
    router.push(to)
  }
}

const openSections = reactive({
  main: true,
  levels: true,
  domains: false,
  labs: false,
  practice: false,
})

const sections = [
  {
    key: 'main',
    label: '主导航',
    items: [
      { to: '/dashboard', label: '仪表板', match: 'dashboard' },
      { to: '/levels', label: '闯关学习', match: 'levels' },
      { to: '/labs', label: '实验室', match: 'labs' },
      { to: '/testcases', label: '用例库', match: 'testcases' },
      { to: '/teams', label: '团队协作', match: 'teams' },
    ],
  },
  {
    key: 'levels',
    label: '能力进阶',
    items: [
      { to: '/levels?stage=beginner', label: '入门', match: false },
      { to: '/levels?stage=intermediate', label: '进阶', match: false },
      { to: '/levels?stage=advanced', label: '专家', match: false },
    ],
  },
  {
    key: 'domains',
    label: '专项领域',
    items: [
      { to: '/levels?stage=web', label: 'Web测试', match: false },
      { to: '/levels?stage=api', label: 'API测试', match: false },
      { to: '/levels?stage=mobile', label: 'APP测试', match: false },
      { to: '/levels?stage=performance', label: '性能测试', match: false },
      { to: '/levels?stage=security', label: '安全测试', match: false },
      { to: '/levels?stage=network', label: '网络&抓包', match: false },
      { to: '/levels?stage=ops', label: '运维&数据库', match: false },
      { to: '/levels?stage=cicd', label: 'CI/CD', match: false },
      { to: '/levels?stage=automotive', label: '车载测试', match: false },
      { to: '/levels?stage=accessibility', label: '无障碍测试', match: false },
      { to: '/levels?stage=data', label: '数据测试', match: false },
      { to: '/levels?stage=chaos', label: '混沌工程', match: false },
      { to: '/levels?stage=visual', label: '视觉回归', match: false },
      { to: '/levels?stage=risk', label: '风险驱动', match: false },
      { to: '/levels?stage=metrics', label: '质量度量', match: false },
      { to: '/levels?stage=automation-arch', label: '自动化架构', match: false },
      { to: '/levels?stage=advanced-api', label: '现代API', match: false },
      { to: '/levels?stage=compliance', label: '合规测试', match: false },
      { to: '/levels?stage=fintech', label: '金融测试', match: false },
    ],
  },
  {
    key: 'labs',
    label: '实操实验室',
    items: [
      { to: '/labs/sql', label: 'SQL 练习场', match: 'sql-lab' },
      { to: '/labs/linux', label: 'Linux 日志分析', match: 'cmd-lab' },
      { to: '/labs/api', label: 'API 请求练习', match: 'api-lab' },
      { to: '/labs/network', label: '网络协议', match: 'network-lab' },
      { to: '/labs/xpath', label: 'XPath/CSS', match: 'xpath-lab' },
      { to: '/labs/security', label: '安全靶场', match: 'security-lab' },
      { to: '/labs/performance', label: '性能测试', match: 'performance-lab' },
      { to: '/labs/ai', label: 'AI 测试', match: 'ai-lab' },
      { to: '/labs/cicd', label: 'CI/CD管道', match: 'cicd-lab' },
      { to: '/labs/automation', label: '自动化测试', match: 'automation-lab' },
      { to: '/labs/mock', label: 'API虚拟化', match: 'mock-lab' },
      { to: '/labs/datagen', label: '数据生成', match: 'datagen-lab' },
    ],
  },
  {
    key: 'practice',
    label: '练习工具',
    items: [
      { to: '/labs/bugreport', label: 'Bug报告工坊', match: 'bug-lab' },
      { to: '/labs/a11y', label: '无障碍测试', match: 'a11y-lab' },
      { to: '/labs/exploratory', label: '探索式测试', match: 'exploratory-lab' },
      { to: '/labs/requirements', label: '需求分析', match: 'requirements-lab' },
      { to: '/labs/mutation', label: '变异测试', match: 'mutation-lab' },
      { to: '/labs/visual', label: '视觉回归', match: 'visual-lab' },
      { to: '/labs/dbtest', label: '数据库测试', match: 'dbtest-lab' },
      { to: '/labs/mobile', label: '移动测试', match: 'mobile-lab' },
      { to: '/labs/devtools', label: 'DevTools', match: 'devtools-lab' },
    ],
  },
]

function toggleSection(key) {
  openSections[key] = !openSections[key]
}

function isActive(to, matchName) {
  if (matchName === false) return false
  if (matchName) {
    if (route.name === matchName) return true
    if (matchName === 'levels' && (route.name === 'level' || route.path.startsWith('/level/'))) return true
    if (route.path === to) return true
    if (route.path.startsWith(to + '/') || route.path.startsWith(to + '?')) return true
  }
  return route.path === to
}

function doSearch() {
  const q = search.value.trim()
  if (!q) return
  router.push(`/levels?search=${encodeURIComponent(q)}`)
}
</script>

<style scoped>
.sidebar {
  width: 250px;
  min-width: 250px;
  height: calc(100vh - 52px);
  position: sticky;
  top: 52px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  overflow-x: hidden;
  transition: all .25s var(--ease);
  z-index: 50;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed {
  width: 0;
  min-width: 0;
  border-right: none;
  opacity: 0;
  pointer-events: none;
}

.sidebar-inner {
  padding: 12px 0 40px;
  flex: 1;
  overflow-y: auto;
}

/* Search */
.sidebar-search {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 12px 8px;
  padding: 0 10px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: border-color var(--fast);
}
.sidebar-search:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-light);
}
.search-icon { font-size: .8rem; flex-shrink: 0; }
.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px 0;
  font-size: .8rem;
  background: transparent;
  color: var(--text);
  font-family: var(--font-sans);
}

/* Nav sections */
.nav-section {
  border-bottom: 1px solid var(--border-light);
}
.nav-section-title {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: var(--text);
  font-size: .82rem;
  font-weight: 650;
  cursor: pointer;
  font-family: var(--font-sans);
  text-align: left;
  transition: all var(--fast);
}
.nav-section-title:hover { background: var(--surface-hover); color: var(--primary); }
.section-chevron {
  font-size: .65rem;
  transition: transform var(--fast);
  color: var(--text-muted);
  width: 12px;
  text-align: center;
}
.nav-section-title.open .section-chevron { transform: rotate(90deg); }

.nav-section-items {
  padding: 2px 0 8px;
  max-height: 360px;
  overflow-y: auto;
}

.nav-section-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 16px 7px 28px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: .8rem;
  transition: all var(--fast);
  border-left: 2px solid transparent;
}
.nav-section-item:hover {
  background: var(--surface-hover);
  color: var(--text);
}
.nav-section-item.active {
  color: var(--primary);
  background: var(--primary-light);
  border-left-color: var(--primary);
  font-weight: 600;
}
.item-icon { font-size: .85rem; flex-shrink: 0; width: 20px; text-align: center; }
.item-badge {
  margin-left: auto;
  font-size: .65rem;
  padding: 1px 6px;
  border-radius: var(--radius-full);
  background: var(--border-light);
  color: var(--text-muted);
  font-weight: 500;
}

/* Toggle button */
.sidebar-toggle {
  position: absolute;
  top: 8px;
  right: -28px;
  width: 22px;
  height: 44px;
  border: 1px solid var(--border);
  border-left: none;
  border-radius: 0 6px 6px 0;
  background: var(--surface);
  color: var(--text-muted);
  cursor: pointer;
  font-size: .6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--fast);
  z-index: 51;
  font-family: var(--font-sans);
  padding: 0;
}
.sidebar-toggle:hover { color: var(--primary); background: var(--surface-hover); }

.sidebar.collapsed .sidebar-toggle { right: -24px; }

/* Scrollbar */
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-track { background: transparent; }
.sidebar::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 52px;
    left: 0;
    z-index: 90;
    box-shadow: var(--shadow-lg);
  }
  .sidebar.collapsed {
    width: 0;
    min-width: 0;
  }
  .sidebar-toggle { right: -30px; }
}
</style>
