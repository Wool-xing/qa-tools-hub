<template>
  <div v-if="store.current" class="player">
    <!-- Breadcrumb -->


    <div class="page-header" style="margin-bottom:var(--space-md);">
      <h1>{{ store.current.title }}</h1>
      <p>{{ store.current.description }}</p>
    </div>

    <!-- Tabs -->
    <div class="tabs" role="tablist" aria-label="关卡内容">
      <button role="tab" :aria-selected="tab==='read' ? 'true' : 'false'" :class="{ active: tab==='read' }" @click="tab='read'">📖 学习理论</button>
      <button v-if="store.current.demo" role="tab" :aria-selected="tab==='watch' ? 'true' : 'false'" :class="{ active: tab==='watch' }" @click="tab='watch'">👀 看演示</button>
      <button role="tab" :aria-selected="tab==='do' ? 'true' : 'false'" :class="{ active: tab==='do' }" @click="tab='do'">✍️ 动手练习</button>
    </div>

    <!-- Read tab -->
    <div v-if="tab==='read'" class="content-panel markdown" v-html="rendered"></div>

    <!-- Watch tab -->
    <div v-if="tab==='watch' && store.current.demo" class="content-panel markdown" v-html="demoHtml"></div>

    <!-- Do tab -->
    <div v-if="tab==='do'" class="task-panel">
      <!-- Quiz -->
      <div v-if="store.current.task_type==='quiz'">
        <div class="task-prompt">{{ store.current.task_config.question }}</div>
        <button v-for="(opt, i) in store.current.task_config.options" :key="i"
          class="quiz-opt" :class="{
            selected: answer.choice===i,
            correct: showResult && i === store.current.task_config.correct_index,
            wrong: showResult && answer.choice===i && i !== store.current.task_config.correct_index
          }"
          :disabled="showResult"
          role="radio" :aria-checked="answer.choice===i ? 'true' : 'false'"
          @click="answer.choice=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span>
          <span>{{ opt }}</span>
        </button>
        <button v-if="!showResult" class="btn-primary" style="width:100%;justify-content:center;padding:12px;margin-top:12px;" :disabled="answer.choice===undefined" @click="doSubmit">提交答案</button>
      </div>

      <!-- Code -->
      <div v-if="store.current.task_type==='code'">
        <div class="content-panel markdown" v-html="rendered" style="margin-bottom:var(--space-md);"></div>
        <div class="code-editor">
          <div class="ce-header">
            <span class="ce-dot red"></span><span class="ce-dot yellow"></span><span class="ce-dot green"></span>
            <span class="ce-fname">solution.py</span>
            <button class="ce-run-btn" @click="runCode" :disabled="!answer.code">▶ 运行</button>
          </div>
          <div class="ce-body"><textarea v-model="answer.code" placeholder="# 在这里写你的 Python 代码..." class="ce-textarea numbered" spellcheck="false" @keydown="handleTab"></textarea></div>
          <div v-if="runResult !== null" class="ce-output" :class="{ error: !runResult.ok }">
            <div v-if="runResult.ok" class="output-text">{{ runResult.stdout || '(无输出)' }}</div>
            <div v-if="runResult.stderr" class="output-err">{{ runResult.stderr }}</div>
            <div v-if="!runResult.ok" class="output-err">{{ runResult.error }}</div>
          </div>
        </div>
        <button v-if="!showResult" class="btn-primary" style="width:100%;justify-content:center;padding:12px;margin-top:12px;" :disabled="!answer.code" @click="doSubmit">提交代码</button>
      </div>

      <!-- Debug -->
      <div v-if="store.current.task_type==='debug'">
        <div class="content-panel markdown" v-html="rendered" style="margin-bottom:var(--space-md);"></div>
        <div class="hint-box">下面的代码有Bug。找出问题并修复它——代码必须运行成功且通过所有检查才算过关。</div>
        <div class="code-editor">
          <div class="ce-header">
            <span class="ce-dot red"></span><span class="ce-dot yellow"></span><span class="ce-dot green"></span>
            <span class="ce-fname">buggy.py</span>
            <button class="ce-run-btn" @click="runCode" :disabled="!answer.code">▶ 运行</button>
          </div>
          <div class="ce-body"><textarea v-model="answer.code" class="ce-textarea numbered" spellcheck="false" @keydown="handleTab"></textarea></div>
          <div v-if="runResult !== null" class="ce-output" :class="{ error: !runResult.ok }">
            <div v-if="runResult.ok" class="output-text">{{ runResult.stdout || '(无输出)' }}</div>
            <div v-if="runResult.stderr" class="output-err">{{ runResult.stderr }}</div>
            <div v-if="!runResult.ok" class="output-err">{{ runResult.error }}</div>
          </div>
        </div>
        <button v-if="!showResult" class="btn-primary" style="width:100%;justify-content:center;padding:12px;margin-top:12px;" :disabled="!answer.code" @click="doSubmit">提交修复</button>
      </div>

      <!-- Scenario -->
      <div v-if="store.current.task_type==='scenario'">
        <div class="content-panel markdown" v-html="rendered" style="margin-bottom:var(--space-md);"></div>
        <div class="scenario-q">{{ store.current.task_config.question }}</div>
        <button v-for="(opt, i) in store.current.task_config.options" :key="i"
          class="quiz-opt" :class="{
            selected: answer.choice===i,
            correct: showResult && i === store.current.task_config.correct_index,
            wrong: showResult && answer.choice===i && i !== store.current.task_config.correct_index
          }" :disabled="showResult"
          role="radio" :aria-checked="answer.choice===i ? 'true' : 'false'"
          @click="answer.choice=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span>
          <span>{{ opt.slice(2).trim() }}</span>
        </button>
        <button v-if="!showResult" class="btn-primary" style="width:100%;justify-content:center;padding:12px;margin-top:12px;" :disabled="answer.choice===undefined" @click="doSubmit">提交判断</button>
      </div>

      <!-- Explore -->
      <div v-if="store.current.task_type==='explore'">
        <div class="content-panel markdown" v-html="rendered" style="margin-bottom:var(--space-md);"></div>
        <textarea v-model="answer.text" placeholder="写下你的理解和回答..." class="explore-textarea" rows="6"></textarea>
        <button v-if="!showResult" class="btn-primary" style="width:100%;justify-content:center;padding:12px;margin-top:12px;" :disabled="!answer.text" @click="doSubmit">提交回答</button>
      </div>

      <!-- Analyze (data-driven quiz) -->
      <div v-if="store.current.task_type==='analyze'">
        <div class="content-panel markdown" v-html="rendered" style="margin-bottom:var(--space-md);"></div>
        <div class="data-card" v-html="analyzeDataHtml"></div>
        <div class="task-prompt">{{ store.current.task_config.question }}</div>
        <button v-for="(opt, i) in store.current.task_config.options" :key="i"
          class="quiz-opt" :class="{
            selected: answer.choice===i,
            correct: showResult && i === store.current.task_config.correct_index,
            wrong: showResult && answer.choice===i && i !== store.current.task_config.correct_index
          }"
          :disabled="showResult"
          role="radio" :aria-checked="answer.choice===i ? 'true' : 'false'"
          @click="answer.choice=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span>
          <span>{{ opt }}</span>
        </button>
        <button v-if="!showResult" class="btn-primary" style="width:100%;justify-content:center;padding:12px;margin-top:12px;" :disabled="answer.choice===undefined" @click="doSubmit">提交答案</button>
      </div>
    </div>

    <!-- Result -->
    <div v-if="store.result" class="result" :class="{ pass: store.result.correct || store.result.score>=70, fail: !store.result.correct && store.result.score<70 }">
      <div class="result-icon">{{ store.result.correct || store.result.score>=70 ? '🎉' : '🤔' }}</div>
      <h2>{{ store.result.correct || store.result.score>=70 ? '恭喜过关！' : '再试一次' }}</h2>
      <p>得分: {{ store.result.score }} 分 | 第 {{ store.result.attempts }} 次尝试</p>
      <p v-if="store.result.explanation" class="explain">{{ store.result.explanation }}</p>
      <div class="result-actions">
        <button v-if="store.result.completed" @click="goNext" class="btn-primary" style="justify-content:center;">继续下一关</button>
        <button v-else @click="resetTask" class="btn-outline">再试一次</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLevelsStore } from '../stores/levels'
