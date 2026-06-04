<template>
  <div>
    <div class="page-header"><h1>📋 测试用例管理</h1><p>创建、组织和管理你的测试用例库</p></div>

    <div class="tc-layout">
      <!-- Sidebar folders -->
      <aside class="tc-sidebar">
        <h4>📁 文件夹</h4>
        <ul>
          <li v-for="f in folders" :key="f.name" :class="{ active: filterFolder === f.name }" @click="filterFolder = filterFolder === f.name ? '' : f.name">
            {{ f.name }} <span class="fc">{{ f.count }}</span>
          </li>
          <li :class="{ active: !filterFolder }" @click="filterFolder = ''">📋 全部 <span class="fc">{{ totalCount }}</span></li>
        </ul>
        <button class="btn-outline" style="width:100%;margin-top:12px;font-size:.78rem;" @click="showCreate=true">+ 新建用例</button>
      </aside>

      <!-- Main -->
      <main class="tc-main">
        <div class="controls">
          <div class="search-box"><span>🔍</span><input v-model="search" placeholder="搜索标题/步骤/标签..." class="search-input"></div>
          <select v-model="filterPriority" class="filter-select"><option value="">全部优先级</option><option>P0</option><option>P1</option><option>P2</option><option>P3</option></select>
          <select v-model="filterStatus" class="filter-select"><option value="">全部状态</option><option>draft</option><option>ready</option><option>running</option><option>passed</option><option>failed</option></select>
          <button class="btn-outline" style="font-size:.74rem;padding:6px 12px;" @click="exportCSV">📥 CSV</button>
        </div>

        <div v-if="selectedIds.length" class="bulk-bar">
          <span>{{ selectedIds.length }} 项已选</span>
          <button class="btn-outline" style="font-size:.72rem;" @click="bulkSetStatus('passed')">✅ 批量通过</button>
          <button class="btn-outline" style="font-size:.72rem;" @click="bulkSetStatus('failed')">❌ 批量失败</button>
        </div>

        <div v-if="cases.length === 0" class="card" style="text-align:center;padding:48px;color:var(--text-muted);">📭 暂无测试用例，点击左侧「新建用例」开始</div>

        <div v-for="tc in cases" :key="tc.id" class="tc-card">
          <div class="tc-header">
            <input type="checkbox" :checked="selectedIds.includes(tc.id)" @click.stop @change="toggleSelect(tc.id)" class="tc-check">
            <strong class="tc-title" @click="editCase(tc)">{{ tc.title }}</strong>
            <div class="tc-meta">
              <span class="badge" :class="'pri-'+tc.priority.toLowerCase()">{{ tc.priority }}</span>
              <span class="badge" :class="'st-'+tc.status">{{ statusLabel(tc.status) }}</span>
              <span class="tc-folder">📁 {{ tc.folder }}</span>
            </div>
          </div>
          <div v-if="tc.steps" class="tc-steps" @click="editCase(tc)">{{ tc.steps.slice(0, 120) }}{{ tc.steps.length > 120 ? '...' : '' }}</div>
          <div class="tc-footer">
            <span class="tc-tags" @click="editCase(tc)">{{ tc.tags }}</span>
            <div class="tc-actions">
              <button class="btn-run" :class="'r-'+tc.status" @click.stop="quickRun(tc, 'passed')" title="标记通过">✅</button>
              <button class="btn-run" :class="'r-failed'" @click.stop="quickRun(tc, 'failed')" title="标记失败">❌</button>
              <button class="btn-run" @click.stop="quickRun(tc, 'skipped')" title="跳过">⏭️</button>
              <button class="btn-ghost" style="font-size:.7rem;padding:2px 8px;" @click.stop="deleteCase(tc.id)">🗑️</button>
            </div>
          </div>
          <div v-if="tc.runs && tc.runs.length" class="tc-runs">
            <span class="run-label">最近执行：</span>
            <span v-for="r in tc.runs.slice(0,3)" :key="r.id" class="run-badge" :class="'run-'+r.status">{{ runIcon(r.status) }} {{ fmtRel(r.created_at) }}</span>
          </div>
        </div>
      </main>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreate || editing" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editing ? '编辑用例' : '新建测试用例' }}</h3>
        <div class="field"><label>标题 *</label><input v-model="form.title" class="form-input" placeholder="例：登录页 - 正确用户名+错误密码"></div>
        <div class="field"><label>复现步骤</label><textarea v-model="form.steps" class="form-input" rows="3" placeholder="1. 打开登录页&#10;2. 输入..."></textarea></div>
        <div class="field"><label>预期结果</label><input v-model="form.expected" class="form-input" placeholder="应显示错误提示"></div>
        <div class="field-row">
          <div class="field" style="flex:1;"><label>优先级</label><select v-model="form.priority" class="form-input"><option>P0</option><option>P1</option><option>P2</option><option>P3</option></select></div>
          <div class="field" style="flex:1;"><label>状态</label><select v-model="form.status" class="form-input"><option value="draft">草稿</option><option value="ready">就绪</option><option value="running">执行中</option><option value="passed">通过</option><option value="failed">失败</option></select></div>
        </div>
        <div class="field-row">
          <div class="field" style="flex:1;"><label>标签</label><input v-model="form.tags" class="form-input" placeholder="登录, 冒烟测试, P0"></div>
          <div class="field" style="flex:1;"><label>文件夹</label><input v-model="form.folder" class="form-input" placeholder="默认"></div>
        </div>
        <div class="modal-actions">
          <button class="btn-outline" @click="closeModal">取消</button>
          <button class="btn-primary" @click="saveCase" :disabled="!form.title">{{ editing ? '更新' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'

const cases = ref([]), folders = ref([]), totalCount = ref(0)
const search = ref(''), filterFolder = ref(''), filterPriority = ref(''), filterStatus = ref('')
const showCreate = ref(false), editing = ref(null), selectedIds = ref([])
const form = reactive({ title: '', steps: '', expected: '', priority: 'P2', status: 'draft', tags: '', folder: '默认' })
const token = () => localStorage.getItem('qa-pro-token') || ''

function statusLabel(s) {
  return { draft: '草稿', ready: '就绪', running: '执行中', passed: '通过', failed: '失败', skipped: '跳过', blocked: '阻塞' }[s] || s
}
function runIcon(s) { return { passed: '✅', failed: '❌', skipped: '⏭️', blocked: '🚫' }[s] || '' }
function fmtRel(iso) {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins}分前`
  if (mins < 1440) return `${Math.floor(mins/60)}时前`
  return `${Math.floor(mins/1440)}天前`
}

async function fetchCases() {
  const params = new URLSearchParams({ search: search.value, folder: filterFolder.value, priority: filterPriority.value, status: filterStatus.value })
  const r = await fetch('/api/testcases?' + params, { headers: { Authorization: `Bearer ${token()}` } })
  if (r.ok) {
    const d = await r.json()
    cases.value = d.cases
    folders.value = d.folders
    totalCount.value = d.cases.length
  }
}

let _searchDebounce = null
watch([search, filterFolder, filterPriority, filterStatus], () => {
  clearTimeout(_searchDebounce)
  _searchDebounce = setTimeout(() => fetchCases(), 300)
})

function editCase(tc) {
  editing.value = tc.id
  form.title = tc.title; form.steps = tc.steps; form.expected = tc.expected_result
  form.priority = tc.priority; form.status = tc.status; form.tags = tc.tags; form.folder = tc.folder
  showCreate.value = true
}

function closeModal() { showCreate.value = false; editing.value = null; Object.assign(form, { title: '', steps: '', expected: '', priority: 'P2', status: 'draft', tags: '', folder: '默认' }) }

async function saveCase() {
  const body = { title: form.title, steps: form.steps, expected_result: form.expected, priority: form.priority, status: form.status, tags: form.tags, folder: form.folder }
  const url = editing.value ? `/api/testcases/${editing.value}` : '/api/testcases'
  const method = editing.value ? 'PUT' : 'POST'
  const r = await fetch(url, { method, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` }, body: JSON.stringify(body) })
  if (r.ok) { closeModal(); fetchCases() }
}

