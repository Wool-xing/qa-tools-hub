import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import LevelsView from '../views/LevelsView.vue'
import LevelPlayView from '../views/LevelPlayView.vue'
import WelcomeView from '../views/WelcomeView.vue'
import { LS_TOKEN, LS_IS_ADMIN, LS_LAB_VISITS, LS_LAB_COUNT, APP_TITLE } from '../constants'

const routes = [
  { path: '/', name: 'home', component: WelcomeView, meta: { title: '首页' } },
  { path: '/login', name: 'login', component: LoginView, meta: { guest: true, title: '登录' } },
  { path: '/forgot-password', name: 'forgot', component: () => import('../views/ForgotPasswordView.vue'), meta: { guest: true, title: '忘记密码' } },
  { path: '/reset-password', name: 'reset', component: () => import('../views/ResetPasswordView.vue'), meta: { guest: true, title: '重置密码' } },
  { path: '/levels', name: 'levels', component: LevelsView, meta: { auth: true, title: '闯关 — 102关' } },
  { path: '/level/:id', name: 'level', component: LevelPlayView, meta: { auth: true, title: '关卡详情' } },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue'), meta: { auth: true, title: '仪表板' } },
  { path: '/profile', name: 'profile', component: () => import('../views/ProfileView.vue'), meta: { auth: true, title: '个人中心' } },
  { path: '/admin', name: 'admin', component: () => import('../views/AdminView.vue'), meta: { auth: true, admin: true, title: '管理面板' } },
  { path: '/labs', name: 'labs', component: () => import('../views/LabsView.vue'), meta: { auth: true, title: '实验室' } },
  { path: '/labs/sql', name: 'sql-lab', component: () => import('../views/SQLLabView.vue'), meta: { auth: true, title: 'SQL 练习场' } },
  { path: '/labs/linux', name: 'cmd-lab', component: () => import('../views/CmdLabView.vue'), meta: { auth: true, title: 'Linux 日志分析' } },
  { path: '/labs/api', name: 'api-lab', component: () => import('../views/APILabView.vue'), meta: { auth: true, title: 'API 请求练习' } },
  { path: '/labs/network', name: 'network-lab', component: () => import('../views/NetworkLabView.vue'), meta: { auth: true, title: '网络协议实验室' } },
  { path: '/labs/xpath', name: 'xpath-lab', component: () => import('../views/XPathLabView.vue'), meta: { auth: true, title: 'XPath/CSS 选择器' } },
  { path: '/labs/bugreport', name: 'bug-lab', component: () => import('../views/BugReportView.vue'), meta: { auth: true, title: 'Bug 报告工坊' } },
  { path: '/labs/security', name: 'security-lab', component: () => import('../views/SecurityLabView.vue'), meta: { auth: true, title: '安全靶场' } },
  { path: '/labs/mobile', name: 'mobile-lab', component: () => import('../views/MobileLabView.vue'), meta: { auth: true, title: '移动测试' } },
  { path: '/labs/ai', name: 'ai-lab', component: () => import('../views/AITestingView.vue'), meta: { auth: true, title: 'AI 测试' } },
  { path: '/labs/visual', name: 'visual-lab', component: () => import('../views/VisualLabView.vue'), meta: { auth: true, title: '视觉回归' } },
  { path: '/labs/a11y', name: 'a11y-lab', component: () => import('../views/A11yLabView.vue'), meta: { auth: true, title: '无障碍测试' } },
  { path: '/labs/exploratory', name: 'exploratory-lab', component: () => import('../views/ExploratoryLabView.vue'), meta: { auth: true, title: '探索式测试' } },
  { path: '/labs/performance', name: 'performance-lab', component: () => import('../views/PerformanceLabView.vue'), meta: { auth: true, title: '性能测试' } },
  { path: '/labs/cicd', name: 'cicd-lab', component: () => import('../views/CICDLabView.vue'), meta: { auth: true, title: 'CI/CD管道' } },
  { path: '/labs/automation', name: 'automation-lab', component: () => import('../views/AutomationPlaygroundView.vue'), meta: { auth: true, title: '自动化测试' } },
  { path: '/labs/requirements', name: 'requirements-lab', component: () => import('../views/RequirementLabView.vue'), meta: { auth: true, title: '需求分析' } },
  { path: '/labs/mock', name: 'mock-lab', component: () => import('../views/MockLabView.vue'), meta: { auth: true, title: 'API虚拟化' } },
  { path: '/labs/dbtest', name: 'dbtest-lab', component: () => import('../views/DBTestLabView.vue'), meta: { auth: true, title: '数据库测试' } },
  { path: '/labs/devtools', name: 'devtools-lab', component: () => import('../views/DevToolsLabView.vue'), meta: { auth: true, title: 'DevTools' } },
  { path: '/labs/datagen', name: 'datagen-lab', component: () => import('../views/DataGenLabView.vue'), meta: { auth: true, title: '测试数据生成' } },
  { path: '/labs/mutation', name: 'mutation-lab', component: () => import('../views/MutationLabView.vue'), meta: { auth: true, title: '变异测试' } },
  { path: '/teams', name: 'teams', component: () => import('../views/TeamView.vue'), meta: { auth: true, title: '团队协作' } },
  { path: '/testcases', name: 'testcases', component: () => import('../views/TestCaseView.vue'), meta: { auth: true, title: '测试用例管理' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from) {
    if (to.query.stage && to.path === from.path) return false  // same page, no scroll reset
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const token = localStorage.getItem(LS_TOKEN)
  if (to.name === 'home' && token) return '/levels'
  if (to.meta.auth && !token) return '/login'
  if (to.meta.guest && token) return '/levels'
  if (to.meta.admin && localStorage.getItem(LS_IS_ADMIN) !== '1') return '/levels'
  // Track lab visits for achievements
  if (to.path.startsWith('/labs/') && to.path !== '/labs') {
    try {
      const raw = localStorage.getItem(LS_LAB_VISITS) || '[]'
      const visits = new Set(JSON.parse(raw))
      visits.add(to.path)
      localStorage.setItem(LS_LAB_VISITS, JSON.stringify([...visits]))
      localStorage.setItem(LS_LAB_COUNT, String(visits.size))
    } catch { /* corrupted localStorage — reset */ }
  }
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} — QA通关` : APP_TITLE
})

export default router