import { levels as levelsApi } from '../api'

const store = useLevelsStore()
const route = useRoute()
const router = useRouter()
const tab = ref('read')
const answer = reactive({})
const showResult = ref(false)
const runResult = ref(null)

/* Enhanced markdown renderer */
function md(str) {
  if (!str) return ''
  let html = str
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  // Protect code blocks from later replacements
  const codeBlocks = []
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    const idx = codeBlocks.length
    const langTag = lang ? `<span class="code-lang">${lang}</span>` : ''
    codeBlocks.push(`<div class="code-block">${langTag}<pre><code>${code.trim().replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre></div>`)
    return `%%CODEBLOCK_${idx}%%`
  })

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // Headings
  html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>')
  // Unordered lists (must come before <br> replacement)
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>')
  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
  // Numbered lists (require preceding blank line to avoid matching versions/dates)
  html = html.replace(/(?:^|\n\n)(\d+)\. (.+)$/gm, (_, num, text) => {
    const n = parseInt(num)
    if (n >= 1 && n <= 30) return '\n<li>' + text + '</li>'
    return _ + '. ' + text
  })
  // Paragraphs
  html = html.replace(/\n\n+/g, '</p><p>')
  html = html.replace(/\n/g, '<br>')

  // Restore code blocks
  html = html.replace(/%%CODEBLOCK_(\d+)%%/g, (_, idx) => codeBlocks[parseInt(idx)] || '')

  if (!html.startsWith('<')) html = '<p>' + html + '</p>'
  return html
}

