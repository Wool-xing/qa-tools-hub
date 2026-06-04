<template>
  <div class="lab-page">
    <div class="card" style="margin-bottom:var(--space-md);">
      <div class="req-bar">
        <select v-model="method" class="method-select">
          <option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option><option>PATCH</option>
        </select>
        <input v-model="url" class="url-input" placeholder="https://httpbin.org/get" spellcheck="false">
        <button class="btn-primary" @click="sendRequest">▶ 发送</button>
      </div>

      <details class="panel-details">
        <summary>📋 Headers ({{ activeHeaderCount }})</summary>
        <div>
          <div v-for="(h, i) in headers" :key="i" class="header-row">
            <input v-model="h.key" placeholder="Header 名称" class="h-key" spellcheck="false">
            <input v-model="h.value" placeholder="值" class="h-val" spellcheck="false">
            <button class="h-remove" @click="headers.splice(i, 1)">×</button>
          </div>
          <button class="add-header" @click="headers.push({key:'',value:''})">+ 添加 Header</button>
        </div>
      </details>

      <details v-if="method !== 'GET'" class="panel-details">
        <summary>📦 Request Body</summary>
        <textarea v-model="body" class="body-input" rows="5" placeholder='{"key": "value"}' spellcheck="false"></textarea>
      </details>
    </div>

    <div v-if="loading" class="card" style="text-align:center;padding:32px;color:var(--text-secondary);">⏳ 发送请求中...</div>

    <div v-if="response" class="card" style="overflow:hidden;padding:0;margin-bottom:var(--space-md);">
      <div class="resp-header">
        <span class="resp-status" :class="statusClass">{{ response.status }} {{ response.statusText }}</span>
        <span class="resp-time">{{ response.time }}ms</span>
      </div>
      <div class="resp-body">
        <pre>{{ formattedBody }}</pre>
      </div>
    </div>

    <div v-if="response" class="card">
      <h3 style="font-size:.9rem;margin-bottom:10px;">✅ 断⾔检查</h3>
      <div class="assert-checks">
        <span class="assert-item" :class="{ pass: checks.status, fail: checks.status === false }">
          {{ checks.status ? '✅' : '❌' }} 状态码 2xx
        </span>
        <span class="assert-item" :class="{ pass: checks.json, fail: checks.json === false }">
          {{ checks.json ? '✅' : '❌' }} 有效 JSON
        </span>
        <span class="assert-item" :class="{ pass: checks.time, fail: checks.time === false }">
          {{ checks.time ? '✅' : '❌' }} 响应 &lt; 1s
        </span>
      </div>
    </div>

    <!-- Advanced: Variables + Schema -->
    <div class="card" style="margin-bottom:var(--space-md);margin-top:var(--space-md);">
      <h3 style="font-size:.88rem;margin-bottom:8px;">🔗 变量提取与链式请求</h3>
      <div class="var-row">
        <div class="field"><label>变量名</label><input v-model="varName" placeholder="token" class="form-input" style="font-size:.8rem;padding:6px 10px;"></div>
        <div class="field"><label>JSON路径 (点分隔)</label><input v-model="varPath" placeholder="access_token" class="form-input" style="font-size:.8rem;padding:6px 10px;"></div>
        <button class="btn-outline" style="font-size:.74rem;" @click="extractVar" :disabled="!response">📌 从响应提取</button>
      </div>
      <div v-if="Object.keys(variables).length" class="var-chips">
        <span v-for="(v,k) in variables" :key="k" class="var-chip">{{ k }} = {{ v }}</span>
        <button class="var-clear" @click="variables={};varName='';varPath=''">清除全部</button>
      </div>
      <p class="hint-text" style="margin-top:6px;">在 URL/Body/Headers 中使用 <code v-pre>{{ variable_name }}</code> 引用变量</p>
    </div>

    <!-- Schema Validation -->
    <div class="card" style="margin-bottom:var(--space-md);">
      <h3 style="font-size:.88rem;margin-bottom:8px;">📐 响应Schema验证</h3>
      <textarea v-model="schemaText" class="body-input" rows="4" placeholder='{"type":"object","required":["id","name"],"properties":{"id":{"type":"integer"},"name":{"type":"string"}}}' style="font-size:.78rem;"></textarea>
      <button class="btn-outline" style="font-size:.74rem;margin-top:6px;" @click="validateSchema" :disabled="!response">🔍 验证Schema</button>
      <div v-if="schemaResult" class="schema-result" :class="schemaResult.valid ? 'pass' : 'fail'">
        {{ schemaResult.valid ? '✅ Schema 匹配' : '❌ ' + schemaResult.error }}
      </div>
    </div>

    <!-- Request History -->
    <details class="hints-card" v-if="history.length">
      <summary>📜 请求历史 ({{ history.length }})</summary>
      <div v-for="(h,i) in history.slice(-10).reverse()" :key="i" class="hist-item" @click="replayRequest(h)">
        <span class="hist-method" :class="'m-'+h.method">{{ h.method }}</span>
        <span class="hist-url">{{ h.url.slice(0,60) }}</span>
        <span class="hist-status" :class="h.status >= 200 && h.status < 300 ? 'ok' : 'err'">{{ h.status || '?' }}</span>
        <span class="hist-time">{{ h.time }}ms</span>
      </div>
    </details>

    <div style="margin-top:var(--space-lg);">
      <h3 style="font-size:.9rem;margin-bottom:10px;">🎯 练习场景</h3>
      <div class="scenario-list">
        <button v-for="s in scenarios" :key="s.label" class="scenario-item" @click="applyScenario(s)">
          <strong>{{ s.label }}</strong>
          <span>{{ s.method }} {{ s.url }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const method = ref('GET')
const url = ref('https://httpbin.org/get')
const headers = ref([{ key: 'Accept', value: 'application/json' }])
const body = ref('')
const response = ref(null)
const loading = ref(false)
const history = ref([])
const MAX_HISTORY = 100
const variables = ref({})
const varName = ref(''), varPath = ref('')
const schemaText = ref(''), schemaResult = ref(null)

const activeHeaderCount = computed(() => headers.value.filter(h => h.key).length)
const formattedBody = computed(() => {
  if (!response.value?.body) return ''
  try { return JSON.stringify(JSON.parse(response.value.body), null, 2) }
  catch { return response.value.body }
})
const statusClass = computed(() => {
  const s = response.value?.status
  if (s >= 200 && s < 300) return 'ok'
  if (s >= 400 && s < 500) return 'client-err'
  if (s >= 500) return 'server-err'
  return ''
})
const checks = computed(() => {
  if (!response.value) return {}
  return {
    status: response.value.status >= 200 && response.value.status < 300,
    json: (() => { try { JSON.parse(response.value.body); return true } catch { return false } })(),
    time: response.value.time < 1000,
  }
})

const scenarios = [
  { label: '正确 GET 请求', method: 'GET', url: 'https://httpbin.org/get', headers: [{ key: 'Accept', value: 'application/json' }], body: '' },
  { label: 'POST 创建资源', method: 'POST', url: 'https://httpbin.org/post', headers: [{ key: 'Content-Type', value: 'application/json' }], body: '{"name":"test","role":"qa"}' },
  { label: '404 错误处理', method: 'GET', url: 'https://httpbin.org/status/404', headers: [], body: '' },
  { label: '500 服务器错误', method: 'GET', url: 'https://httpbin.org/status/500', headers: [], body: '' },
  { label: '带延迟的请求', method: 'GET', url: 'https://httpbin.org/delay/2', headers: [], body: '' },
]

function applyScenario(s) {
  method.value = s.method; url.value = s.url; headers.value = s.headers.length ? s.headers.map(h=>({...h})) : []
  body.value = s.body; response.value = null
}

function interpolate(str) { return str.replace(/\{\{(\w+)\}\}/g, (_, k) => variables.value[k] !== undefined ? variables.value[k] : `{{${k}}}`) }

async function sendRequest() {
  loading.value = true; response.value = null
  const hdrs = {}
  headers.value.forEach(h => { if (h.key) hdrs[h.key] = interpolate(h.value) })
  const targetUrl = interpolate(url.value)
  const opts = { method: method.value, headers: hdrs }
  if (method.value !== 'GET' && body.value) opts.body = interpolate(body.value)
  const start = performance.now()
  try {
    const res = await fetch(targetUrl, opts)
    const text = await res.text()
    response.value = { status: res.status, statusText: res.statusText, body: text, time: Math.round(performance.now() - start), url: targetUrl, method: method.value }
    history.value.push({ ...response.value })
    if (history.value.length > MAX_HISTORY) history.value = history.value.slice(-MAX_HISTORY)
  } catch (e) {
    response.value = { status: 0, statusText: e.message, body: '', time: Math.round(performance.now() - start), url: targetUrl, method: method.value }
    history.value.push({ ...response.value })
    if (history.value.length > MAX_HISTORY) history.value = history.value.slice(-MAX_HISTORY)
  }
  loading.value = false
}

function extractVar() {
  if (!response.value?.body || !varName.value || !varPath.value) return
  try {
    const obj = JSON.parse(response.value.body)
    const value = varPath.value.split('.').reduce((o, k) => o?.[k], obj)
    if (value !== undefined) variables.value[varName.value] = typeof value === 'object' ? JSON.stringify(value) : String(value)
  } catch (e) { /* invalid JSON */ }
}

function validateSchema() {
  if (!response.value?.body || !schemaText.value) return
  try {
    const data = JSON.parse(response.value.body)
    const schema = JSON.parse(schemaText.value)
    const errors = []
    if (schema.type && typeof data !== schema.type) errors.push(`根类型应为 ${schema.type}`)
    if (schema.required) {
      for (const key of schema.required) {
        if (!(key in data)) errors.push(`缺少必填字段: ${key}`)
      }
    }
    if (schema.properties) {
      for (const [key, prop] of Object.entries(schema.properties)) {
        if (key in data) {
          const actualType = Array.isArray(data[key]) ? 'array' : typeof data[key]
          if (prop.type && actualType !== prop.type) errors.push(`${key}: 期望 ${prop.type}, 实际 ${actualType}`)
        }
      }
    }
    schemaResult.value = errors.length ? { valid: false, error: errors.join('; ') } : { valid: true }
  } catch (e) { schemaResult.value = { valid: false, error: 'JSON解析错误: ' + e.message } }
}

function replayRequest(h) { url.value = h.url; method.value = h.method; sendRequest() }
</script>

<style scoped>
.lab-page { max-width: 800px; margin: 0 auto; }

.req-bar { display: flex; gap: 8px; margin-bottom: 10px; }
.method-select {
  padding: 8px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-weight: 700; font-size: .82rem;
  background: var(--primary-light); color: var(--primary); cursor: pointer; outline: none;
}
.url-input {
  flex: 1; padding: 8px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .84rem; background: var(--surface); color: var(--text); outline: none;
}
.url-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.panel-details { margin-top: 10px; }
.panel-details summary { font-size: .8rem; cursor: pointer; color: var(--text-secondary); margin-bottom: 8px; }
.header-row { display: flex; gap: 6px; margin-bottom: 4px; }
.h-key, .h-val { flex: 1; padding: 6px 10px; border: 1px solid var(--border); border-radius: 4px; font-family: var(--font-mono); font-size: .76rem; background: var(--surface); color: var(--text); outline: none; }
.h-remove { padding: 4px 8px; border: none; background: none; cursor: pointer; color: var(--text-muted); font-size: 1rem; }
.h-remove:hover { color: var(--danger); }
.add-header { padding: 4px 10px; border: 1px dashed var(--border); border-radius: 4px; background: none; cursor: pointer; font-size: .74rem; color: var(--text-secondary); margin-top: 4px; }
.body-input { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-family: var(--font-mono); font-size: .82rem; background: var(--surface); color: var(--text); outline: none; resize: vertical; }

.resp-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; background: var(--bg); border-bottom: 1px solid var(--border); }
.resp-status { font-weight: 700; font-size: .84rem; font-family: var(--font-mono); }
.resp-status.ok { color: var(--success); } .resp-status.client-err { color: var(--warning); } .resp-status.server-err { color: var(--danger); }
.resp-time { color: var(--text-muted); font-size: .76rem; }
.resp-body { padding: 16px 20px; }
.resp-body pre { color: var(--text); font-family: var(--font-mono); font-size: .78rem; line-height: 1.6; white-space: pre-wrap; word-break: break-all; margin: 0; }

