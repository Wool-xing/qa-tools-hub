<template>
  <div class="lab-page">
    <div class="scenario-bar">
      <button v-for="s in scenarios" :key="s.id" class="scenario-btn" :class="{ active: activeScenario === s.id }" @click="selectScenario(s.id)">{{ s.label }}</button>
    </div>

    <div v-if="currentScenario" class="card" style="margin-bottom:var(--space-md);">
      <p class="scenario-desc">{{ currentScenario.desc }}</p>

      <div class="diff-panels">
        <div class="diff-panel baseline-panel">
          <div class="diff-label">📸 基线截图 (Baseline)</div>
          <div class="diff-canvas" ref="baselineRef" @click="(e) => handleClick(e, 'baseline')">
            <component :is="renderScenario('baseline')" />
            <div v-for="(r, i) in currentScenario.regions" :key="'bl-'+i"
              class="diff-hitbox" :class="{ found: foundRegions.has(i) }"
              :style="hitboxStyle(r, 'baseline')"
              @click.stop="findRegion(i)" />
          </div>
        </div>
        <div class="diff-panel current-panel">
          <div class="diff-label">🔬 当前截图 (Current)</div>
          <div class="diff-canvas" ref="currentRef" @click="(e) => handleClick(e, 'current')">
            <component :is="renderScenario('current')" />
            <div v-for="(r, i) in currentScenario.regions" :key="'cr-'+i"
              class="diff-hitbox" :class="{ found: foundRegions.has(i) }"
              :style="hitboxStyle(r, 'current')"
              @click.stop="findRegion(i)" />
          </div>
        </div>
      </div>

      <div class="diff-status">
        <div class="score-display">
          <span class="score-label">已找到</span>
          <span class="score-num">{{ foundRegions.size }}</span>
          <span class="score-sep">/</span>
          <span class="score-total">{{ currentScenario.regions.length }}</span>
          <span class="score-label">个差异</span>
          <span v-if="foundRegions.size === currentScenario.regions.length" class="all-found">🎉 全部找到！</span>
        </div>
        <button class="btn-outline" @click="resetScenario">🔄 重新开始</button>
      </div>

      <div v-if="foundRegions.size === currentScenario.regions.length" class="quiz-section">
        <p class="quiz-q">这是哪种视觉回归类型？</p>
        <button v-for="(o, i) in quizOptions" :key="i" class="quiz-opt" :class="{
          selected: quizChosen === i,
          correct: quizSubmitted && i === currentScenario.quizAnswer,
          wrong: quizSubmitted && quizChosen === i && i !== currentScenario.quizAnswer
        }" :disabled="quizSubmitted" @click="quizChosen = i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span><span>{{ o }}</span>
        </button>
        <button v-if="!quizSubmitted" class="btn-primary" style="margin-top:10px;" :disabled="quizChosen === -1" @click="quizSubmitted = true">✅ 提交</button>
        <div v-if="quizSubmitted" class="explain" :class="quizChosen === currentScenario.quizAnswer ? 'correct' : 'wrong'">
          {{ quizChosen === currentScenario.quizAnswer ? '✅ 正确！' : '❌ 错误。' }} {{ currentScenario.quizExplain }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, h, reactive } from 'vue'

const activeScenario = ref('layout-shift')
const foundRegions = ref(new Set())
const quizChosen = ref(-1)
const quizSubmitted = ref(false)