const rendered = computed(() => md(store.current?.theory))
const demoHtml = computed(() => md(store.current?.demo))
const analyzeDataHtml = computed(() => md(store.current?.task_config?.data_block || ''))

async function doSubmit() {
  const body = store.current.task_type === 'quiz' || store.current.task_type === 'analyze' ? { choice: answer.choice }
    : store.current.task_type === 'code' ? { code: answer.code }
    : { text: answer.text }
  await store.submit(store.current.id, body)
  showResult.value = true
}

async function runCode() {
  runResult.value = { ok: false, error: '运行中...' }
  try {
    const data = await levelsApi.runCode(store.current.id, answer.code)
    runResult.value = data
  } catch (e) {
    runResult.value = { ok: false, error: e.message }
  }
}

function handleTab(e) { if (e.key === 'Tab') { e.preventDefault(); const ta = e.target; const s = ta.selectionStart; ta.value = ta.value.slice(0, s) + '    ' + ta.value.slice(ta.selectionEnd); ta.selectionStart = ta.selectionEnd = s + 4 } }

function resetTask() {
  store.resetResult()
  showResult.value = false
  runResult.value = null
  answer.choice = undefined
  answer.code = ''
  answer.text = ''
}

async function goNext() {
  await store.fetchList() // refresh so next level unlocks
  const curOrder = store.current?.order
  const allLevels = [...store.levels].sort((a, b) => a.order - b.order)
  const next = allLevels.find(l => l.order === curOrder + 1 && l.status !== 'locked')
  if (next) router.push('/level/' + next.id)
  else router.push('/levels')
}