async function deleteCase(id) {
  if (!confirm('确认删除？')) return
  await fetch(`/api/testcases/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token()}` } })
  fetchCases()
}

function toggleSelect(id) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

async function bulkSetStatus(status) {
  await fetch('/api/testcases/bulk', {
    method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` },
    body: JSON.stringify({ ids: selectedIds.value, status })
  })
  selectedIds.value = []
  fetchCases()
}

async function exportCSV() {
  const r = await fetch('/api/testcases/export/csv', { headers: { Authorization: `Bearer ${token()}` } })
  if (!r.ok) return
  const blob = await r.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'testcases.csv'; a.click()
  URL.revokeObjectURL(url)
}

async function quickRun(tc, status) {
  await fetch(`/api/testcases/${tc.id}/runs`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` },
    body: JSON.stringify({ status, notes: '' })
  })
  fetchCases()
}

onMounted(() => fetchCases())
</script>

<style scoped>
.tc-layout { display: flex; gap: var(--space-lg); align-items: flex-start; }
.tc-sidebar { width: 180px; flex-shrink: 0; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; position: sticky; top: 72px; }
.tc-sidebar h4 { font-size: .78rem; text-transform: uppercase; letter-spacing: .5px; color: var(--text-muted); margin-bottom: 10px; }
.tc-sidebar ul { list-style: none; }
.tc-sidebar li { padding: 5px 8px; border-radius: 4px; cursor: pointer; font-size: .8rem; display: flex; justify-content: space-between; transition: all var(--fast); }
.tc-sidebar li:hover { background: var(--surface-hover); }
.tc-sidebar li.active { background: var(--primary-light); color: var(--primary); font-weight: 600; }
.fc { font-size: .7rem; color: var(--text-muted); background: var(--border-light); padding: 1px 6px; border-radius: 10px; }
.tc-main { flex: 1; min-width: 0; }

