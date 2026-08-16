<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <img v-if="brandLogo" :src="brandLogo" class="brand-icon" alt="" @error="brandLogo = null" />
        <span v-else class="brand-icon">🔑</span>
        <h2>忘记密码</h2>
        <p>输入注册邮箱，我们将发送重置链接</p>
      </div>
      <form @submit.prevent="submit" class="login-form">
        <div class="field">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="you@example.com" required>
        </div>
        <p v-if="message" class="msg ok">{{ message }}</p>
        <p v-if="error" class="err">{{ error }}</p>
        <button type="submit" class="btn-primary" style="width:100%;justify-content:center;padding:12px;" :disabled="sent">
          {{ sent ? '已发送' : '发送重置链接' }}
        </button>
      </form>
      <p class="switch"><router-link to="/login">← 返回登录</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const email = ref(''), error = ref(''), message = ref(''), sent = ref(false)
const brandLogo = ref('/QA_Test/favicon.svg')

async function submit() {
  error.value = ''; message.value = ''
  try {
    const r = await fetch('/api/auth/forgot-password', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value })
    })
    const data = await r.json()
    if (r.ok) { message.value = data.message; sent.value = true }
    else error.value = data.detail || '发送失败'
  } catch (e) { error.value = '网络错误，请稍后重试' }
}
</script>

<style scoped>
.login-page { display: flex; justify-content: center; align-items: center; min-height: calc(100vh - 56px - 2*var(--space-xl)); padding: var(--space-xl); }
.login-card { width: 420px; max-width: 100%; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 40px 36px; box-shadow: var(--shadow-lg); }
.login-brand { text-align: center; margin-bottom: 32px; }
.brand-icon { display: inline-flex; width: 56px; height: 56px; border-radius: 14px; background: linear-gradient(135deg, var(--primary), #8b5cf6); align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 12px; object-fit: cover; }
.login-brand h2 { font-size: 1.4rem; font-weight: 750; }
.login-brand p { color: var(--text-secondary); font-size: .84rem; margin-top: 4px; }
.login-form { display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: .78rem; font-weight: 600; color: var(--text-secondary); }
.field input { padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: .88rem; font-family: var(--font-sans); outline: none; background: var(--bg); color: var(--text); }
.field input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.err { color: var(--danger); font-size: .8rem; text-align: center; }
.msg.ok { color: var(--success); font-size: .82rem; text-align: center; font-weight: 500; }
.switch { margin-top: 24px; text-align: center; font-size: .82rem; }
.switch a { color: var(--primary); text-decoration: none; font-weight: 600; }
</style>
