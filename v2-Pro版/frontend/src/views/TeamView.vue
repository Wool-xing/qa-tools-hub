<template>
  <div>
    <!-- ==================== Dashboard Mode ==================== -->
    <template v-if="dashboardTeamId">
      <div class="page-header">
        <a @click="backToList" class="back-link">← 返回团队列表</a>
        <h1>📊 {{ dashboardTeamName }} — 仪表板</h1>
      </div>

      <div v-if="dashboardLoading" class="card" style="text-align:center;padding:48px;color:var(--text-muted);">加载仪表板...</div>

      <template v-else-if="dashboard">
        <div class="stats-row">
          <div class="card stat-card">
            <span class="stat-num">{{ dashboard.member_count }}</span>
            <span class="stat-label">团队成员</span>
          </div>
          <div class="card stat-card">
            <span class="stat-num">{{ dashboard.test_case_count }}</span>
            <span class="stat-label">共享用例</span>
          </div>
        </div>

        <div class="card" style="margin-top:var(--space-lg);">
          <h3 style="margin-bottom:var(--space-md);">👥 成员进度</h3>
          <table class="member-table" v-if="members.length">
            <thead>
              <tr>
                <th>用户名</th>
                <th>角色</th>
                <th>完成数</th>
                <th>加入时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in members" :key="m.user_id">
                <td class="mem-name">{{ m.username }}</td>
                <td><span class="tag" :class="roleBadge(m.role).class">{{ roleBadge(m.role).label }}</span></td>
                <td><span class="completion-count">{{ getMemberCompletion(m.user_id) }}</span></td>
                <td class="mem-date">{{ fmtDate(m.joined_at) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else style="color:var(--text-muted);text-align:center;padding:24px;">暂无成员数据</p>
        </div>
      </template>

      <div v-else class="card" style="text-align:center;padding:48px;color:var(--danger);">加载仪表板失败</div>
    </template>

    <!-- ==================== Tabs Mode ==================== -->
    <template v-else>
      <div class="page-header">
        <h1>👥 团队协作</h1>
        <p>创建团队，与同事共享测试用例和学习进度</p>
      </div>

      <div class="tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'mine' }" @click="activeTab = 'mine'">我的团队</button>
        <button class="tab-btn" :class="{ active: activeTab === 'create' }" @click="activeTab = 'create'">创建团队</button>
        <button class="tab-btn" :class="{ active: activeTab === 'join' }" @click="activeTab = 'join'">加入团队</button>
      </div>

      <!-- Tab: 我的团队 -->
      <div v-if="activeTab === 'mine'">
        <div v-if="loading" class="card" style="text-align:center;padding:48px;color:var(--text-muted);">加载中...</div>

        <div v-else-if="error" class="card" style="text-align:center;padding:48px;">
          <p style="color:var(--danger);margin-bottom:12px;">{{ error }}</p>
          <button class="btn-outline" @click="fetchTeams">重试</button>
        </div>

        <div v-else-if="!hasTeams" class="card empty-state">
          <div class="empty-icon">👥</div>
          <p class="empty-title">你还没有加入任何团队</p>
          <p class="empty-hint">创建自己的团队或通过邀请码加入同事的团队</p>
          <div class="empty-actions">
            <button class="btn-primary" @click="activeTab = 'create'">创建团队</button>
            <button class="btn-outline" @click="activeTab = 'join'">加入团队</button>
          </div>
        </div>

        <div v-else class="team-list">
          <div v-for="t in teamsList" :key="t.id" class="card team-card">
            <div class="team-card-top">
              <div class="team-card-info">
                <h3 class="team-name">{{ t.name }}</h3>
                <div class="team-meta">
                  <span class="tag" :class="roleBadge(t.role).class">{{ roleBadge(t.role).label }}</span>
                  <span class="meta-item">👤 {{ t.member_count }} 人</span>
                </div>
              </div>
              <div class="team-card-code" @click="copyCode(t.invite_code)" title="点击复制邀请码">
                <span class="code-label">邀请码</span>
                <code class="code-val">{{ t.invite_code }}</code>
                <span class="code-copy-hint">📋</span>
              </div>
            </div>
            <div class="team-card-actions">
              <button class="btn-outline" @click="viewDashboard(t.id)">📊 查看仪表板</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: 创建团队 -->
      <div v-if="activeTab === 'create'">
        <div v-if="createdTeam" class="card success-card">
          <div class="success-icon">✅</div>
          <h3>团队创建成功！</h3>
          <p class="success-team-name">{{ createdTeam.name }}</p>
          <div class="invite-code-box">
            <span class="invite-label">邀请码</span>
            <code class="invite-code">{{ createdTeam.invite_code }}</code>
          </div>
          <button class="btn-primary" @click="copyCode(createdTeam.invite_code)">📋 复制邀请码</button>
          <p class="invite-hint">分享邀请码给团队成员即可加入</p>
          <hr style="margin:16px 0;border:none;border-top:1px solid var(--border-light);">
          <button class="btn-outline" @click="createdTeam = null; fetchTeams()">创建另一个团队</button>
        </div>

        <div v-else class="card">
          <h3 style="margin-bottom:var(--space-md);">创建新团队</h3>
          <form @submit.prevent="handleCreate">
            <div class="field">
              <label>团队名称</label>
              <input v-model="createName" type="text" placeholder="例如：质量保障组" maxlength="50" autocomplete="off">
              <span class="field-hint">{{ createName.length }}/50 字符（2-50个字符）</span>
            </div>
            <p v-if="createError" class="form-error">{{ createError }}</p>
            <button type="submit" class="btn-primary" :disabled="creating || createName.length < 2 || createName.length > 50">
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Tab: 加入团队 -->
      <div v-if="activeTab === 'join'">
        <div class="card">
          <h3 style="margin-bottom:var(--space-md);">加入团队</h3>
          <form @submit.prevent="handleJoin">
            <div class="field">
              <label>邀请码</label>
              <input v-model="inviteCode" type="text" placeholder="例如：ABC12345" maxlength="8" autocomplete="off" style="text-transform:uppercase;letter-spacing:2px;font-family:var(--font-mono);" @input="inviteCode = inviteCode.toUpperCase().replace(/[^A-Z0-9]/g,'')">
              <span class="field-hint">输入团队创建者分享的8位邀请码</span>
            </div>
            <p v-if="joinError" class="form-error">{{ joinError }}</p>
            <button type="submit" class="btn-primary" :disabled="joining || inviteCode.length !== 8">
              {{ joining ? '加入中...' : '加入' }}
            </button>
          </form>
        </div>
      </div>
    </template>

    <!-- ==================== Toast ==================== -->
    <Transition name="toast-fade">
      <div v-if="toast.show" class="toast-popup">{{ toast.message }}</div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { teams } from '../api'

// --- Tabs & navigation ---
const activeTab = ref('mine')
const dashboardTeamId = ref(null)

// --- My teams ---
const teamsList = ref([])
const loading = ref(false)
const error = ref('')

const hasTeams = computed(() => teamsList.value.length > 0)
const dashboardTeamName = computed(() => {
  const t = teamsList.value.find(t => t.id === dashboardTeamId.value)
  return t ? t.name : ''
})

// --- Create form ---
const createName = ref('')
const creating = ref(false)
const createError = ref('')
const createdTeam = ref(null)

// --- Join form ---
const inviteCode = ref('')
const joining = ref(false)
const joinError = ref('')

// --- Dashboard ---
const dashboard = ref(null)
const members = ref([])
const dashboardLoading = ref(false)

// --- Toast ---
const toast = reactive({ show: false, message: '' })
let toastTimer = null
function showToast(msg) {
  toast.message = msg
  toast.show = true
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.show = false }, 2000)
}
// --- API calls ---
async function fetchTeams() {
  loading.value = true
  error.value = ''
  try {
    const data = await teams.mine()
    teamsList.value = data.teams || []
  } catch (e) {
    error.value = e.message || '加载团队列表失败'
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (createName.value.length < 2 || createName.value.length > 50) {
    createError.value = '团队名称需2-50个字符'
    return
  }
  creating.value = true
  createError.value = ''
  try {
    const data = await teams.create(createName.value.trim())
    createdTeam.value = data
    createName.value = ''
  } catch (e) {
    createError.value = e.message || '创建失败'
  } finally {
    creating.value = false
  }
}

async function handleJoin() {
  const code = inviteCode.value.trim().toUpperCase()
  if (code.length !== 8) {
    joinError.value = '邀请码需为8位字符'
    return
  }
  joining.value = true
  joinError.value = ''
  try {
    await teams.join(code)
    inviteCode.value = ''
    showToast('成功加入团队！')
    activeTab.value = 'mine'
    await fetchTeams()
  } catch (e) {
    const msg = e.message || '加入失败'
    if (msg.includes('already') || msg.includes('已是') || msg.includes('已在') || msg.includes('exist') || msg.includes('duplicate')) {
      joinError.value = '你已经是该团队成员'
    } else if (msg.includes('invalid') || msg.includes('not found') || msg.includes('无效') || msg.includes('不存在') || msg.includes('404')) {
      joinError.value = '无效的邀请码'
    } else {
      joinError.value = msg
    }
  } finally {
    joining.value = false
  }
}

async function viewDashboard(teamId) {
  dashboardTeamId.value = teamId
  dashboardLoading.value = true
  dashboard.value = null
  members.value = []
  try {
    const [dashData, memberData] = await Promise.all([
      teams.dashboard(teamId),
      teams.members(teamId)
    ])
    dashboard.value = dashData
    members.value = memberData.members || []
  } catch (e) {
    showToast(e.message || '加载仪表板失败')
  } finally {
    dashboardLoading.value = false
  }
}

function backToList() {
  dashboardTeamId.value = null
  dashboard.value = null
  members.value = []
  fetchTeams()
}

// --- Helpers ---
async function copyCode(code) {
  try {
    await navigator.clipboard.writeText(code)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = code
    ta.style.position = 'fixed'; ta.style.left = '-9999px'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
  showToast('已复制邀请码')
}

function getMemberCompletion(userId) {
  const progress = dashboard.value?.member_progress
  if (!progress) return 0
  const entry = progress[userId]
  if (entry === undefined || entry === null) return 0
  if (typeof entry === 'number') return entry
  if (typeof entry === 'object') return entry.completed ?? entry.count ?? entry.passed ?? 0
  return 0
}

function roleBadge(role) {
  if (role === 'owner') return { class: 'tag-primary', label: '创建者' }
  if (role === 'admin') return { class: 'tag-warning', label: '管理员' }
  return { class: 'tag-success', label: '成员' }
}

function fmtDate(d) {
  if (!d) return '—'
  try {
    return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
  } catch {
    return d
  }
}

// --- Lifecycle ---
onMounted(() => {
  fetchTeams()
})

onBeforeUnmount(() => {
  clearTimeout(toastTimer)
})
</script>

<style scoped>
/* ==================== Tabs ==================== */
.tabs {
  display: flex; gap: 2px; margin-bottom: var(--space-lg);
  border-bottom: 2px solid var(--border-light);
}
.tab-btn {
  padding: 10px 20px; border: none; background: none;
  font-size: .88rem; font-weight: 500; color: var(--text-secondary);
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: all var(--fast); font-family: var(--font-sans);
}
.tab-btn:hover { color: var(--text); }
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }

/* ==================== Empty State ==================== */
.empty-state { text-align: center; padding: 56px var(--space-lg); }
.empty-icon { font-size: 3rem; margin-bottom: var(--space-md); }
.empty-title { font-size: 1.05rem; font-weight: 650; margin-bottom: 6px; color: var(--text); }
.empty-hint { font-size: .84rem; color: var(--text-secondary); margin-bottom: var(--space-lg); }
.empty-actions { display: flex; gap: var(--space-sm); justify-content: center; }

/* ==================== Team Cards ==================== */
.team-list { display: flex; flex-direction: column; gap: var(--space-md); }
.team-card { padding: var(--space-md) var(--space-lg); }
.team-card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: var(--space-lg); }
.team-card-info { flex: 1; min-width: 0; }
.team-name { font-size: 1.05rem; font-weight: 650; margin-bottom: 8px; }
.team-meta { display: flex; align-items: center; gap: var(--space-sm); flex-wrap: wrap; }
.meta-item { font-size: .78rem; color: var(--text-secondary); }

