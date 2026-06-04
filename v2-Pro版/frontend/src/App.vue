<template>
  <div class="app">
    <nav class="topbar">
      <div class="topbar-inner">
        <router-link to="/" class="logo" v-if="!auth.isLoggedIn">
          <span class="logo-icon">🧪</span>
          <span class="logo-text">QA通关</span>
        </router-link>
        <router-link to="/dashboard" class="logo" v-else>
          <span class="logo-icon">🧪</span>
          <span class="logo-text">QA通关</span>
        </router-link>
        <template v-if="auth.isLoggedIn">
          <div class="nav-links">
            <router-link to="/levels" class="nav-item">🎯 闯关</router-link>
            <router-link to="/labs" class="nav-item">🧪 实验室</router-link>
          </div>
          <div class="nav-right">
            <button @click="toggleDark" class="btn-ghost" :title="isDark ? '浅色模式' : '深色模式'">{{ isDark ? '☀️' : '🌙' }}</button>
            <router-link to="/profile" class="nav-item" title="个人中心">
              <span class="user-avatar">{{ (auth.user?.username || 'U')[0].toUpperCase() }}</span>
              <span class="user-name">{{ auth.user?.username }}</span>
            </router-link>
            <router-link v-if="auth.user?.is_admin" to="/admin" class="nav-item">🛡️</router-link>
            <button @click="handleLogout" class="btn-ghost">退出</button>
          </div>
        </template>
        <template v-if="!auth.isLoggedIn && $route.name !== 'login' && $route.name !== 'forgot' && $route.name !== 'reset'">
          <div class="nav-right">
            <button @click="toggleDark" class="btn-ghost" :title="isDark ? '浅色模式' : '深色模式'">{{ isDark ? '☀️' : '🌙' }}</button>
            <router-link to="/login" class="btn-primary">登录</router-link>
          </div>
        </template>
        <template v-else-if="!auth.isLoggedIn">
          <div class="nav-right">
            <button @click="toggleDark" class="btn-ghost" :title="isDark ? '浅色模式' : '深色模式'">{{ isDark ? '☀️' : '🌙' }}</button>
          </div>
        </template>
      </div>
    </nav>
    <div class="app-body">
      <Sidebar v-if="showSidebar" />
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
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const guestRoutes = ['login', 'forgot', 'reset', 'home']
const showSidebar = computed(() => auth.isLoggedIn && !guestRoutes.includes(route.name))

const isDark = ref(false)

function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : '')
  localStorage.setItem('qa-dark-mode', isDark.value ? '1' : '0')
}

async function handleLogout() {
  try {
    await fetch('/api/auth/logout', {
      method: 'POST', headers: { 'Authorization': `Bearer ${auth.token}` }
    })
  } catch (e) { /* ignore */ }
  auth.logout()
  router.push('/login')
}

const _mq = window.matchMedia('(prefers-color-scheme: dark)')
const _mqHandler = (e) => {
  if (!localStorage.getItem('qa-dark-mode')) {
    isDark.value = e.matches
    document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : '')
  }
}

