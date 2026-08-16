<template>
  <div>
    <div class="page-header"><h1>管理面板</h1><p>用户管理与平台数据</p></div>

    <div v-if="auth.user && !auth.user.is_admin" class="card" style="text-align:center;padding:48px;color:var(--text-muted);">
      🔒 需要管理员权限
    </div>
    <template v-else>
      <div v-if="adminError" class="err-banner" @click="adminError=''">{{ adminError }} <span class="err-dismiss">✕</span></div>
      <!-- Admin Tabs -->
      <div class="admin-tabs">
        <button :class="{ active: adminTab==='overview' }" @click="adminTab='overview'">概览</button>
        <button :class="{ active: adminTab==='levels' }" @click="adminTab='levels'">关卡管理</button>
      </div>

      <!-- ====== Overview Tab ====== -->
      <template v-if="adminTab==='overview'">
        <div class="stats-row">
          <div class="stat-card"><span class="stat-icon">👥</span><div><span class="stat-num">{{ stats.users?.total || 0 }}</span><span class="stat-label">总用户</span></div></div>
          <div class="stat-card"><span class="stat-icon">🎯</span><div><span class="stat-num">{{ stats.levels?.completions || 0 }}</span><span class="stat-label">总通关数</span></div></div>
          <div class="stat-card"><span class="stat-icon">📊</span><div><span class="stat-num">{{ stats.users?.active || 0 }}</span><span class="stat-label">活跃用户</span></div></div>
        </div>

        <div class="card" style="margin-top:var(--space-lg);">
          <h3 style="margin-bottom:var(--space-md);">用户列表</h3>
          <div class="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>用户名</th><th>邮箱</th><th>角色</th><th>已通关</th><th>注册时间</th></tr></thead>
              <tbody>
                <tr v-for="u in users" :key="u.id">
                  <td>{{ u.id }}</td>
                  <td><strong>{{ u.username }}</strong></td>
                  <td>{{ u.email }}</td>
                  <td><span :class="['tag', u.is_admin ? 'tag-warning' : 'tag-primary']">{{ u.is_admin ? '管理员' : '用户' }}</span></td>
                  <td>{{ u.levels_completed }}</td>
                  <td>{{ fmtDate(u.created_at) }}</td>
                </tr>
                <tr v-if="users.length === 0"><td colspan="6" style="text-align:center;color:var(--text-muted);">加载中...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- ====== Levels Tab ====== -->
      <template v-if="adminTab==='levels'">
        <!-- Filters + Add -->
        <div class="levels-toolbar">
          <input v-model="levelSearch" type="text" placeholder="🔍 搜索关卡标题..." class="input" style="flex:1;max-width:280px;" />
          <select v-model="levelFilterStage" class="input" style="width:120px;">
            <option value="">全部阶段</option>
            <option value="beginner">入门</option>
            <option value="intermediate">进阶</option>
            <option value="advanced">高级</option>
            <option value="expert">专家</option>
          </select>
          <select v-model="levelFilterType" class="input" style="width:120px;">
            <option value="">全部类型</option>
            <option value="quiz">测验</option>
            <option value="code">代码</option>
            <option value="explore">探索</option>
            <option value="debug">调试</option>
            <option value="scenario">情景</option>
            <option value="analyze">分析</option>
          </select>
          <button class="btn btn-primary" @click="openCreateModal">＋ 新增关卡</button>
        </div>

        <!-- Levels Table -->
        <div class="card" style="margin-top:var(--space-md);">
          <div class="table-wrap" style="max-height:520px;overflow-y:auto;">
            <table>
              <thead><tr><th>Order</th><th>标题</th><th>阶段</th><th>类型</th><th>分值</th><th style="width:130px;">操作</th></tr></thead>
              <tbody>
                <tr v-for="lv in filteredLevels" :key="lv.id">
                  <td>{{ lv.order }}</td>
                  <td><strong>{{ lv.title }}</strong></td>
                  <td><span :class="['tag', 'tag-' + stageTag(lv.stage)]">{{ stageLabel(lv.stage) }}</span></td>
                  <td><span class="tag tag-primary">{{ lv.task_type }}</span></td>
                  <td>{{ lv.points }}</td>
                  <td>
                    <button class="btn btn-sm btn-outline" @click="openEditModal(lv)" style="margin-right:6px;">✏️</button>
                    <button class="btn btn-sm btn-outline" @click="confirmDelete(lv)">🗑️</button>
                  </td>
                </tr>
                <tr v-if="filteredLevels.length === 0"><td colspan="6" style="text-align:center;color:var(--text-muted);padding:24px;">{{ levels.length === 0 ? '加载中...' : '无匹配关卡' }}</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Edit / Create Modal -->
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal-card">
            <h3>{{ modalMode === 'edit' ? '✏️ 编辑关卡' : '＋ 新增关卡' }}</h3>
            <div class="modal-body">
              <div class="form-row">
                <label>标题 <span class="req">*</span></label>
                <input v-model="form.title" class="input" />
              </div>
              <div class="form-row form-row-3">
                <label>阶段</label>
                <select v-model="form.stage" class="input">
                  <option v-for="s in stageKeys" :key="s" :value="s">{{ stageLabels[s] || s }}</option>
                </select>
                <label>任务类型</label>
                <select v-model="form.task_type" class="input">
                  <option value="quiz">测验</option>
                  <option value="code">代码</option>
                  <option value="explore">探索</option>
                  <option value="debug">调试</option>
                  <option value="scenario">情景</option>
                  <option value="analyze">分析</option>
                </select>
                <label>分值</label>
                <input v-model.number="form.points" type="number" class="input" style="width:90px;" />
              </div>
              <div class="form-row">
                <label>Order</label>
                <input v-model.number="form.order" type="number" class="input" style="width:120px;" />
              </div>
              <div class="form-row">
                <label>描述</label>
                <textarea v-model="form.description" class="input" rows="2"></textarea>
              </div>
              <div class="form-row">
                <label>理论 (theory)</label>
                <textarea v-model="form.theory" class="input" rows="3"></textarea>
              </div>
              <div class="form-row">
                <label>演示 (demo)</label>
                <textarea v-model="form.demo" class="input" rows="2"></textarea>
              </div>
              <div class="form-row">
                <label>任务配置 (task_config JSON)</label>
                <textarea v-model="form.task_config_str" class="input" rows="4" placeholder='{"question": "...", "answer": "..."}'></textarea>
                <div v-if="configError" class="form-err">{{ configError }}</div>
              </div>
            </div>
            <div class="modal-actions">
              <button class="btn btn-outline" @click="closeModal">取消</button>
              <button class="btn btn-primary" @click="saveLevel" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
            </div>
          </div>
        </div>

        <!-- Delete Confirm Modal -->
        <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm=false">
          <div class="modal-card" style="max-width:400px;">
            <h3>确认删除</h3>
            <p style="margin:16px 0;">确定要删除关卡 <strong>{{ deleteTarget?.title }}</strong> 吗？此操作不可撤销。</p>
            <div class="modal-actions">
              <button class="btn btn-outline" @click="showDeleteConfirm=false">取消</button>
              <button class="btn btn-danger" @click="doDelete" :disabled="saving">{{ saving ? '删除中...' : '确认删除' }}</button>
            </div>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { LS_TOKEN } from '../constants'