.team-card-code {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px; border-radius: var(--radius-sm);
  background: var(--bg); border: 1px dashed var(--border);
  cursor: pointer; transition: all var(--fast); user-select: none;
  flex-shrink: 0;
}
.team-card-code:hover { border-color: var(--primary); background: var(--primary-light); }
.code-label { font-size: .68rem; color: var(--text-muted); text-transform: uppercase; }
.code-val { font-family: var(--font-mono); font-size: .88rem; font-weight: 600; color: var(--text); letter-spacing: 1px; }
.code-copy-hint { font-size: .8rem; opacity: .5; }

.team-card-actions { margin-top: var(--space-md); display: flex; gap: var(--space-sm); }

/* ==================== Forms ==================== */
.field { display: flex; flex-direction: column; gap: 4px; margin-bottom: var(--space-md); }
.field label { font-size: .78rem; font-weight: 600; color: var(--text-secondary); }
.field input {
  padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .88rem; font-family: var(--font-sans); outline: none; background: var(--surface);
  color: var(--text); transition: border-color var(--fast);
}
.field input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.field-hint { font-size: .7rem; color: var(--text-muted); }
.form-error { color: var(--danger); font-size: .8rem; margin-bottom: var(--space-sm); font-weight: 500; }

/* ==================== Success Card (after create) ==================== */
.success-card { text-align: center; padding: var(--space-xl); border-color: var(--success); }
.success-icon { font-size: 2.5rem; margin-bottom: var(--space-sm); }
.success-team-name { font-size: 1.1rem; font-weight: 650; color: var(--text); margin-bottom: var(--space-md); }
.invite-code-box {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 20px; border-radius: var(--radius);
  background: var(--success-light); border: 2px solid var(--success);
  margin-bottom: var(--space-md);
}
.invite-label { font-size: .72rem; color: var(--success); text-transform: uppercase; font-weight: 600; }
.invite-code { font-family: var(--font-mono); font-size: 1.2rem; font-weight: 800; color: var(--success); letter-spacing: 2px; }
.invite-hint { font-size: .78rem; color: var(--text-secondary); margin-top: var(--space-sm); }