const scenarios = [
  {
    id: 'layout-shift', label: '📐 布局偏移', quizAnswer: 0,
    quizExplain: '布局偏移（Layout Shift）指元素位置发生变化——此例中"提交"按钮向右下偏移了20px，可能由CSS加载延迟或动态插入内容引起。',
    desc: '某表单页面部署后，"提交"按钮位置与设计稿不一致。对比两图找出差异区域。',
    regions: [{ x: 190, y: 228, w: 72, h: 34, diff: '按钮向右偏移20px，向下偏移8px' }],
    renderBaseline: () => h('div', { class: 'mock-page' }, [
      h('div', { class: 'mock-header' }, [h('span', { class: 'mock-logo' }, 'MyApp')]),
      h('div', { class: 'mock-form' }, [
        h('label', { class: 'mock-label' }, '用户名'),
        h('div', { class: 'mock-input' }, 'admin@example.com'),
        h('label', { class: 'mock-label', style: { marginTop: '12px' } }, '密码'),
        h('div', { class: 'mock-input' }, '••••••••'),
        h('div', { class: 'mock-btn', style: { marginTop: '14px' } }, '提交'),
      ]),
    ]),
    renderCurrent: () => h('div', { class: 'mock-page' }, [
      h('div', { class: 'mock-header' }, [h('span', { class: 'mock-logo' }, 'MyApp')]),
      h('div', { class: 'mock-form' }, [
        h('label', { class: 'mock-label' }, '用户名'),
        h('div', { class: 'mock-input' }, 'admin@example.com'),
        h('label', { class: 'mock-label', style: { marginTop: '12px' } }, '密码'),
        h('div', { class: 'mock-input' }, '••••••••'),
        h('div', { class: 'mock-btn', style: { marginTop: '22px', marginLeft: '20px' } }, '提交'),
      ]),
    ]),
  },
  {
    id: 'missing-element', label: '🔮 元素缺失', quizAnswer: 2,
    quizExplain: '元素缺失（Missing Element）指页面中某个元素完全没有渲染。此例中搜索图标消失，可能是图标字体加载失败或组件条件渲染逻辑变更。',
    desc: '导航栏更新后，测试发现某个图标不见了。找出缺失的元素。',
    regions: [{ x: 328, y: 12, w: 24, h: 24, diff: '搜索图标缺失' }],
    renderBaseline: () => h('div', { class: 'mock-page' }, [
      h('div', { class: 'mock-nav' }, [
        h('span', { class: 'mock-nav-item' }, '首页'),
        h('span', { class: 'mock-nav-item' }, '产品'),
        h('span', { class: 'mock-nav-item' }, '关于'),
        h('span', { class: 'mock-nav-spacer' }),
        h('span', { class: 'mock-icon-btn' }, '🔍'),
        h('span', { class: 'mock-icon-btn' }, '👤'),
      ]),
      h('div', { class: 'mock-content' }, [
        h('h3', { class: 'mock-title' }, '欢迎回来'),
        h('p', { class: 'mock-text' }, '这里是仪表板内容区域。'),
      ]),
    ]),
    renderCurrent: () => h('div', { class: 'mock-page' }, [
      h('div', { class: 'mock-nav' }, [
        h('span', { class: 'mock-nav-item' }, '首页'),
        h('span', { class: 'mock-nav-item' }, '产品'),
        h('span', { class: 'mock-nav-item' }, '关于'),
        h('span', { class: 'mock-nav-spacer' }),
        h('span', { class: 'mock-icon-btn mock-missing' }),
        h('span', { class: 'mock-icon-btn' }, '👤'),
      ]),
      h('div', { class: 'mock-content' }, [
        h('h3', { class: 'mock-title' }, '欢迎回来'),
        h('p', { class: 'mock-text' }, '这里是仪表板内容区域。'),
      ]),
    ]),
  },
  {
    id: 'color-change', label: '🎨 颜色变化', quizAnswer: 1,
    quizExplain: '颜色变化（Color Shift）指颜色值细微变化。此例中背景从 #eef2ff（浅紫）变为 #f0fdf4（浅绿），差值仅几个色调，肉眼需仔细对比才能发现。',
    desc: '设计系统升级后，部分组件背景色出现轻微偏差。找出颜色变化区域。',
    regions: [{ x: 88, y: 96, w: 224, h: 66, diff: '卡片背景色从浅紫变为浅绿' }],
    renderBaseline: () => h('div', { class: 'mock-page' }, [
      h('div', { class: 'mock-section-title' }, '通知面板'),
      h('div', { class: 'mock-card-list' }, [
        h('div', { class: 'mock-notify-card', style: { background: '#eef2ff' } }, [
          h('span', { class: 'mock-notify-icon' }, '📬'),
          h('div', {}, [h('strong', {}, '新消息'), h('span', { class: 'mock-notify-desc' }, '你有3条未读消息')]),
        ]),
        h('div', { class: 'mock-notify-card', style: { background: '#f9fafb' } }, [
          h('span', { class: 'mock-notify-icon' }, '📅'),
          h('div', {}, [h('strong', {}, '日程提醒'), h('span', { class: 'mock-notify-desc' }, '明天下午3点会议')]),
        ]),
        h('div', { class: 'mock-notify-card', style: { background: '#f9fafb' } }, [
          h('span', { class: 'mock-notify-icon' }, '✅'),
          h('div', {}, [h('strong', {}, '任务完成'), h('span', { class: 'mock-notify-desc' }, 'PR #128 已合并')]),
        ]),
      ]),
    ]),
    renderCurrent: () => h('div', { class: 'mock-page' }, [
      h('div', { class: 'mock-section-title' }, '通知面板'),
      h('div', { class: 'mock-card-list' }, [
        h('div', { class: 'mock-notify-card', style: { background: '#f0fdf4' } }, [
          h('span', { class: 'mock-notify-icon' }, '📬'),
          h('div', {}, [h('strong', {}, '新消息'), h('span', { class: 'mock-notify-desc' }, '你有3条未读消息')]),
        ]),
        h('div', { class: 'mock-notify-card', style: { background: '#f9fafb' } }, [
          h('span', { class: 'mock-notify-icon' }, '📅'),
          h('div', {}, [h('strong', {}, '日程提醒'), h('span', { class: 'mock-notify-desc' }, '明天下午3点会议')]),
        ]),
        h('div', { class: 'mock-notify-card', style: { background: '#f9fafb' } }, [
          h('span', { class: 'mock-notify-icon' }, '✅'),
          h('div', {}, [h('strong', {}, '任务完成'), h('span', { class: 'mock-notify-desc' }, 'PR #128 已合并')]),
        ]),
      ]),
    ]),
  },
  {
    id: 'text-overflow', label: '📝 文本溢出', quizAnswer: 3,
    quizExplain: '文本溢出（Text Overflow）指长文本超出容器边界或被截断。此例中右侧面板的用户名过长被截断为省略号。常见于多语言（如德语单词较长）或动态数据场景。',
    desc: '国际化后，部分面板中的长文本显示异常。找出文本被截断的位置。',
    regions: [{ x: 236, y: 84, w: 140, h: 28, diff: '用户名文本被截断，显示省略号' }],
    renderBaseline: () => h('div', { class: 'mock-page' }, [
      h('div', { class: 'mock-section-title' }, '团队成员'),
      h('div', { class: 'mock-member-grid' }, [
        h('div', { class: 'mock-member' }, [h('span', { class: 'mock-avatar' }, 'Z'), h('span', {}, '张三')]),
        h('div', { class: 'mock-member' }, [h('span', { class: 'mock-avatar' }, 'L'), h('span', {}, '李四')]),
        h('div', { class: 'mock-member' }, [h('span', { class: 'mock-avatar' }, 'W'), h('span', {}, '王小明')]),
        h('div', { class: 'mock-member' }, [h('span', { class: 'mock-avatar' }, 'C'), h('span', {}, 'Christopher Johnson')]),
      ]),
    ]),
    renderCurrent: () => h('div', { class: 'mock-page' }, [
      h('div', { class: 'mock-section-title' }, '团队成员'),
      h('div', { class: 'mock-member-grid' }, [
        h('div', { class: 'mock-member' }, [h('span', { class: 'mock-avatar' }, 'Z'), h('span', {}, '张三')]),
        h('div', { class: 'mock-member' }, [h('span', { class: 'mock-avatar' }, 'L'), h('span', {}, '李四')]),
        h('div', { class: 'mock-member' }, [h('span', { class: 'mock-avatar' }, 'W'), h('span', {}, '王小明')]),
        h('div', { class: 'mock-member' }, [h('span', { class: 'mock-avatar' }, 'C'), h('span', { style: 'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:88px;display:inline-block;' }, 'Christopher Johnson')]),
      ]),
    ]),
  },
]

