<template>
  <div v-if="error" class="err-boundary">
    <div class="err-card">
      <span class="err-icon">⚠️</span>
      <h2>页面出错</h2>
      <p class="err-msg">{{ error.message || '未知错误' }}</p>
      <button class="btn-primary" @click="reset">重试</button>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'

const error = ref(null)

onErrorCaptured((err) => {
  error.value = err
  return false  // prevent propagation
})

function reset() {
  error.value = null
}
</script>

<style scoped>
.err-boundary {
  display: flex; align-items: center; justify-content: center;
  min-height: 60vh; padding: var(--space-xl);
}
.err-card {
  text-align: center; background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: var(--space-2xl); max-width: 420px;
  box-shadow: var(--shadow);
}
.err-icon { font-size: 2.5rem; display: block; margin-bottom: var(--space-md); }
.err-card h2 { font-size: 1.15rem; margin-bottom: var(--space-sm); }
.err-msg { font-size: .84rem; color: var(--text-secondary); margin-bottom: var(--space-lg); line-height: 1.6; word-break: break-all; }
</style>
