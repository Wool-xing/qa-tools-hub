<template>
  <div class="app">
    <nav class="topbar">
      <div class="topbar-inner">
        <!-- Mobile hamburger -->
        <button v-if="auth.isLoggedIn" class="hamburger" @click="sidebarOpen = !sidebarOpen" :aria-label="sidebarOpen ? '关闭菜单' : '打开菜单'">
          <span :class="{ open: sidebarOpen }"></span>
        </button>

        <!-- Logo left -->
        <router-link :to="auth.isLoggedIn ? '/dashboard' : '/'" class="logo">
          <img v-if="brandLogo" :src="brandLogo" class="logo-mark" alt="" @error="brandLogo = null" />
          <span v-else class="logo-mark">QA</span>
          <span class="logo-text">QA通关</span>
        </router-link>

        <!-- Right actions -->
        <div class="topbar-actions">
          <button @click="toggleDark" class="topbar-icon-btn" :title="isDark ? '浅色' : '深色'">
            {{ isDark ? '☀️' : '🌙' }}
          </button>
          <template v-if="auth.isLoggedIn">
            <router-link to="/profile" class="topbar-user">
              {{ auth.user?.username }}
            </router-link>
            <button @click="handleLogout" class="topbar-link logout-btn">退出</button>
          </template>
          <template v-else>
            <router-link to="/login" class="topbar-link">登录</router-link>
            <router-link v-if="$route.name !== 'login'" to="/login" class="topbar-cta">免费开始</router-link>
          </template>
        </div>
      </div>
    </nav>
    <div class="app-body">
      <Sidebar v-if="showSidebar" :open="sidebarOpen" @toggle="sidebarOpen = !sidebarOpen" />
      <main :class="{ 'has-sidebar': showSidebar }">
        <Breadcrumb v-if="showSidebar" />
        <ErrorBoundary>
          <router-view />
        </ErrorBoundary>
      </main>
    </div>
    <BackToTop />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ErrorBoundary from './components/ErrorBoundary.vue'
import Sidebar from './components/Sidebar.vue'
import Breadcrumb from './components/Breadcrumb.vue'
import BackToTop from './components/BackToTop.vue'
import { useAuthStore } from './stores/auth'
import { LS_DARK_MODE, LS_TOKEN } from './constants'
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const guestRoutes = ['login', 'forgot', 'reset', 'home']
const showSidebar = computed(() => auth.isLoggedIn && !guestRoutes.includes(route.name))
const sidebarOpen = ref(window.innerWidth > 768)

const isDark = ref(false)
const brandLogo = ref('/QA_Test/favicon.svg')

function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : '')
  localStorage.setItem(LS_DARK_MODE, isDark.value ? '1' : '0')
}

async function handleLogout() {
  try {
    await fetch('/api/auth/logout', {
      method: 'POST', headers: { 'Authorization': `Bearer ${localStorage.getItem(LS_TOKEN)}` }
    })
  } catch (e) { /* ignore */ }
  auth.logout()
  router.push('/login')
}

const _mq = window.matchMedia('(prefers-color-scheme: dark)')
const _mqHandler = (e) => {
  if (!localStorage.getItem(LS_DARK_MODE)) {
    isDark.value = e.matches
    document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : '')
  }
}