onMounted(() => {
  auth.restore()
  const saved = localStorage.getItem('qa-dark-mode')
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
  /* Colors */
  --bg: #f5f5f7;
  --bg-subtle: #fafafa;
  --surface: #ffffff;
  --surface-hover: #f8f9fb;
  --surface-raised: #ffffff;
  --text: #1a1a2e;
  --text-secondary: #5a5a7a;
  --text-muted: #9ca3af;
  --border: #e8e8ed;
  --border-light: #f0f0f5;
  --primary: #6366f1;
  --primary-hover: #5558e6;
  --primary-light: #eef2ff;
  --primary-bg: #f5f3ff;
  --success: #10b981;
  --success-light: #ecfdf5;
  --warning: #f59e0b;
  --warning-light: #fffbeb;
  --danger: #ef4444;
  --danger-light: #fef2f2;
  --info: #3b82f6;
  --info-light: #eff6ff;

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

  /* Radii */
  --radius-sm: 6px;
  --radius: 10px;
  --radius-lg: 14px;
  --radius-xl: 18px;
  --radius-full: 999px;

  /* Shadows */
  --shadow-xs: 0 1px 2px rgba(0,0,0,.04);
  --shadow-sm: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow: 0 4px 12px rgba(0,0,0,.06);
  --shadow-lg: 0 12px 32px rgba(0,0,0,.08);

  /* Transitions */
  --ease: cubic-bezier(.16,1,.3,1);
  --fast: .15s var(--ease);
  --normal: .25s var(--ease);
}

/* Reset */
*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

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
.topbar {
  position: sticky; top: 0; z-index: 100;
  background: rgba(255,255,255,.8);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--border);
  height: 56px;
}
.topbar-inner {
  max-width: 1100px; margin: 0 auto; padding: 0 var(--space-lg);
  height: 100%; display: flex; align-items: center; gap: var(--space-lg);
}
.logo {
  display: flex; align-items: center; gap: 8px;
  text-decoration: none; color: var(--text); font-weight: 700; font-size: 1.05rem;
  letter-spacing: -.3px; white-space: nowrap;
}
.logo-icon {
  width: 32px; height: 32px; border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--primary) 0%, #8b5cf6 100%);
  display: flex; align-items: center; justify-content: center; font-size: .9rem;
  box-shadow: 0 2px 8px rgba(99,102,241,.3);
}
.nav-links { display: flex; align-items: center; gap: 2px; flex: 1; }
.nav-item {
  padding: 6px 14px; border-radius: var(--radius-sm);
  text-decoration: none; color: var(--text-secondary); font-size: .84rem;
  font-weight: 500; transition: all var(--fast); white-space: nowrap;
}
.nav-item:hover { color: var(--text); background: var(--surface-hover); }
.nav-item.router-link-active { color: var(--primary); background: var(--primary-light); font-weight: 600; }
.nav-right { display: flex; align-items: center; gap: 10px; }
.user-avatar {
  width: 30px; height: 30px; border-radius: var(--radius-sm);
  background: var(--primary); color: #fff; display: flex; align-items: center;
  justify-content: center; font-size: .75rem; font-weight: 700; flex-shrink: 0;
}
.user-name { font-size: .82rem; color: var(--text); font-weight: 500; }

/* ==================== Buttons ==================== */
.btn-primary {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 20px; border-radius: var(--radius-sm); border: none;
  background: var(--primary); color: #fff; font-weight: 600;
  font-size: .84rem; cursor: pointer; text-decoration: none;
  transition: all var(--fast); font-family: var(--font-sans);
}
.btn-primary:hover { background: var(--primary-hover); box-shadow: 0 2px 12px rgba(99,102,241,.3); }
.btn-primary:disabled { opacity: .4; cursor: not-allowed; pointer-events: none; }

.btn-ghost {
  padding: 6px 14px; border-radius: var(--radius-sm); border: 1px solid transparent;
  background: transparent; color: var(--text-secondary); cursor: pointer;
  font-size: .82rem; font-family: var(--font-sans);
  transition: all var(--fast);
}
.btn-ghost:hover { background: var(--surface-hover); color: var(--text); }

.btn-outline {
  padding: 8px 20px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); color: var(--text-secondary); cursor: pointer;
  font-size: .84rem; font-weight: 500; font-family: var(--font-sans);
  transition: all var(--fast);
}
.btn-outline:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-light); }

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
  --bg: #0f1117; --bg-subtle: #161822; --surface: #1a1d2e; --surface-hover: #222640;
  --surface-raised: #222640; --text: #e5e7eb; --text-secondary: #a0a0b8;
  --text-muted: #6b7280; --border: #2d2d4a; --border-light: #252540;
  --primary: #818cf8; --primary-hover: #6366f1; --primary-light: #1e1b4b; --primary-bg: #1e1b4b;
  --success: #34d399; --success-light: #064e3b;
  --warning: #fbbf24; --warning-light: #451a03;
  --danger: #f87171; --danger-light: #450a0a;
  --info: #60a5fa; --info-light: #0c1a3e;
  --shadow-xs: 0 1px 2px rgba(0,0,0,.3); --shadow-sm: 0 1px 3px rgba(0,0,0,.4);
  --shadow: 0 4px 12px rgba(0,0,0,.4); --shadow-lg: 0 12px 32px rgba(0,0,0,.5);
}
[data-theme="dark"] .topbar { background: rgba(26,29,46,.85); }
[data-theme="dark"] body { background: var(--bg); }
</style>
