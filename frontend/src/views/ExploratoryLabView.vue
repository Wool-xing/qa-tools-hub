<template>
  <div class="lab-page">
    <!-- Setup Phase -->
    <div v-if="phase === 'setup'" class="card">
      <h3 style="margin-bottom:14px;">会话设置</h3>

      <label class="field-label">Charter 模板</label>
      <div class="template-bar">
        <button v-for="(t, i) in templates" :key="i" class="template-btn" :class="{ active: templateIdx === i }" @click="selectTemplate(i)">{{ t.label }}</button>
      </div>
      <textarea v-model="charter" rows="4" class="charter-input" placeholder="在此编写或修改你的测试 Charter..."></textarea>

      <label class="field-label">时间限制</label>
      <div class="time-selector">
        <button v-for="m in [30, 60, 90]" :key="m" class="time-btn" :class="{ active: timeLimit === m }" @click="timeLimit = m">{{ m }} 分钟</button>
      </div>

      <button class="btn-primary btn-start" @click="startSession">▶ 开始会话</button>
    </div>

    <!-- Active Session -->
    <div v-if="phase === 'active'" class="session-active">
      <div class="card charter-readonly">
        <div class="charter-label">测试 Charter</div>
        <p>{{ charter }}</p>
      </div>

      <div class="card timer-card">
        <div class="timer-ring-container">
          <svg class="timer-ring" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="52" fill="none" stroke="var(--border-light)" stroke-width="8" />
            <circle cx="60" cy="60" r="52" fill="none" stroke="var(--primary)" stroke-width="8"
              stroke-linecap="round" :stroke-dasharray="ringCircumference"
              :stroke-dashoffset="ringOffset" transform="rotate(-90 60 60)"
              style="transition: stroke-dashoffset .3s linear;" />
          </svg>
          <div class="timer-text">
            <span class="timer-time">{{ formattedTime }}</span>
            <span class="timer-label">{{ isPaused ? '已暂停' : '进行中' }}</span>
          </div>
        </div>
        <div class="timer-actions">
          <button v-if="!isPaused" class="btn-outline" @click="pauseSession">⏸️ 暂停</button>
          <button v-else class="btn-primary" @click="resumeSession">▶ 继续</button>
          <button class="btn-outline" style="color:var(--danger);border-color:var(--danger);" @click="endSession">⏹️ 结束会话</button>
        </div>
      </div>

      <div class="card obs-form">
        <h3 style="margin-bottom:12px;">➕ 添加观察</h3>
        <div class="obs-type-bar">
          <button v-for="t in obsTypes" :key="t.value" class="obs-type-btn" :class="{ active: obsType === t.value }" @click="obsType = t.value">{{ t.icon }} {{ t.label }}</button>
        </div>
        <textarea v-model="obsText" rows="3" class="obs-input" placeholder="描述你观察到的现象..."></textarea>
        <button class="btn-primary" :disabled="!obsText.trim()" @click="addObservation">📝 记录观察</button>
      </div>

      <div v-if="observations.length > 0" class="card">
        <h3 style="margin-bottom:12px;">📜 会话日志</h3>
        <div class="obs-log">
          <div v-for="(o, i) in observations" :key="i" class="obs-entry">
            <div class="obs-meta">
              <span class="obs-type-tag" :class="'obs-tag-' + o.type">{{ typeIcon(o.type) }} {{ typeLabel(o.type) }}</span>
              <span class="obs-time">{{ o.timestamp }}</span>
            </div>
            <p class="obs-body">{{ o.text }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Review Phase -->
    <div v-if="phase === 'review'" class="session-review">
      <div class="card">
        <h3 style="margin-bottom:8px;">会话完成</h3>
        <p class="review-summary">
          共 <strong>{{ formattedTime }}</strong> · <strong>{{ observations.length }}</strong> 条观察记录
        </p>
      </div>

      <div v-if="obsByType.Bug.length" class="card">
        <h3>Bug ({{ obsByType.Bug.length }})</h3>
        <ul class="review-list">
          <li v-for="(o, i) in obsByType.Bug" :key="i">{{ o.text }}</li>
        </ul>
      </div>
      <div v-if="obsByType.Idea.length" class="card">
        <h3>💡 测试思路 ({{ obsByType.Idea.length }})</h3>
        <ul class="review-list">
          <li v-for="(o, i) in obsByType.Idea" :key="i">{{ o.text }}</li>
        </ul>
      </div>
      <div v-if="obsByType.Question.length" class="card">
        <h3>❓ 疑问 ({{ obsByType.Question.length }})</h3>
        <ul class="review-list">
          <li v-for="(o, i) in obsByType.Question" :key="i">{{ o.text }}</li>
        </ul>
      </div>
      <div v-if="obsByType.Risk.length" class="card">
        <h3>风险 ({{ obsByType.Risk.length }})</h3>
        <ul class="review-list">
          <li v-for="(o, i) in obsByType.Risk" :key="i">{{ o.text }}</li>
        </ul>
      </div>

      <div class="card">
        <h3 style="margin-bottom:10px;">📝 复盘总结</h3>
        <textarea v-model="debrief" rows="5" class="obs-input" placeholder="写下你的 session 复盘：学到了什么？哪些地方可以改进？还有什么需要跟进？"></textarea>
      </div>

      <div class="review-actions">
        <button class="btn-primary" @click="copyMarkdown">复制为 Markdown</button>
        <button class="btn-outline" @click="resetAll">开始新会话</button>
      </div>
      <p v-if="copied" class="copied-msg">已复制到剪贴板！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onBeforeUnmount } from 'vue'