const quizOptions = ['布局偏移 (Layout Shift)', '颜色变化 (Color Shift)', '元素缺失 (Missing Element)', '文本溢出 (Text Overflow)']

const currentScenario = computed(() => scenarios.find(s => s.id === activeScenario.value))

function selectScenario(id) {
  activeScenario.value = id
  foundRegions.value = new Set()
  quizChosen.value = -1
  quizSubmitted.value = false
}

function findRegion(i) {
  const next = new Set(foundRegions.value)
  next.add(i)
  foundRegions.value = next
}

function handleClick(e, side) {
  // Clicked on canvas but not on hitbox — visual feedback only
}

function hitboxStyle(region, side) {
  return {
    left: region.x + 'px',
    top: region.y + 'px',
    width: region.w + 'px',
    height: region.h + 'px',
  }
}

function resetScenario() {
  foundRegions.value = new Set()
  quizChosen.value = -1
  quizSubmitted.value = false
}

function renderScenario(side) {
  const s = currentScenario.value
  if (!s) return () => null
  return side === 'baseline' ? s.renderBaseline : s.renderCurrent
}
</script>

<style scoped>
.lab-page { max-width: 900px; margin: 0 auto; }
.scenario-bar { display: flex; gap: 8px; margin-bottom: var(--space-md); flex-wrap: wrap; }
.scenario-btn {
  padding: 8px 16px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .8rem; font-weight: 500;
  transition: all var(--fast); font-family: var(--font-sans);
}
.scenario-btn:hover { border-color: var(--primary); }
.scenario-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }

.scenario-desc { font-size: .84rem; color: var(--text-secondary); margin-bottom: 16px; line-height: 1.6; }

.diff-panels { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
@media (max-width: 720px) { .diff-panels { grid-template-columns: 1fr; } }

.diff-panel { border: 2px solid var(--border); border-radius: var(--radius); overflow: hidden; }
.diff-panel.baseline-panel { border-color: var(--primary); }
.diff-panel.current-panel { border-color: var(--warning); }
.diff-label {
  padding: 8px 14px; font-size: .74rem; font-weight: 600;
  font-family: var(--font-mono); text-align: center;
}
.baseline-panel .diff-label { background: var(--primary-light); color: var(--primary); }
.current-panel .diff-label { background: var(--warning-light); color: var(--warning); }

.diff-canvas { position: relative; min-height: 260px; background: #fff; padding: 16px 20px; }
[data-theme="dark"] .diff-canvas { background: #1e1e2e; }

.diff-hitbox {
  position: absolute; border: 2px dashed var(--danger); border-radius: 4px;
  cursor: pointer; transition: all var(--fast); background: rgba(239,68,68,.08);
  z-index: 10;
}
.diff-hitbox:hover { background: rgba(239,68,68,.2); border-style: solid; transform: scale(1.02); }
.diff-hitbox.found {
  border-color: var(--success); border-style: solid;
  background: rgba(16,185,129,.15); animation: pulse-found .6s ease;
}
@keyframes pulse-found { 0% { transform: scale(1); } 50% { transform: scale(1.08); } 100% { transform: scale(1); } }

.diff-status { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-top: 1px solid var(--border-light); }
.score-display { display: flex; align-items: baseline; gap: 6px; font-family: var(--font-mono); }
.score-label { font-size: .8rem; color: var(--text-secondary); }
.score-num { font-size: 1.4rem; font-weight: 700; color: var(--primary); }
.score-sep { font-size: 1rem; color: var(--text-muted); }
.score-total { font-size: 1rem; font-weight: 600; color: var(--text-secondary); }
.all-found { margin-left: 10px; font-size: .82rem; color: var(--success); font-weight: 600; }

.quiz-section { margin-top: var(--space-md); padding-top: var(--space-md); border-top: 1px solid var(--border-light); }
.quiz-q { font-size: .92rem; font-weight: 600; margin-bottom: 12px; line-height: 1.5; }
.quiz-opt { display: flex; align-items: center; gap: 12px; width: 100%; padding: 12px 16px; margin-bottom: 6px; border: 2px solid var(--border); border-radius: var(--radius); background: var(--surface); cursor: pointer; font-size: .86rem; text-align: left; transition: all var(--fast); font-family: var(--font-sans); }
.quiz-opt:hover:not(:disabled) { border-color: var(--primary); background: var(--primary-light); }
.quiz-opt.selected { border-color: var(--primary); background: var(--primary-light); font-weight: 600; }
.quiz-opt.correct { border-color: var(--success); background: var(--success-light); }
.quiz-opt.wrong { border-color: var(--danger); background: var(--danger-light); }
.quiz-opt:disabled { cursor: default; }
.opt-letter { width: 26px; height: 26px; border-radius: 6px; background: var(--border-light); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .76rem; flex-shrink: 0; }
.quiz-opt.selected .opt-letter { background: var(--primary); color: #fff; }
.quiz-opt.correct .opt-letter { background: var(--success); color: #fff; }
.quiz-opt.wrong .opt-letter { background: var(--danger); color: #fff; }
.explain { margin-top: 12px; padding: 14px; border-radius: var(--radius); font-size: .84rem; line-height: 1.6; }
.explain.correct { background: var(--success-light); color: #065f46; }
.explain.wrong { background: var(--danger-light); color: var(--danger); }

/* Mock UI styles */
.mock-page :deep(.mock-header) { display: flex; align-items: center; padding-bottom: 12px; border-bottom: 1px solid #e5e7eb; margin-bottom: 16px; }
.mock-page :deep(.mock-logo) { font-weight: 700; font-size: .95rem; color: #4f46e5; }
.mock-page :deep(.mock-form) { max-width: 260px; }
.mock-page :deep(.mock-label) { font-size: .76rem; font-weight: 600; color: #374151; display: block; margin-bottom: 4px; }
.mock-page :deep(.mock-input) { width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: .8rem; background: #f9fafb; color: #374151; }
.mock-page :deep(.mock-btn) { display: inline-block; padding: 8px 22px; background: #4f46e5; color: #fff; border-radius: 6px; font-size: .82rem; font-weight: 600; }
.mock-page :deep(.mock-nav) { display: flex; align-items: center; gap: 18px; padding: 8px 0; border-bottom: 1px solid #e5e7eb; margin-bottom: 16px; }
.mock-page :deep(.mock-nav-item) { font-size: .82rem; color: #4b5563; font-weight: 500; }
.mock-page :deep(.mock-nav-spacer) { flex: 1; }
.mock-page :deep(.mock-icon-btn) { font-size: .9rem; cursor: pointer; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; }
.mock-page :deep(.mock-missing) { background: #fee2e2; border-radius: 4px; border: 1px dashed #ef4444; }
.mock-page :deep(.mock-content) { padding: 8px 0; }
.mock-page :deep(.mock-title) { font-size: .92rem; font-weight: 700; color: #111827; margin-bottom: 6px; }
.mock-page :deep(.mock-text) { font-size: .8rem; color: #6b7280; }
.mock-page :deep(.mock-section-title) { font-size: .84rem; font-weight: 700; color: #374151; margin-bottom: 10px; }
.mock-page :deep(.mock-card-list) { display: flex; flex-direction: column; gap: 8px; }
.mock-page :deep(.mock-notify-card) { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 8px; font-size: .8rem; }
.mock-page :deep(.mock-notify-icon) { font-size: 1.1rem; }
.mock-page :deep(.mock-notify-desc) { display: block; font-size: .72rem; color: #6b7280; }
.mock-page :deep(.mock-member-grid) { display: flex; flex-direction: column; gap: 8px; }
.mock-page :deep(.mock-member) { display: flex; align-items: center; gap: 10px; font-size: .82rem; }
.mock-page :deep(.mock-avatar) { width: 28px; height: 28px; border-radius: 50%; background: #6366f1; color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: .72rem; font-weight: 700; }
</style>
