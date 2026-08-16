<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <img v-if="brandLogo" :src="brandLogo" class="brand-icon" alt="" @error="brandLogo = null" />
        <span v-else class="brand-icon">🧪</span>
        <h2>QA通关</h2>
        <p>从零到测试专家的实战学习平台</p>
      </div>
      <form @submit.prevent="submit" class="login-form">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" placeholder="输入用户名" required autocomplete="username">
        </div>
        <div v-if="isRegister" class="field">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="you@example.com" required autocomplete="email">
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="输入密码" required :autocomplete="isRegister ? 'new-password' : 'current-password'">
        </div>
        <p v-if="error" class="err">{{ error }}</p>
        <button type="submit" class="btn-primary" style="width:100%;justify-content:center;padding:12px;" :disabled="submitting">
          {{ submitting ? '⏳ 处理中...' : (isRegister ? '创建账号' : '登录') }}
        </button>
      </form>
      <p class="switch">
        {{ isRegister ? '已有账号？' : '没有账号？' }}
        <a href="#" @click.prevent="isRegister=!isRegister;error=''">{{ isRegister ? '去登录' : '立即注册' }}</a>
      </p>
      <p v-if="!isRegister" class="switch" style="margin-top:8px;">
        <router-link to="/forgot-password">忘记密码？</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const isRegister = ref(false)
const brandLogo = ref('/QA_Test/favicon.svg')
const username = ref(''), email = ref(''), password = ref(''), error = ref('')
const submitting = ref(false)

async function submit() {
  error.value = ''
  submitting.value = true
  try {
    if (isRegister.value) await auth.register(username.value, email.value, password.value)
    else await auth.login(username.value, password.value)
    const redirect = route.query.redirect
    router.push(redirect || '/levels')
  } catch (e) { error.value = e.message }
  finally { submitting.value = false }
}
</script>

<style scoped>
.login-page {
  display: flex; justify-content: center; align-items: center;
  min-height: calc(100vh - 56px - 2 * var(--space-xl)); padding: var(--space-xl);
}
.login-card {
  width: 420px; max-width: 100%;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-xl); padding: 40px 36px;
  box-shadow: var(--shadow-lg);
}
.login-brand { text-align: center; margin-bottom: 32px; }
.brand-icon {
  display: inline-flex; width: 56px; height: 56px; border-radius: 14px;
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  align-items: center; justify-content: center; font-size: 1.5rem;
  margin-bottom: 12px; box-shadow: 0 4px 20px rgba(99,102,241,.25);
  object-fit: cover;
}
.login-brand h2 { font-size: 1.4rem; font-weight: 750; letter-spacing: -.5px; }
.login-brand p { color: var(--text-secondary); font-size: .84rem; margin-top: 4px; }
.login-form { display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: .78rem; font-weight: 600; color: var(--text-secondary); }
.field input {
  padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .88rem; font-family: var(--font-sans); outline: none;
  background: var(--bg); color: var(--text);
  transition: all var(--fast);
}
.field input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.err { color: var(--danger); font-size: .8rem; text-align: center; }
.switch { margin-top: 24px; text-align: center; font-size: .82rem; color: var(--text-secondary); }
.switch a { color: var(--primary); text-decoration: none; font-weight: 600; }
.switch a:hover { text-decoration: underline; }
</style>