.assert-checks { display: flex; gap: 10px; flex-wrap: wrap; }
.assert-item { padding: 6px 14px; border-radius: var(--radius-sm); font-size: .8rem; font-weight: 500; }
.assert-item.pass { background: var(--success-light); color: #065f46; }
.assert-item.fail { background: var(--danger-light); color: #991b1b; }

.scenario-list { display: flex; flex-wrap: wrap; gap: 8px; }
.scenario-item {
  padding: 10px 16px; border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--surface); cursor: pointer; text-align: left;
  transition: all var(--fast); font-family: var(--font-sans);
}
.scenario-item:hover { border-color: var(--primary); box-shadow: var(--shadow-xs); }
.scenario-item strong { display: block; font-size: .84rem; margin-bottom: 2px; }
.scenario-item span { font-size: .72rem; color: var(--text-muted); font-family: var(--font-mono); }

.var-row { display: flex; gap: 8px; align-items: flex-end; }
.var-chips { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; margin-top: 8px; }
.var-chip { padding: 3px 10px; background: var(--primary-light); color: var(--primary); border-radius: 4px; font-size: .72rem; font-family: var(--font-mono); font-weight: 600; }
.var-clear { padding: 3px 8px; border: 1px solid var(--border); border-radius: 4px; background: none; cursor: pointer; font-size: .68rem; color: var(--text-muted); }

.schema-result { margin-top: 6px; padding: 8px 12px; border-radius: 6px; font-size: .78rem; font-family: var(--font-mono); }
.schema-result.pass { background: var(--success-light); color: #065f46; }
.schema-result.fail { background: var(--danger-light); color: #991b1b; }

.hist-item { display: flex; gap: 10px; align-items: center; padding: 6px 10px; cursor: pointer; border-radius: 4px; font-size: .74rem; transition: all var(--fast); }
.hist-item:hover { background: var(--surface-hover); }
.hist-method { font-weight: 700; font-size: .68rem; padding: 1px 5px; border-radius: 3px; min-width: 42px; text-align: center; }
.hist-method.m-GET { background: #dbeafe; color: #1d4ed8; } .hist-method.m-POST { background: #d1fae5; color: #047857; } .hist-method.m-PUT { background: #fef3c7; color: #b45309; } .hist-method.m-DELETE { background: #fee2e2; color: #b91c1c; } .hist-method.m-PATCH { background: #ede9fe; color: #6d28d9; }
.hist-url { flex: 1; font-family: var(--font-mono); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-secondary); }
.hist-status.ok { color: var(--success); } .hist-status.err { color: var(--danger); }
.hist-time { color: var(--text-muted); font-family: var(--font-mono); font-size: .7rem; }
</style>