const auth = useAuthStore()
const adminTab = ref('overview')
const stats = ref({}), users = ref([]), adminError = ref('')
const token = () => localStorage.getItem(LS_TOKEN) || ''

async function adminApi(method, path, body) {
  const headers = { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` }
  const opts = { method, headers }
  if (body) opts.body = JSON.stringify(body)
  const r = await fetch(path, opts)
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err.detail || `请求失败 (${r.status})`)
  }
  return r.json()
}

function fmtDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('zh-CN')
}

// ── Level Management ──
const levels = ref([])
const levelSearch = ref('')
const levelFilterStage = ref('')
const levelFilterType = ref('')
const showModal = ref(false)
const modalMode = ref('edit')
const saving = ref(false)
const configError = ref('')
const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)

const emptyForm = () => ({
  id: null,
  title: '',
  stage: 'beginner',
  task_type: 'quiz',
  points: 10,
  order: null,
  description: '',
  theory: '',
  demo: '',
  task_config_str: '{}',
})
const form = ref(emptyForm())

const stageLabels = { beginner: '入门', intermediate: '进阶', advanced: '高级', expert: '专家' }
const stageKeys = computed(() => {
  const keys = new Set(levels.value.map(l => l.stage))
  return [...keys].sort()
})
const STAGE_TAGS = ['primary', 'success', 'warning', 'danger', 'info', 'neutral', 'accent']
function stageLabel(s) { return stageLabels[s] || s }
function stageTag(s) {
  const idx = stageKeys.value.indexOf(s)
  return STAGE_TAGS[idx % STAGE_TAGS.length] || 'primary'
}

const filteredLevels = computed(() => {
  let list = levels.value
  if (levelSearch.value) {
    const q = levelSearch.value.toLowerCase()
    list = list.filter(lv => lv.title.toLowerCase().includes(q))
  }
  if (levelFilterStage.value) {
    list = list.filter(lv => lv.stage === levelFilterStage.value)
  }
  if (levelFilterType.value) {
    list = list.filter(lv => lv.task_type === levelFilterType.value)
  }
  return list
})

async function fetchLevels() {
  try {
    const data = await adminApi('GET', '/api/admin/levels')
    levels.value = data.levels || []
  } catch (e) { adminError.value = e.message || '加载关卡列表失败' }
}

function openCreateModal() {
  modalMode.value = 'create'
  form.value = emptyForm()
  configError.value = ''
  showModal.value = true
}

function openEditModal(lv) {
  modalMode.value = 'edit'
  form.value = {
    id: lv.id,
    title: lv.title || '',
    stage: lv.stage || 'beginner',
    task_type: lv.task_type || 'quiz',
    points: lv.points || 10,
    order: lv.order,
    description: lv.description || '',
    theory: lv.theory || '',
    demo: lv.demo || '',
    task_config_str: typeof lv.task_config === 'string' ? lv.task_config : JSON.stringify(lv.task_config || {}, null, 2),
  }
  configError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function saveLevel() {
  // Validate JSON
  let tc
  try {
    tc = JSON.parse(form.value.task_config_str)
  } catch (e) {
    configError.value = 'JSON 格式无效: ' + e.message
    return
  }
  configError.value = ''
  saving.value = true

  const body = {
    title: form.value.title,
    stage: form.value.stage,
    task_type: form.value.task_type,
    points: form.value.points,
    order: form.value.order,
    description: form.value.description,
    theory: form.value.theory,
    demo: form.value.demo || null,
    task_config: tc,
  }

  try {
    if (modalMode.value === 'create') {
      await adminApi('POST', '/api/admin/levels', body)
    } else {
      await adminApi('PUT', `/api/admin/levels/${form.value.id}`, body)
    }
    await fetchLevels()
    closeModal()
  } catch (e) {
    adminError.value = '保存失败: ' + e.message
  } finally {
    saving.value = false
  }
}

function confirmDelete(lv) {
  deleteTarget.value = lv
  showDeleteConfirm.value = true
}

async function doDelete() {
  if (!deleteTarget.value) return
  saving.value = true
  try {
    await adminApi('DELETE', `/api/admin/levels/${deleteTarget.value.id}`)
    await fetchLevels()
    showDeleteConfirm.value = false
    deleteTarget.value = null
  } catch (e) {
    adminError.value = '删除失败: ' + e.message
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [s, u] = await Promise.all([
      adminApi('GET', '/api/admin/stats'),
      adminApi('GET', '/api/admin/users'),
    ])
    stats.value = s
    users.value = u
  } catch (e) { adminError.value = e.message || '加载管理数据失败' }
  fetchLevels()
})
</script>

<style scoped>
/* ── Error Banner ── */
.err-banner {
  background: rgba(var(--danger-rgb, 239,68,68), 0.1); border: 1px solid var(--danger, #ef4444);
  color: var(--danger, #ef4444); padding: 10px 16px; border-radius: var(--radius-md);
  margin-bottom: var(--space-md); font-size: .84rem; cursor: pointer;
  display: flex; justify-content: space-between; align-items: center;
}
.err-dismiss { font-weight: 700; opacity: 0.6; }
.err-dismiss:hover { opacity: 1; }

/* ── Tabs ── */
.admin-tabs {
  display: flex; gap: 8px; margin-bottom: var(--space-lg);
  border-bottom: 2px solid var(--border); padding-bottom: 0;
}
.admin-tabs button {
  padding: 8px 20px; border: none; background: transparent;
  font-size: .9rem; font-weight: 600; color: var(--text-muted);
  cursor: pointer; border-radius: var(--radius-md) var(--radius-md) 0 0;
  transition: all .15s;
}
.admin-tabs button:hover { color: var(--text-primary); background: var(--surface-hover); }
.admin-tabs button.active {
  color: var(--primary); background: var(--surface);
  border: 2px solid var(--border); border-bottom-color: var(--surface);
  margin-bottom: -2px;
}

/* ── Stats ── */
.stats-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 18px 20px; display: flex; align-items: center; gap: 14px; box-shadow: var(--shadow-xs); }
.stat-icon { font-size: 1.6rem; }
.stat-num { display: block; font-size: 1.5rem; font-weight: 800; color: var(--primary); line-height: 1.1; }
.stat-label { font-size: .75rem; color: var(--text-muted); font-weight: 500; }

/* ── Tables ── */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: .82rem; }
th { text-align: left; padding: 10px 12px; border-bottom: 2px solid var(--border); font-weight: 650; color: var(--text-secondary); font-size: .76rem; text-transform: uppercase; letter-spacing: .5px; position: sticky; top: 0; background: var(--surface); z-index: 1; }
td { padding: 10px 12px; border-bottom: 1px solid var(--border-light); }
tr:hover td { background: var(--surface-hover); }

/* ── Levels Toolbar ── */
.levels-toolbar {
  display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
}

/* ── Forms ── */
.input {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 8px 12px; font-size: .85rem;
  color: var(--text-primary); outline: none; width: 100%; box-sizing: border-box;
  font-family: inherit;
}
.input:focus { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(var(--primary-rgb, 99,102,241), 0.15); }
.form-row { margin-bottom: 14px; }
.form-row label { display: block; font-size: .8rem; font-weight: 600; margin-bottom: 4px; color: var(--text-secondary); }
.form-row .req { color: var(--danger, #ef4444); }
.form-row-3 { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 8px; align-items: end; }
.form-err { color: var(--danger, #ef4444); font-size: .78rem; margin-top: 4px; }

/* ── Tags ── */
.tag {
  display: inline-block; padding: 2px 8px; border-radius: var(--radius-sm, 4px);
  font-size: .72rem; font-weight: 600;
}

/* ── Buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 8px 16px; border: 1px solid transparent; border-radius: var(--radius-md);
  font-size: .84rem; font-weight: 600; cursor: pointer; transition: all .15s;
  font-family: inherit;
}
.btn-primary { background: var(--primary); color: #fff; border-color: var(--primary); }
.btn-primary:hover { filter: brightness(1.1); }
.btn-primary:disabled { opacity: .6; cursor: not-allowed; }
.btn-outline { background: transparent; color: var(--text-primary); border-color: var(--border); }
.btn-outline:hover { background: var(--surface-hover); }
.btn-danger { background: var(--danger, #ef4444); color: #fff; border-color: var(--danger, #ef4444); }
.btn-danger:hover { filter: brightness(1.1); }
.btn-danger:disabled { opacity: .6; cursor: not-allowed; }
.btn-sm { padding: 3px 8px; font-size: .78rem; }

/* ── Modal ── */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal-card {
  background: var(--surface); border-radius: var(--radius-lg); padding: 24px 28px;
  max-width: 640px; width: 95%; max-height: 85vh; overflow-y: auto;
  box-shadow: var(--shadow-lg, 0 10px 40px rgba(0,0,0,0.2));
}
.modal-card h3 { margin: 0 0 16px; font-size: 1.1rem; }
.modal-body { margin-bottom: 20px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }

/* ── Misc ── */
.tag-primary { background: rgba(var(--primary-rgb, 99,102,241), 0.12); color: var(--primary); }
.tag-warning { background: rgba(var(--warning-rgb, 245,158,11), 0.12); color: var(--warning, #f59e0b); }
.tag-success { background: rgba(var(--success-rgb, 16,185,129), 0.12); color: var(--success, #10b981); }
.tag-danger { background: rgba(var(--danger-rgb, 239,68,68), 0.12); color: var(--danger, #ef4444); }
</style>
