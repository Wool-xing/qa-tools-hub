<template>
  <div class="lab-page">
    <!-- Main Layout: left panel (builder) + right panel (tester) -->
    <div class="mock-layout">
      <!-- ===== LEFT: Mock Builder ===== -->
      <div class="mock-left">
        <div class="card" style="margin-bottom:var(--space-md);">
          <h3 style="font-size:.9rem;margin-bottom:10px;">🔧 Mock 构建器</h3>
          <div class="form-row">
            <div class="form-group" style="flex:0 0 120px;">
              <label class="form-label">方法</label>
              <select v-model="mockForm.method" class="form-input">
                <option v-for="m in methods" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="form-group" style="flex:1;">
              <label class="form-label">路径</label>
              <input v-model="mockForm.path" placeholder="/api/test" class="form-input">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group" style="flex:1;">
              <label class="form-label">状态码</label>
              <input v-model.number="mockForm.status_code" type="number" min="100" max="599" class="form-input">
            </div>
            <div class="form-group" style="flex:2;">
              <label class="form-label">延迟 (ms): {{ mockForm.delay_ms }}</label>
              <input v-model.number="mockForm.delay_ms" type="range" min="0" max="5000" step="100" class="slider">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">响应体</label>
            <textarea v-model="mockForm.response_body" rows="4" class="sql-input" style="font-size:.78rem;"></textarea>
          </div>

          <!-- Fault Injection Presets -->
          <div style="margin-bottom:10px;">
            <label class="form-label" style="margin-bottom:6px;">⚡ 故障注入预设</label>
            <div class="preset-chips">
              <button class="preset-chip" @click="applyPreset('503')">💥 注入503错误</button>
              <button class="preset-chip" @click="applyPreset('delay')">🐌 注入5s延迟</button>
              <button class="preset-chip" @click="applyPreset('badjson')">🧨 注入格式错误JSON</button>
              <button class="preset-chip" @click="applyPreset('empty')">🕳️ 注入空响应</button>
            </div>
          </div>

          <button class="btn-primary" style="width:100%;justify-content:center;padding:10px;margin-bottom:8px;" @click="createMock">✅ 创建 Mock</button>

          <!-- Sequence Builder -->
          <details style="font-size:.8rem;">
            <summary style="cursor:pointer;font-weight:600;color:var(--primary);margin-bottom:8px;">📋 行为序列 (高级)</summary>
            <p style="color:var(--text-secondary);font-size:.74rem;margin-bottom:8px;">按调用顺序返回不同的响应</p>
            <div v-for="(step, i) in mockForm.sequence" :key="i" class="seq-step">
              <span class="seq-order">#{{ i + 1 }}</span>
              <input v-model.number="step.status_code" type="number" placeholder="状态码" class="seq-input" style="width:70px;">
              <input v-model="step.response_body" placeholder="响应体" class="seq-input" style="flex:1;">
              <input v-model.number="step.delay_ms" type="number" placeholder="延迟ms" class="seq-input" style="width:70px;">
              <button class="btn-ghost" style="font-size:.7rem;padding:2px 6px;color:var(--danger);" @click="mockForm.sequence.splice(i,1)">✕</button>
            </div>
            <button class="btn-outline" style="font-size:.72rem;padding:4px 12px;margin-top:6px;" @click="addSeqStep">+ 添加步骤</button>
          </details>
        </div>

        <!-- Mock List -->
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <h3 style="font-size:.9rem;">📋 已注册 Mock</h3>
            <button class="btn-ghost" style="font-size:.72rem;color:var(--danger);" @click="resetMocks">清空全部</button>
          </div>
          <div v-if="mockList.length === 0" style="color:var(--text-muted);font-size:.78rem;text-align:center;padding:16px;">暂无 Mock</div>
          <div v-for="m in mockList" :key="m.key" class="mock-item">
            <div class="mock-item-header">
              <span class="mock-method" :class="'method-' + m.key.split(':')[0].toLowerCase()">{{ m.key.split(':')[0] }}</span>
              <code style="font-size:.74rem;flex:1;">{{ m.key.split(':').slice(1).join(':') }}</code>
              <span style="font-size:.7rem;color:var(--text-muted);">调用 {{ m.calls || 0 }} 次</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== RIGHT: Test Panel ===== -->
      <div class="mock-right">
        <div class="card" style="margin-bottom:var(--space-md);">
          <h3 style="font-size:.9rem;margin-bottom:10px;">🧪 测试面板</h3>
          <div class="form-row">
            <div class="form-group" style="flex:0 0 110px;">
              <select v-model="testForm.method" class="form-input">
                <option v-for="m in methods" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="form-group" style="flex:1;">
              <input v-model="testForm.path" placeholder="/mock/api/test" class="form-input">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">请求体 (JSON)</label>
            <textarea v-model="testForm.body" rows="3" class="sql-input" style="font-size:.78rem;" placeholder='{"key": "value"}'></textarea>
          </div>
          <button class="btn-primary" style="width:100%;justify-content:center;padding:10px;" @click="sendTest" :disabled="testLoading">
            {{ testLoading ? '⏳ 发送中...' : '📤 发送请求' }}
          </button>

          <div v-if="testResult" class="test-result">
            <div class="result-row">
              <span class="result-label">状态码</span>
              <span class="result-value" :class="testResult.status >= 400 ? 'text-danger' : 'text-success'">{{ testResult.status }}</span>
            </div>
            <div class="result-row">
              <span class="result-label">耗时</span>
              <span class="result-value">{{ testResult.timing }}ms</span>
            </div>
            <div class="result-row">
              <span class="result-label">响应体</span>
            </div>
            <pre class="result-body">{{ testResult.body }}</pre>
          </div>
          <div v-if="testError" class="test-error">❌ {{ testError }}</div>
        </div>

        <!-- Challenge Scenarios -->
        <div class="card">
          <h3 style="font-size:.9rem;margin-bottom:10px;">🏆 挑战关卡</h3>
          <div class="challenge-bar">
            <button v-for="(c,i) in challenges" :key="i" class="challenge-btn" :class="{ active: chIdx === i, solved: chSolved[i] }"
              @click="selectChallenge(i)">{{ c.diff }} {{ c.label }}</button>
          </div>
          <div v-if="challenges[chIdx]" class="challenge-card">
            <p class="ch-task">{{ challenges[chIdx].task }}</p>
            <div class="ch-steps" v-if="challenges[chIdx].steps">
              <p v-for="(s, si) in challenges[chIdx].steps" :key="si" class="ch-step">{{ si + 1 }}. {{ s }}</p>
            </div>
            <div class="ch-actions" style="margin-top:10px;">
              <button class="btn-ghost" style="font-size:.72rem;" @click="showHint = !showHint">{{ showHint ? '隐藏' : '显示' }}提示</button>
            </div>
            <p v-if="showHint" class="ch-hint">💡 {{ challenges[chIdx].hint }}</p>
            <div v-if="chFeedback" class="ch-feedback" :class="chFeedback.ok ? 'pass' : 'fail'">
              {{ chFeedback.ok ? '🎉 完成！' : '💪 ' }}{{ chFeedback.msg }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { labs } from '../api'

const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

// Mock form
const mockForm = reactive({
  method: 'GET',
  path: '/api/test',
  status_code: 200,
  response_body: '{"ok": true, "data": []}',
  delay_ms: 0,
  sequence: [],
})

function addSeqStep() {
  mockForm.sequence.push({ status_code: 200, response_body: '{}', delay_ms: 0 })
}

function applyPreset(type) {
  mockForm.sequence = []
  if (type === '503') {
    mockForm.status_code = 503
    mockForm.response_body = '{"error": "Service Unavailable"}'
    mockForm.delay_ms = 0
  } else if (type === 'delay') {
    mockForm.status_code = 200
    mockForm.response_body = '{"ok": true}'
    mockForm.delay_ms = 5000
  } else if (type === 'badjson') {
    mockForm.status_code = 200
    mockForm.response_body = '{ok: true, broken json'
    mockForm.delay_ms = 0
  } else if (type === 'empty') {
    mockForm.status_code = 200
    mockForm.response_body = ''
    mockForm.delay_ms = 0
  }
}

async function createMock() {
  try {
    await labs.mock.create({
      method: mockForm.method,
      path: mockForm.path,
      status_code: mockForm.status_code,
      response_body: mockForm.response_body,
      delay_ms: mockForm.delay_ms,
      sequence: mockForm.sequence,
    })
    await loadMocks()
  } catch (e) {
    alert('创建失败: ' + e.message)
  }
}

// Test panel
const testForm = reactive({ method: 'GET', path: '/mock/api/test', body: '' })
const testLoading = ref(false)
const testResult = ref(null)
const testError = ref(null)

async function sendTest() {
  testLoading.value = true; testResult.value = null; testError.value = null
  const start = performance.now()
  try {
    const headers = { 'Content-Type': 'application/json' }
    const token = localStorage.getItem('qa-pro-token')
    if (token) headers['Authorization'] = `Bearer ${token}`
    const opts = { method: testForm.method, headers }
    if (testForm.method !== 'GET' && testForm.body) {
      try { opts.body = JSON.stringify(JSON.parse(testForm.body)) } catch { testError.value = '[警告] JSON 格式无效，已作为纯文本发送'; opts.body = testForm.body }
    }
    const res = await fetch(testForm.path, opts)
    const timing = Math.round(performance.now() - start)
    let body
    try { body = await res.text() } catch { body = '[无法读取响应]' }
    try { body = JSON.stringify(JSON.parse(body), null, 2) } catch { /* raw text */ }
    testResult.value = { status: res.status, timing, body }
  } catch (e) {
    testError.value = e.message
  }
  testLoading.value = false
}

// Mock list
const mockList = ref([])

async function loadMocks() {
  try {
    const data = await labs.mock.stats()
    mockList.value = data.mocks.map(k => ({
      key: k,
      calls: data.call_counts[k] || 0,
    }))
  } catch { /* ignore */ }
}

async function resetMocks() {
  try { await labs.mock.reset(); await loadMocks() } catch { /* ignore */ }
}

// Challenges
const chIdx = ref(0)
const showHint = ref(false)
const chFeedback = ref(null)
const chSolved = ref([false, false, false])

const challenges = [
  {
    diff: '⭐', label: '初级',
    task: 'Payment service returns 503. Write test that retries once and handles gracefully.',
    hint: '创建 GET /mock/payment 返回503。在测试面板中发送请求，验证返回503状态码。思考：你的测试代码如何实现重试逻辑？',
    steps: ['用 Mock 构建器创建 GET /mock/payment，状态码 503', '在测试面板发送 GET /mock/payment', '确认返回 503', '思考：编写测试代码时如何添加重试逻辑'],
  },
  {
    diff: '⭐⭐', label: '中级',
    task: 'Inventory service has 2s latency. Verify checkout times out at 3s and shows error message.',
    hint: '创建 GET /mock/inventory 延迟 2000ms。在测试面板调用它，观察响应时间。思考：如何设置 3s 超时阈值？',
    steps: ['创建 GET /mock/inventory，delay_ms = 2000，status_code = 200', '在测试面板发送请求，观察耗时是否约 2s', '思考：你的测试框架如何设置 fetch 超时 = 3s？(AbortController)'],
  },
  {
    diff: '⭐⭐⭐', label: '高级',
    task: 'Mock all 4 dependencies of Order Service (payment, inventory, user, notification). Test order creation end-to-end.',
    hint: '创建4个Mock端点。在测试面板依次调用它们，模拟一个完整的订单创建流程。',
    steps: [
      '创建 POST /mock/payment → 200 {"paid": true}',
      '创建 GET /mock/inventory → 200 {"stock": 99}',
      '创建 GET /mock/user → 200 {"id": 1, "name": "test"}',
      '创建 POST /mock/notification → 201 {"sent": true}',
      '在测试面板按顺序调用这4个端点',
      '验证每个端点返回预期的状态码和响应',
    ],
  },
]

function selectChallenge(i) {
  chIdx.value = i
  showHint.value = false
  chFeedback.value = null
}

onMounted(() => { loadMocks() })
</script>

<style scoped>
.lab-page { max-width: 1100px; margin: 0 auto; }
.breadcrumb a { color: var(--primary); text-decoration: none; }
.breadcrumb a:hover { text-decoration: underline; }

.mock-layout { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md); }
@media (max-width: 860px) { .mock-layout { grid-template-columns: 1fr; } }