const phase = ref('setup')
const templateIdx = ref(0)
const charter = ref('')
const timeLimit = ref(30)
const isPaused = ref(false)
const elapsedSeconds = ref(0)
const obsType = ref('Bug')
const obsText = ref('')
const observations = ref([])
const debrief = ref('')
const copied = ref(false)
let timerInterval = null

const templates = [
  {
    label: '🔐 登录功能探索',
    text: '探索登录功能的安全性与边界：\n1. 正常登录流程（正确用户名/密码）\n2. 边界：空用户名、空密码、超长输入、特殊字符\n3. 安全：SQL注入、XSS、暴力破解防护、会话固定\n4. 错误处理：错误提示是否泄露信息、密码找回流程\n5. 状态：记住我、多设备登录、并发登录\n6. 兼容性：不同浏览器、移动端',
  },
  {
    label: '🔍 搜索功能探索',
    text: '探索搜索功能的正确性与边界：\n1. 正常搜索：有结果、无结果、单字符搜索\n2. 边界：超长关键词、特殊字符 (SQL注入/XSS)、空搜索\n3. 分页：第一页、中间页、最后一页、边界跳转\n4. 排序：每种排序独立验证，排序后翻页是否保持\n5. 过滤：多条件组合、清除过滤、URL参数同步\n6. 性能：大数据量搜索响应时间、并发搜索',
  },
  {
    label: '🗺️ 自由探索',
    text: '（在此编写你的自定义测试 Charter）\n\n目标功能：\n时间限制：\n测试重点：\n1.\n2.\n3.\n边界与风险区域：\n1.\n2.\n3.',
  },
]

const obsTypes = [
  { value: 'Bug', label: 'Bug', icon: '🐛' },
  { value: 'Idea', label: '思路', icon: '💡' },
  { value: 'Question', label: '疑问', icon: '❓' },
  { value: 'Risk', label: '风险', icon: '⚠️' },
]

const ringCircumference = 2 * Math.PI * 52