/* ==================== Dashboard ==================== */
.back-link { color: var(--primary); cursor: pointer; font-size: .84rem; font-weight: 500; display: inline-block; margin-bottom: 4px; }
.back-link:hover { text-decoration: underline; }

.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: var(--space-md); }
.stat-card { text-align: center; padding: var(--space-lg); }
.stat-num { display: block; font-size: 2rem; font-weight: 800; color: var(--primary); }
.stat-label { display: block; font-size: .78rem; color: var(--text-muted); margin-top: 4px; }

.member-table { width: 100%; border-collapse: collapse; font-size: .85rem; }
.member-table th {
  text-align: left; padding: 10px 12px; border-bottom: 2px solid var(--border);
  font-size: .74rem; font-weight: 650; color: var(--text-muted); text-transform: uppercase; letter-spacing: .3px;
}
.member-table td { padding: 10px 12px; border-bottom: 1px solid var(--border-light); }
.mem-name { font-weight: 600; }
.mem-date { color: var(--text-muted); font-size: .8rem; }
.completion-count { font-weight: 700; color: var(--primary); font-size: .95rem; }

/* ==================== Toast ==================== */
.toast-popup {
  position: fixed; bottom: 32px; right: 32px; z-index: 200;
  background: var(--surface-raised); color: var(--text);
  padding: 12px 22px; border-radius: var(--radius);
  border: 1px solid var(--border); box-shadow: var(--shadow-lg);
  font-size: .84rem; font-weight: 500;
  pointer-events: none;
}
.toast-fade-enter-active { transition: all .3s var(--ease); }
.toast-fade-leave-active { transition: all .25s ease-in; }
.toast-fade-enter-from { opacity: 0; transform: translateY(12px); }
.toast-fade-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
