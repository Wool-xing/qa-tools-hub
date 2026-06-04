<template>
  <button v-show="visible" class="back-top" @click="scrollTop" aria-label="回到顶部" title="回到顶部">⬆</button>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const visible = ref(false)

function onScroll() {
  visible.value = window.scrollY > 400
}

function scrollTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.back-top {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 200;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-secondary);
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow);
  transition: all var(--fast);
  font-family: var(--font-sans);
  padding: 0;
}
.back-top:hover {
  color: var(--primary);
  border-color: var(--primary);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}
@media (max-width: 768px) {
  .back-top { bottom: 20px; right: 16px; width: 36px; height: 36px; font-size: .85rem; }
}
</style>