onMounted(() => {
  auth.restore()
  const saved = localStorage.getItem(LS_DARK_MODE)
  if (saved === '1' || (!saved && _mq.matches)) {
    isDark.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
  _mq.addEventListener('change', _mqHandler)
})

onBeforeUnmount(() => { _mq.removeEventListener('change', _mqHandler) })
</script>

<style>
/* ==================== Design System ==================== */
:root {
  /* Colors — Light */
  --bg: #f0f0f3;
  --surface: #ffffff;
  --surface-hover: #f5f5f8;
  --surface-raised: #ffffff;
  --text: #0f1115;
  --text-secondary: #5c5e6b;
  --text-muted: #8b8e99;
  --border: #e2e3e9;
  --border-light: #eeeef2;
  --primary: #5e6ad2;
  --primary-hover: #4f5ac0;
  --primary-light: #f0f1ff;
  --success: #10b981;
  --success-light: #ecfdf5;
  --warning: #f59e0b;
  --warning-light: #fffbeb;
  --danger: #ef4444;
  --danger-light: #fef2f2;

  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', 'Consolas', monospace;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;

  /* Radii — Linear scale */
  --radius-sm: 4px;
  --radius: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 999px;

  /* Shadows — minimal */
  --shadow-xs: 0 1px 2px rgba(0,0,0,.03);
  --shadow: 0 2px 8px rgba(0,0,0,.06);
  --shadow-lg: 0 8px 24px rgba(0,0,0,.10);

  /* Transitions */
  --ease: cubic-bezier(.16,1,.3,1);
  --fast: .15s var(--ease);
  --normal: .2s var(--ease);
}

/* Reset */
*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
button, input, select, textarea { color: inherit; font-family: inherit; }

html { scroll-behavior: smooth; }

body {
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}

.app { min-height: 100vh; display: flex; flex-direction: column; }

/* App body: sidebar + main */
.app-body { display: flex; flex: 1; }

main { flex: 1; min-width: 0; }

main.has-sidebar {
  padding: var(--space-lg) var(--space-xl);
  max-width: none;
}
/* ==================== Topbar — Stripe nav-bar style ==================== */
.topbar {
  position: sticky; top: 0; z-index: 100;
  background: var(--surface); border-bottom: 1px solid var(--border);
  height: 52px;
}
.topbar-inner {
  width: 100%; padding: 0 32px;
  height: 100%; display: flex; align-items: center; justify-content: space-between;
}
.logo {
  display: flex; align-items: center; gap: 8px; text-decoration: none;
  color: var(--text); font-weight: 600; font-size: .95rem;
  letter-spacing: -.3px; margin-right: 32px;
}
.logo-mark {
  width: 28px; height: 28px; border-radius: 6px;
  object-fit: cover;
  background: var(--primary); color: #fff; display: flex;
  align-items: center; justify-content: center; font-size: .65rem;
  font-weight: 700; letter-spacing: 0;
}
.topbar-link {
  padding: 6px 14px; border-radius: 6px; text-decoration: none;
  color: var(--text-secondary); font-size: .85rem; font-weight: 450;
  transition: all var(--fast);
}
.topbar-link:hover { color: var(--text); }
.topbar-link.router-link-active { color: var(--primary); }
.topbar-actions { display: flex; align-items: center; gap: 8px; }
.topbar-icon-btn {
  width: 32px; height: 32px; border-radius: 6px; border: none;
  background: transparent; cursor: pointer; font-size: .95rem;
  display: flex; align-items: center; justify-content: center;
  transition: background var(--fast);
}
.topbar-icon-btn:hover { background: var(--surface-hover); }
.topbar-cta {
  padding: 7px 18px; border-radius: var(--radius-full); text-decoration: none;
  background: var(--primary); color: #fff; font-size: .82rem; font-weight: 550;
  transition: filter var(--fast);
}
.topbar-cta:hover { filter: brightness(1.1); }
.topbar-user { text-decoration: none; color: var(--text); font-size: .85rem; font-weight: 500; }
.topbar-user:hover { color: var(--primary); }
.logout-btn { background: none; border: none; cursor: pointer; font-family: var(--font-sans); }

/* ==================== Buttons ==================== */
.btn-primary {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 8px 20px; border-radius: var(--radius-full); border: none;
  background: var(--primary); color: #fff; font-weight: 550;
  font-size: .84rem; cursor: pointer; text-decoration: none;
  transition: filter var(--fast); font-family: var(--font-sans);
}
.btn-primary:hover { filter: brightness(1.08); }
.btn-primary:disabled { opacity: .4; cursor: not-allowed; pointer-events: none; }

.btn-ghost {
  padding: 6px 14px; border-radius: 6px; border: none;
  background: transparent; color: var(--text-secondary); cursor: pointer;
  font-size: .82rem; font-family: var(--font-sans); transition: all var(--fast);
}
.btn-ghost:hover { background: var(--surface-hover); color: var(--text); }

.btn-outline {
  padding: 8px 20px; border-radius: var(--radius-full); border: 1px solid var(--border);
  background: var(--surface); color: var(--text); cursor: pointer;
  font-size: .84rem; font-weight: 500; font-family: var(--font-sans);
  transition: all var(--fast);
}
.btn-outline:hover { border-color: var(--primary); color: var(--primary); }

/* ==================== Shared Components ==================== */
.page-header {
  margin-bottom: var(--space-xl);
}
.page-header h1 {
  font-size: 1.6rem; font-weight: 750; letter-spacing: -.5px;
  margin-bottom: 6px;
}
.page-header p {
  color: var(--text-secondary); font-size: .9rem; line-height: 1.6;
}

.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: var(--space-lg);
  box-shadow: var(--shadow-xs); transition: all var(--fast);
}

