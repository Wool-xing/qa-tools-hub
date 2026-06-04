<template>
  <div class="profile-page">
    <div class="page-header"><h1>👤 个人中心</h1><p>管理你的账户信息</p></div>

    <div class="profile-grid">
      <!-- Profile Card -->
      <div class="card">
        <h3>基本信息</h3>
        <div class="info-rows">
          <div class="info-row"><span class="info-label">用户名</span><span class="info-val">{{ auth.user?.username }}</span></div>
          <div class="info-row"><span class="info-label">邮箱</span><span class="info-val">{{ auth.user?.email }}</span></div>
          <div class="info-row"><span class="info-label">角色</span><span class="info-val">{{ auth.user?.is_admin ? '管理员' : '普通用户' }}</span></div>
        </div>
      </div>

      <!-- Stats Card -->
      <div class="card">
        <h3>学习统计</h3>
        <div class="stats-mini">
          <div class="stat-item"><span class="stat-num">{{ store.progress.completed || 0 }}</span><span class="stat-label">已完成</span></div>
          <div class="stat-item"><span class="stat-num">{{ store.progress.points || 0 }}</span><span class="stat-label">积分</span></div>
          <div class="stat-item"><span class="stat-num">{{ store.progress.total || 0 }}</span><span class="stat-label">总关卡</span></div>
        </div>
      </div>

      <!-- Change Password -->
      <div class="card">
        <h3>🔒 修改密码</h3>
        <form @submit.prevent="changePassword" class="pw-form">
          <div class="field">
            <label>当前密码</label>
            <input v-model="currentPw" type="password" required autocomplete="current-password">
          </div>
          <div class="field">
            <label>新密码 (8字符以上, 含字母+数字)</label>
            <input v-model="newPw" type="password" required autocomplete="new-password" @input="checkStrength">
            <div class="pw-meter"><div class="pw-fill" :class="strengthClass" :style="{width: strengthPct+'%'}"></div></div>
            <span class="pw-hint">{{ strengthHint }}</span>
          </div>
          <p v-if="pwError" class="err">{{ pwError }}</p>
          <p v-if="pwSuccess" class="success">{{ pwSuccess }}</p>
          <button type="submit" class="btn-primary" :disabled="loading || strengthPct < 50">
            {{ loading ? '修改中...' : '更新密码' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useLevelsStore } from '../stores/levels'

const auth = useAuthStore()
const store = useLevelsStore()

const currentPw = ref(''), newPw = ref('')
const loading = ref(false), pwError = ref(''), pwSuccess = ref('')

const strengthPct = ref(0)
const strengthClass = ref('')
const strengthHint = ref('')

function checkStrength() {
  const v = newPw.value
  let score = 0
  if (v.length >= 8) score += 25
  if (v.length >= 12) score += 15
  if (/[a-zA-Z]/.test(v) && /\d/.test(v)) score += 30
  if (/[^a-zA-Z0-9]/.test(v)) score += 20
  if (/[A-Z]/.test(v) && /[a-z]/.test(v)) score += 10
  strengthPct.value = Math.min(score, 100)
  if (score < 40) { strengthClass.value = 'weak'; strengthHint.value = '弱' }
  else if (score < 65) { strengthClass.value = 'fair'; strengthHint.value = '一般' }
  else if (score < 85) { strengthClass.value = 'good'; strengthHint.value = '强' }
  else { strengthClass.value = 'strong'; strengthHint.value = '很强' }
}

async function changePassword() {
  pwError.value = ''; pwSuccess.value = ''
  if (newPw.value.length < 8) { pwError.value = '新密码至少8个字符'; return }
  loading.value = true
  try {
    const r = await fetch('/api/auth/me', {
      method: 'PATCH', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${auth.token}` },
      body: JSON.stringify({ current_password: currentPw.value, new_password: newPw.value })
    })
    const data = await r.json()
    if (!r.ok) { pwError.value = data.detail || '修改失败'; return }
    pwSuccess.value = '密码已更新'
    currentPw.value = ''; newPw.value = ''; strengthPct.value = 0
  } catch (e) { pwError.value = '网络错误' }
  finally { loading.value = false }
}

onMounted(() => store.fetchList())
</script>

<style scoped>
.profile-page { max-width: 700px; }
.profile-grid { display: flex; flex-direction: column; gap: var(--space-lg); }

.info-rows { display: flex; flex-direction: column; gap: 12px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border-light); }
.info-label { font-size: .82rem; color: var(--text-secondary); font-weight: 500; }
.info-val { font-size: .88rem; font-weight: 600; }

.stats-mini { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.stat-item { text-align: center; padding: 12px; background: var(--bg); border-radius: var(--radius); }
.stat-num { display: block; font-size: 1.4rem; font-weight: 800; color: var(--primary); }
.stat-label { font-size: .72rem; color: var(--text-muted); }

.pw-form { display: flex; flex-direction: column; gap: 12px; }
.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: .78rem; font-weight: 600; color: var(--text-secondary); }
.field input {
  padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .88rem; font-family: var(--font-sans); outline: none; background: var(--surface);
  transition: border-color var(--fast);
}
.field input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.pw-meter { height: 4px; background: var(--border-light); border-radius: 2px; margin-top: 2px; overflow: hidden; }
.pw-fill { height: 100%; border-radius: 2px; transition: width .3s var(--ease); }
.pw-fill.weak { background: var(--danger); }
.pw-fill.fair { background: var(--warning); }
.pw-fill.good { background: var(--primary); }
.pw-fill.strong { background: var(--success); }
.pw-hint { font-size: .7rem; color: var(--text-muted); }

.err { color: var(--danger); font-size: .8rem; }
.success { color: var(--success); font-size: .8rem; font-weight: 600; }
</style>