.form-row { display: flex; gap: 8px; margin-bottom: 8px; }
.form-group { display: flex; flex-direction: column; margin-bottom: 8px; }
.form-label { font-size: .74rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 4px; }
.form-input {
  padding: 8px 10px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .82rem; font-family: var(--font-sans); background: var(--bg); color: var(--text);
  outline: none; transition: all var(--fast); width: 100%;
}
.form-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
select.form-input { cursor: pointer; }

.slider { width: 100%; accent-color: var(--primary); cursor: pointer; }

.sql-input {
  width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .78rem; line-height: 1.6;
  background: #1a1a2e; color: #e5e7eb; outline: none; resize: vertical;
}
[data-theme="dark"] .sql-input { background: #0f1117; color: #e5e7eb; }
.sql-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.preset-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.preset-chip {
  padding: 5px 10px; border-radius: var(--radius-sm); border: 1px solid var(--warning);
  background: var(--warning-light); color: var(--warning); cursor: pointer;
  font-size: .72rem; font-weight: 600; font-family: var(--font-sans);
  transition: all var(--fast);
}
.preset-chip:hover { filter: brightness(.95); transform: scale(1.03); }

.seq-step { display: flex; gap: 4px; align-items: center; margin-bottom: 4px; }
.seq-order { font-size: .7rem; font-weight: 700; color: var(--text-muted); min-width: 22px; }
.seq-input {
  padding: 4px 6px; border: 1px solid var(--border); border-radius: 4px;
  font-size: .72rem; font-family: var(--font-mono); background: var(--bg); color: var(--text); outline: none;
}
.seq-input:focus { border-color: var(--primary); }

.mock-item { padding: 8px 0; border-bottom: 1px solid var(--border-light); }
.mock-item:last-child { border-bottom: none; }
.mock-item-header { display: flex; align-items: center; gap: 8px; }
.mock-method {
  font-size: .66rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;
  background: var(--primary-light); color: var(--primary); font-family: var(--font-mono);
  min-width: 48px; text-align: center;
}
.mock-method.method-get { background: var(--success-light); color: var(--success); }
.mock-method.method-post { background: var(--info-light); color: var(--info); }
.mock-method.method-put { background: var(--warning-light); color: var(--warning); }
.mock-method.method-delete { background: var(--danger-light); color: var(--danger); }
.mock-method.method-patch { background: #f3e8ff; color: #9333ea; }

.test-result { margin-top: 12px; padding: 12px; background: var(--bg-subtle); border-radius: var(--radius-sm); }
.result-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.result-label { font-size: .74rem; font-weight: 600; color: var(--text-secondary); min-width: 50px; }
.result-value { font-size: .82rem; font-family: var(--font-mono); font-weight: 700; }
.text-success { color: var(--success); }
.text-danger { color: var(--danger); }
.result-body {
  font-size: .74rem; font-family: var(--font-mono); background: #1a1a2e; color: #e5e7eb;
  padding: 10px; border-radius: var(--radius-sm); overflow-x: auto; max-height: 200px; white-space: pre-wrap; word-break: break-all;
}
[data-theme="dark"] .result-body { background: #0f1117; }
.test-error { margin-top: 10px; padding: 8px 12px; background: var(--danger-light); color: var(--danger); border-radius: var(--radius-sm); font-size: .78rem; }

.challenge-bar { display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap; }
.challenge-btn {
  padding: 6px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .76rem; transition: all var(--fast); font-family: var(--font-sans);
}
.challenge-btn:hover { border-color: var(--primary); }
.challenge-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }
.challenge-btn.solved { border-color: var(--success); background: var(--success-light); }
.challenge-card { padding: 14px; background: var(--bg-subtle); border-radius: var(--radius); }
.ch-task { font-size: .86rem; font-weight: 600; margin-bottom: 8px; }
.ch-steps { margin-bottom: 8px; }
.ch-step { font-size: .76rem; color: var(--text-secondary); margin-bottom: 4px; line-height: 1.5; }
.ch-hint { font-size: .78rem; color: var(--primary); margin-top: 8px; padding: 8px; background: var(--primary-light); border-radius: 4px; font-family: var(--font-mono); }
.ch-actions { display: flex; justify-content: space-between; align-items: center; }
.ch-feedback { margin-top: 8px; padding: 8px 12px; border-radius: 6px; font-size: .8rem; font-weight: 500; }
.ch-feedback.pass { background: var(--success-light); color: #065f46; }
.ch-feedback.fail { background: var(--warning-light); color: #92400e; }
</style>