const curId = computed(() => parseInt(route.params.id))
onMounted(async () => { try { await store.fetchLevel(curId.value) } catch { /* router guard or error boundary */ } initDebugCode() })
watch(curId, async (id) => { if (id) { try { await store.fetchLevel(id) } catch { /* ignore */ } resetTask(); tab.value = 'read'; initDebugCode() } })

function initDebugCode() {
  if (store.current?.task_type === 'debug' && store.current?.demo) {
    if (!answer.code || answer.code === store.current.demo) {
      answer.code = store.current.demo
    }
  }
}
</script>

<style scoped>
.player { max-width: 760px; margin: 0 auto; }

/* Breadcrumb */


/* Tabs */
.tabs {
  display: flex; gap: 4px; margin-bottom: var(--space-md);
  background: var(--surface); border-radius: var(--radius); padding: 4px;
  border: 1px solid var(--border);
}
.tabs button {
  flex: 1; padding: 10px; border: none; background: none; border-radius: 8px;
  cursor: pointer; font-size: .84rem; color: var(--text-secondary); font-weight: 500;
  transition: all var(--fast); font-family: var(--font-sans);
}
.tabs button.active { background: var(--primary); color: #fff; font-weight: 600; box-shadow: var(--shadow-xs); }
.tabs button:disabled { opacity: .4; cursor: not-allowed; }

/* Content panel */
.content-panel {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 28px;
  line-height: 1.75; font-size: .9rem;
}
.markdown :deep(p) { margin-bottom: 14px; }
.markdown :deep(strong) { color: var(--primary); font-weight: 650; }
.markdown :deep(h3) { font-size: 1.05rem; margin: 20px 0 10px; font-weight: 700; }
.markdown :deep(h4) { font-size: .95rem; margin: 16px 0 8px; font-weight: 650; }
.markdown :deep(ul), .markdown :deep(ol) { margin: 8px 0; padding-left: 20px; }
.markdown :deep(li) { margin-bottom: 4px; }
.markdown :deep(code) {
  background: var(--primary-light); padding: 2px 7px; border-radius: 4px;
  font-family: var(--font-mono); font-size: .8rem; color: var(--primary);
}
.markdown :deep(.code-block) {
  background: #1a1a2e; color: #e5e7eb; border-radius: var(--radius);
  margin: 14px 0; overflow: hidden; position: relative;
}
.markdown :deep(.code-lang) {
  position: absolute; top: 6px; right: 12px;
  font-size: .65rem; color: #6b7280; text-transform: uppercase; letter-spacing: .5px;
}
.markdown :deep(.code-block pre) {
  padding: 18px 20px; overflow-x: auto; margin: 0;
}
.markdown :deep(.code-block code) {
  background: none; color: inherit; padding: 0; font-size: .82rem; line-height: 1.7;
}

/* Task panel */
.task-panel { margin-top: 4px; }
.task-prompt { font-size: 1rem; font-weight: 600; margin-bottom: var(--space-md); line-height: 1.6; }
.scenario-q { font-size: 1rem; font-weight: 600; margin-bottom: var(--space-md); line-height: 1.6; padding: 14px; background: #fef3c7; border-radius: var(--radius); border: 1px solid #f59e0b; }

/* Analyze data card */
.data-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 16px 20px; margin-bottom: var(--space-md); font-family: var(--font-mono); font-size: .8rem;
  line-height: 1.6; overflow-x: auto; white-space: pre-wrap;
}

/* Quiz options */
.quiz-opt {
  display: flex; align-items: center; gap: 12px; width: 100%; padding: 14px 16px;
  margin-bottom: 8px; border: 2px solid var(--border); border-radius: var(--radius);
  background: var(--surface); cursor: pointer; font-size: .88rem; text-align: left;
  transition: all var(--fast); font-family: var(--font-sans);
}
.quiz-opt:hover:not(:disabled) { border-color: var(--primary); background: var(--primary-light); }
.quiz-opt.selected { border-color: var(--primary); background: var(--primary-light); font-weight: 600; }
.quiz-opt.correct { border-color: var(--success); background: var(--success-light); }
.quiz-opt.wrong { border-color: var(--danger); background: var(--danger-light); }
.quiz-opt:disabled { cursor: default; }
.opt-letter {
  width: 28px; height: 28px; border-radius: var(--radius-sm);
  background: var(--border-light); display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: .78rem; flex-shrink: 0;
}
.quiz-opt.selected .opt-letter { background: var(--primary); color: #fff; }
.quiz-opt.correct .opt-letter { background: var(--success); color: #fff; }
.quiz-opt.wrong .opt-letter { background: var(--danger); color: #fff; }

/* Code editor */
.code-editor {
  background: #1a1a2e; border-radius: var(--radius-lg); overflow: hidden;
  border: 1px solid #2d2d4a;
}
.ce-header {
  display: flex; align-items: center; gap: 8px; padding: 10px 14px;
  background: #16162a; border-bottom: 1px solid #2d2d4a;
}
.ce-dot { width: 10px; height: 10px; border-radius: 50%; }
.ce-dot.red { background: #ff5f57; } .ce-dot.yellow { background: #febc2e; } .ce-dot.green { background: #28c840; }
.ce-fname { color: #a0a0b8; font-size: .72rem; font-family: var(--font-mono); flex: 1; }
.ce-run-btn {
  padding: 4px 14px; border: 1px solid #28c840; border-radius: 4px;
  background: transparent; color: #28c840; cursor: pointer;
  font-size: .74rem; font-weight: 600; font-family: var(--font-sans);
  transition: all var(--fast);
}
.ce-run-btn:hover:not(:disabled) { background: #28c840; color: #000; }
.ce-run-btn:disabled { opacity: .4; cursor: not-allowed; }
.ce-body { display: flex; }
.ce-textarea {
  width: 100%; min-height: 200px; padding: 16px 12px; border: none;
  font-family: var(--font-mono); font-size: .82rem; line-height: 1.7;
  background: transparent; color: #e5e7eb; resize: vertical; outline: none;
  tab-size: 4;
}
.ce-textarea.numbered {
  padding-left: 52px;
  background-image: linear-gradient(#2d2d4a 1px, transparent 1px);
  background-size: 100% 27.2px;
  background-position: 0 16px;
}
.ce-textarea::placeholder { color: #6b7280; }
.ce-output { padding: 12px 20px; border-top: 1px solid #2d2d4a; font-family: var(--font-mono); font-size: .78rem; }
.ce-output .output-text { color: #e5e7eb; white-space: pre-wrap; }
.ce-output .output-err { color: #ef4444; white-space: pre-wrap; }
.ce-output.error { background: rgba(239,68,68,.05); }

/* Explore */
.explore-textarea {
  width: 100%; padding: 14px; border: 1px solid var(--border); border-radius: var(--radius);
  font-family: var(--font-sans); font-size: .86rem; resize: vertical; outline: none;
  background: var(--surface); color: var(--text); line-height: 1.6;
}
.explore-textarea:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

/* Result */
.result {
  margin-top: var(--space-lg); padding: 32px; border-radius: var(--radius-lg);
  text-align: center; border: 2px solid var(--border); background: var(--surface);
}
.result.pass { border-color: var(--success); }
.result.fail { border-color: var(--warning); }
.result-icon { font-size: 3.5rem; margin-bottom: 8px; }
.result h2 { font-size: 1.3rem; margin-bottom: 8px; }
.result p { color: var(--text-secondary); font-size: .88rem; margin-bottom: 4px; }
.explain {
  margin-top: 14px !important; padding: 14px;
  background: var(--primary-light); border-radius: var(--radius);
  color: var(--text) !important; font-size: .85rem !important;
  line-height: 1.6; text-align: left;
}
.result-actions { margin-top: 20px; display: flex; gap: 10px; justify-content: center; }
</style>