const totalSeconds = computed(() => timeLimit.value * 60)
const ringOffset = computed(() => {
  const progress = Math.min(elapsedSeconds.value / totalSeconds.value, 1)
  return ringCircumference * (1 - progress)
})
const formattedTime = computed(() => {
  const remaining = Math.max(0, totalSeconds.value - elapsedSeconds.value)
  const m = Math.floor(remaining / 60)
  const s = remaining % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
const formattedElapsed = computed(() => {
  const m = Math.floor(elapsedSeconds.value / 60)
  const s = elapsedSeconds.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
const obsByType = computed(() => ({
  Bug: observations.value.filter(o => o.type === 'Bug'),
  Idea: observations.value.filter(o => o.type === 'Idea'),
  Question: observations.value.filter(o => o.type === 'Question'),
  Risk: observations.value.filter(o => o.type === 'Risk'),
}))

function selectTemplate(i) {
  templateIdx.value = i
  charter.value = templates[i].text
}

function typeIcon(t) {
  const found = obsTypes.find(o => o.value === t)
  return found ? found.icon : '📌'
}

function typeLabel(t) {
  const found = obsTypes.find(o => o.value === t)
  return found ? found.label : t
}

function startSession() {
  elapsedSeconds.value = 0
  isPaused.value = false
  observations.value = []
  debrief.value = ''
  copied.value = false
  if (!charter.value.trim()) charter.value = templates[templateIdx.value].text
  phase.value = 'active'
  startTimer()
}

function pauseSession() {
  isPaused.value = true
  clearInterval(timerInterval)
  timerInterval = null
}

function resumeSession() {
  isPaused.value = false
  startTimer()
}

function startTimer() {
  clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    if (!isPaused.value) {
      elapsedSeconds.value++
      if (elapsedSeconds.value >= totalSeconds.value) {
        endSession()
      }
    }
  }, 1000)
}

function endSession() {
  clearInterval(timerInterval)
  timerInterval = null
  isPaused.value = false
  phase.value = 'review'
}

function addObservation() {
  if (!obsText.value.trim()) return
  const now = new Date()
  const ts = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  observations.value.push({
    type: obsType.value,
    text: obsText.value.trim(),
    timestamp: `${formattedElapsed.value} / ${ts}`,
  })
  obsText.value = ''
}

function resetAll() {
  phase.value = 'setup'
  elapsedSeconds.value = 0
  isPaused.value = false
  observations.value = []
  debrief.value = ''
  copied.value = false
  clearInterval(timerInterval)
  timerInterval = null
}

function generateMarkdown() {
  const lines = []
  lines.push('# 探索式测试报告')
  lines.push('')
  lines.push('## Charter')
  lines.push('')
  lines.push(charter.value.split('\n').map(l => `> ${l}`).join('\n'))
  lines.push('')
  lines.push('## 会话信息')
  lines.push('')
  lines.push(`- **耗时**：${formattedElapsed.value}`)
  lines.push(`- **观察总数**：${observations.value.length}`)
  lines.push(`- **Bug**：${obsByType.value.Bug.length} · **思路**：${obsByType.value.Idea.length} · **疑问**：${obsByType.value.Question.length} · **风险**：${obsByType.value.Risk.length}`)
  lines.push('')

  const sections = [
    { type: 'Bug', title: '🐛 Bug', items: obsByType.value.Bug },
    { type: 'Idea', title: '💡 测试思路', items: obsByType.value.Idea },
    { type: 'Question', title: '❓ 疑问', items: obsByType.value.Question },
    { type: 'Risk', title: '⚠️ 风险', items: obsByType.value.Risk },
  ]
  sections.forEach(s => {
    if (s.items.length) {
      lines.push(`## ${s.title}`)
      lines.push('')
      s.items.forEach(o => lines.push(`- [${o.timestamp}] ${o.text}`))
      lines.push('')
    }
  })

  if (debrief.value.trim()) {
    lines.push('## 复盘总结')
    lines.push('')
    lines.push(debrief.value)
  }

  return lines.join('\n')
}

async function copyMarkdown() {
  const md = generateMarkdown()
  try {
    await navigator.clipboard.writeText(md)
    copied.value = true
    setTimeout(() => { copied.value = false }, 3000)
  } catch (e) {
    // Fallback for older browsers
    const ta = document.createElement('textarea')
    ta.value = md
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
    setTimeout(() => { copied.value = false }, 3000)
  }
}

onBeforeUnmount(() => {
  clearInterval(timerInterval)
})
</script>

<style scoped>
.lab-page { max-width: 760px; margin: 0 auto; }

.field-label { display: block; font-size: .8rem; font-weight: 600; margin-bottom: 8px; margin-top: 14px; color: var(--text-secondary); }
.field-label:first-of-type { margin-top: 0; }

.template-bar { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.template-btn {
  padding: 8px 16px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .8rem; font-weight: 500;
  transition: all var(--fast); font-family: var(--font-sans);
}
.template-btn:hover { border-color: var(--primary); }
.template-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }

.charter-input {
  width: 100%; padding: 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-sans); font-size: .82rem; line-height: 1.7;
  background: var(--bg); color: var(--text); outline: none; resize: vertical;
}
.charter-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.time-selector { display: flex; gap: 8px; margin-bottom: 16px; }
.time-btn {
  padding: 10px 22px; border-radius: var(--radius-sm); border: 2px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .88rem; font-weight: 600;
  transition: all var(--fast); font-family: var(--font-mono);
}
.time-btn:hover { border-color: var(--primary); }
.time-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); }