.tag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px; border-radius: var(--radius-full);
  font-size: .7rem; font-weight: 600;
}
.tag-primary { background: var(--primary-light); color: var(--primary); }
.tag-success { background: var(--success-light); color: var(--success); }
.tag-warning { background: var(--warning-light); color: var(--warning); }
.tag-danger { background: var(--danger-light); color: var(--danger); }

main:not(.has-sidebar) { flex: 1; max-width: 1100px; width: 100%; margin: 0 auto; padding: var(--space-xl) var(--space-lg); }

/* Dark mode */
[data-theme="dark"] {
  --bg: #010102; --surface: #0f1011; --surface-hover: #141516;
  --surface-raised: #18191a; --text: #ffffff; --text-secondary: #a0a4b0;
  --text-muted: #6b6e7a; --border: #23252a; --border-light: #1c1d21;
  --primary: #5e6ad2; --primary-hover: #828fff; --primary-light: #1a1c2e;
  --success: #27a644; --success-light: #0d2e16;
  --warning: #f59e0b; --warning-light: #3d2c04;
  --danger: #ef4444; --danger-light: #3d0f0f;
  --shadow-xs: 0 1px 2px rgba(0,0,0,.5);
  --shadow: 0 2px 8px rgba(0,0,0,.6);
  --shadow-lg: 0 8px 24px rgba(0,0,0,.7);
}
[data-theme="dark"] .topbar { background: var(--surface); }
[data-theme="dark"] body { background: var(--bg); }

/* Skeleton loading animation */
@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .4; }
}
.skeleton {
  background: var(--border-light);
  border-radius: var(--radius);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
.skeleton-text { height: 14px; margin-bottom: 8px; }
.skeleton-title { height: 20px; width: 60%; margin-bottom: 12px; }
.skeleton-card { height: 120px; margin-bottom: var(--space-md); }

/* ==================== Mobile Responsive ==================== */
.hamburger {
  display: none; width: 32px; height: 32px; border: none;
  background: transparent; cursor: pointer; position: relative;
  padding: 6px 4px; margin-right: 8px;
}
.hamburger span, .hamburger span::before, .hamburger span::after {
  display: block; width: 100%; height: 2px; background: var(--text);
  border-radius: 2px; transition: all .2s ease; position: absolute;
}
.hamburger span { top: 50%; transform: translateY(-50%); }
.hamburger span::before { content: ''; top: -6px; }
.hamburger span::after { content: ''; top: 6px; }
.hamburger span.open { background: transparent; }
.hamburger span.open::before { top: 0; transform: rotate(45deg); }
.hamburger span.open::after { top: 0; transform: rotate(-45deg); }

@media (max-width: 768px) {
  .hamburger { display: flex; align-items: center; }
  .topbar-inner { padding: 0 12px; }
  .logo-text { display: none; }
  main.has-sidebar { padding: var(--space-md); }
  main:not(.has-sidebar) { padding: var(--space-md); max-width: 100%; }
  .page-header h1 { font-size: 1.3rem; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .btn-primary { font-size: .8rem; padding: 8px 16px; }
}
</style>