.controls { display: flex; gap: 8px; margin-bottom: var(--space-md); }
.search-box { flex: 1; display: flex; align-items: center; gap: 8px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 0 12px; }
.search-box:focus-within { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.search-input { flex: 1; border: none; outline: none; padding: 9px 0; font-size: .84rem; background: transparent; color: var(--text); font-family: var(--font-sans); }
.filter-select { padding: 8px 12px; border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); color: var(--text); font-size: .8rem; cursor: pointer; outline: none; font-family: var(--font-sans); }

.tc-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 18px; margin-bottom: 8px; cursor: pointer; transition: all var(--fast); }
.tc-card:hover { border-color: var(--primary); box-shadow: var(--shadow-xs); }
.tc-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 6px; }
.tc-title { font-size: .88rem; font-weight: 650; }
.tc-meta { display: flex; gap: 6px; align-items: center; flex-shrink: 0; }
.badge { padding: 2px 8px; border-radius: 4px; font-size: .66rem; font-weight: 700; }
.badge.pri-p0 { background: #fef2f2; color: #dc2626; } .badge.pri-p1 { background: #fffbeb; color: #d97706; } .badge.pri-p2 { background: #eff6ff; color: #2563eb; } .badge.pri-p3 { background: #f3f4f6; color: #6b7280; }
.badge.st-passed { background: #ecfdf5; color: #059669; } .badge.st-failed { background: #fef2f2; color: #dc2626; } .badge.st-running { background: #eff6ff; color: #2563eb; } .badge.st-ready { background: #f5f3ff; color: #7c3aed; } .badge.st-draft { background: #f3f4f6; color: #6b7280; }
.tc-folder { font-size: .7rem; color: var(--text-muted); }
.tc-steps { font-size: .78rem; color: var(--text-secondary); line-height: 1.5; }
.tc-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
.tc-tags { font-size: .7rem; color: var(--text-muted); }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal { background: var(--surface); border-radius: var(--radius-lg); padding: 28px; max-width: 560px; width: 100%; box-shadow: var(--shadow-lg); max-height: 90vh; overflow-y: auto; }
.modal h3 { font-size: 1.05rem; margin-bottom: 16px; }
.field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; }
.field label { font-size: .76rem; font-weight: 600; color: var(--text-secondary); }
.form-input { padding: 9px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: .84rem; font-family: var(--font-sans); background: var(--surface); color: var(--text); outline: none; width: 100%; resize: vertical; transition: border-color var(--fast); }
.form-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
select.form-input { cursor: pointer; }
.field-row { display: flex; gap: 10px; }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }

.tc-check { width: 16px; height: 16px; cursor: pointer; flex-shrink: 0; accent-color: var(--primary); }

.bulk-bar { display: flex; align-items: center; gap: 10px; padding: 8px 16px; background: var(--primary-light); border-radius: var(--radius-sm); margin-bottom: 10px; font-size: .78rem; border: 1px solid var(--primary); }

.tc-actions { display: flex; gap: 2px; align-items: center; }
.btn-run { padding: 3px 8px; border: 1px solid var(--border); border-radius: 4px; background: var(--surface); cursor: pointer; font-size: .85rem; transition: all var(--fast); opacity: .6; }
.btn-run:hover { opacity: 1; border-color: var(--primary); }
.btn-run.r-passed { border-color: var(--success); background: var(--success-light); opacity: 1; }

.tc-runs { margin-top: 6px; padding-top: 6px; border-top: 1px solid var(--border-light); display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.run-label { font-size: .68rem; color: var(--text-muted); }
.run-badge { font-size: .66rem; padding: 1px 6px; border-radius: 3px; }
.run-badge.run-passed { background: var(--success-light); color: #065f46; }
.run-badge.run-failed { background: var(--danger-light); color: #991b1b; }
.run-badge.run-skipped { background: var(--border-light); color: var(--text-muted); }

.hint-box { padding: 12px 16px; background: #fffbeb; border: 1px solid #f59e0b; border-radius: var(--radius); margin-bottom: var(--space-md); font-size: .84rem; color: #92400e; font-weight: 500; }
</style>