.btn-start { padding: 12px 36px; font-size: .92rem; margin-top: 4px; }

/* Active session */
.charter-readonly { margin-bottom: var(--space-md); }
.charter-label { font-size: .74rem; color: var(--text-muted); font-weight: 600; margin-bottom: 8px; text-transform: uppercase; letter-spacing: .5px; }
.charter-readonly p { font-size: .84rem; line-height: 1.7; white-space: pre-wrap; }

.timer-card { display: flex; align-items: center; gap: 24px; margin-bottom: var(--space-md); }
.timer-ring-container { position: relative; width: 120px; height: 120px; flex-shrink: 0; }
.timer-ring { width: 120px; height: 120px; }
.timer-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; }
.timer-time { display: block; font-family: var(--font-mono); font-size: 1.3rem; font-weight: 700; color: var(--primary); }
.timer-label { display: block; font-size: .68rem; color: var(--text-muted); }
.timer-actions { display: flex; gap: 8px; flex-wrap: wrap; }

.obs-form { margin-bottom: var(--space-md); }
.obs-type-bar { display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap; }
.obs-type-btn {
  padding: 6px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .78rem; font-weight: 500;
  transition: all var(--fast); font-family: var(--font-sans);
}
.obs-type-btn:hover { border-color: var(--primary); }
.obs-type-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }
.obs-input {
  width: 100%; padding: 12px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-sans); font-size: .82rem; line-height: 1.6;
  background: var(--bg); color: var(--text); outline: none; resize: vertical; margin-bottom: 10px;
}
.obs-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.obs-log { display: flex; flex-direction: column; gap: 10px; }
.obs-entry { padding: 12px; background: var(--bg); border-radius: var(--radius-sm); border-left: 3px solid var(--border); }
.obs-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.obs-type-tag { padding: 2px 10px; border-radius: var(--radius-full); font-size: .7rem; font-weight: 600; }
.obs-tag-Bug { background: var(--danger-light); color: var(--danger); }
.obs-tag-Idea { background: var(--primary-light); color: var(--primary); }
.obs-tag-Question { background: var(--warning-light); color: var(--warning); }
.obs-tag-Risk { background: #fef3c7; color: #d97706; }
.obs-time { font-family: var(--font-mono); font-size: .7rem; color: var(--text-muted); }
.obs-body { font-size: .82rem; line-height: 1.6; color: var(--text); }

/* Review */
.review-summary { font-size: .88rem; color: var(--text-secondary); }
.review-list { padding-left: 18px; font-size: .82rem; line-height: 1.8; color: var(--text-secondary); }
.review-list li { margin-bottom: 4px; }
.review-actions { display: flex; gap: 10px; margin-top: var(--space-md); }
.copied-msg { margin-top: 8px; font-size: .82rem; color: var(--success); font-weight: 600; }
</style>
