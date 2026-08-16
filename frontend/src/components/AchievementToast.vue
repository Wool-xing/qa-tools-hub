<template>
  <Transition name="toast">
    <div v-if="visible" class="toast" role="status" aria-live="polite">
      <span class="toast-icon">🏆</span>
      <div class="toast-body">
        <strong>成就解锁！</strong>
        <span>{{ name }} — {{ desc }}</span>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({ name: String, desc: String })
const visible = ref(false)
let _timer = null

onMounted(() => {
  requestAnimationFrame(() => { visible.value = true })
  _timer = setTimeout(() => { visible.value = false }, 4000)
})

onBeforeUnmount(() => {
  if (_timer) clearTimeout(_timer)
})
</script>

<style scoped>
.toast {
  position: fixed; top: 72px; right: 20px; z-index: 999;
  display: flex; align-items: center; gap: 12px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #1a1a2e; padding: 14px 20px; border-radius: var(--radius-lg);
  box-shadow: 0 8px 28px rgba(245,158,11,.35);
  max-width: 320px; pointer-events: none;
}
.toast-icon { font-size: 1.6rem; flex-shrink: 0; }
.toast-body strong { display: block; font-size: .84rem; margin-bottom: 2px; }
.toast-body span { font-size: .74rem; opacity: .8; }
.toast-enter-active { transition: all .4s var(--ease); }
.toast-leave-active { transition: all .3s ease-in; }
.toast-enter-from { opacity: 0; transform: translateX(40px) scale(.9); }
.toast-leave-to { opacity: 0; transform: translateY(-20px); }
</style>
