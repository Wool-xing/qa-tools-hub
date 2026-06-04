<template>
  <div class="lab-page">
    <div class="scenario-bar">
      <button v-for="s in scenarios" :key="s.id" class="scenario-btn" :class="{ active: currentScenario === s.id }"
        @click="currentScenario = s.id; result = null">{{ s.label }}</button>
    </div>

    <div class="card" style="margin-bottom:var(--space-md);">
      <div class="schema-info">📋 <strong>{{ currentSchema }}</strong></div>
      <textarea v-model="sql" placeholder="SELECT * FROM bugs WHERE status = 'open'" rows="4" class="sql-input"></textarea>
      <div class="toolbar">
        <span class="hint-text">提示: SELECT · FROM · WHERE · GROUP BY · HAVING · ORDER BY · LIMIT</span>
        <button class="btn-primary" :disabled="!sql.trim()" @click="execute">▶ 执行</button>
      </div>
    </div>

    <div v-if="loading" class="card" style="text-align:center;padding:32px;color:var(--text-secondary);">⏳ 执行中...</div>

    <div v-if="result" class="card" style="overflow:hidden;padding:0;">
      <div v-if="result.ok">
        <div style="padding:12px 20px;font-size:.78rem;color:var(--text-secondary);border-bottom:1px solid var(--border);">
          返回 <strong>{{ result.row_count }}</strong> 行 · {{ result.columns.length }} 列
        </div>
        <div style="overflow-x:auto;">
          <table v-if="result.rows.length" class="result-table">
            <thead><tr><th v-for="c in result.columns" :key="c">{{ c }}</th></tr></thead>
            <tbody><tr v-for="(row, i) in result.rows" :key="i"><td v-for="c in result.columns" :key="c">{{ row[c] }}</td></tr></tbody>
          </table>
        </div>
        <p v-if="!result.rows.length" style="padding:32px;text-align:center;color:var(--text-muted);">查询执行成功，无返回数据</p>
      </div>
      <div v-else style="padding:16px 20px;color:var(--danger);background:var(--danger-light);font-size:.84rem;">❌ {{ result.error }}</div>
    </div>

    <details class="hints-card">
      <summary>💡 试试这些查询</summary>
      <ul>
        <li><code>SELECT * FROM bugs WHERE status = 'open'</code></li>
        <li><code>SELECT module, COUNT(*) FROM bugs GROUP BY module</code></li>
        <li><code>SELECT * FROM bugs WHERE severity = 'P0'</code></li>
        <li><code>SELECT assignee, COUNT(*) as cnt FROM bugs GROUP BY assignee ORDER BY cnt DESC</code></li>
        <li><code>SELECT * FROM bugs WHERE severity = 'P0' AND status != 'fixed'</code></li>
      </ul>
    </details>

    <!-- Challenge Mode -->
    <div class="card" style="margin-top:var(--space-md);">
      <h3 style="margin-bottom:10px;font-size:.9rem;">🏆 进阶挑战</h3>
      <div class="challenge-bar">
        <button v-for="(c,i) in challenges" :key="i" class="challenge-btn" :class="{ active: chIdx===i, solved: chSolved[i] }"
          @click="selectChallenge(i)">{{ c.diff }} {{ c.label }}</button>
      </div>
      <div v-if="challenges[chIdx]" class="challenge-card">
        <p class="ch-task">{{ challenges[chIdx].task }}</p>
        <p class="ch-hint" v-if="showHint">💡 {{ challenges[chIdx].hint }}</p>
        <div class="ch-actions">
          <button class="btn-ghost" style="font-size:.72rem;" @click="showHint=!showHint">{{ showHint ? '隐藏' : '显示' }}提示</button>
          <button class="btn-primary" style="font-size:.78rem;padding:6px 16px;" @click="checkChallenge" :disabled="!sql.trim()">✅ 提交挑战</button>
        </div>
        <div v-if="chFeedback" class="ch-feedback" :class="chFeedback.ok ? 'pass' : 'fail'">
          {{ chFeedback.ok ? '🎉 正确！' : '❌ 不对。' }} {{ chFeedback.msg }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { labs } from '../api'

const sql = ref('SELECT * FROM bugs')
const result = ref(null)
const loading = ref(false)
const currentScenario = ref(38)

const scenarios = [
  { id: 38, label: '🐛 缺陷管理库', schema: 'bugs(id, title, module, severity, status, assignee)' },
  { id: 31, label: '👤 用户表', schema: 'users(id, username, password, role)' },
  { id: 0, label: '📊 通用数据', schema: 'test_data(id, name, value, category)' },
]

const currentSchema = computed(() => scenarios.find(s => s.id === currentScenario)?.schema || '')

async function execute() {
  loading.value = true; result.value = null
  try { result.value = await labs.sql(sql.value, currentScenario.value) }
  catch (e) { result.value = { ok: false, error: e.message } }
  loading.value = false
}

// Challenge mode
const chIdx = ref(0), showHint = ref(false), chFeedback = ref(null), chSolved = ref([false, false, false])
const challenges = [
  { diff: '⭐', label: '初级', task: '查询所有P0级别的缺陷', hint: 'WHERE severity = \'P0\'', check: (rows) => rows.length === 2 && rows.every(r => r.severity === 'P0') },
  { diff: '⭐⭐', label: '中级', task: '统计每个模块的缺陷数量，按数量降序', hint: 'GROUP BY module, COUNT(*), ORDER BY COUNT(*) DESC', check: (rows) => rows.length >= 3 && rows[0].hasOwnProperty('module') },
  { diff: '⭐⭐⭐', label: '高级', task: '找出被分配了P0缺陷的人员（去重，排除状态为fixed的）', hint: 'WHERE severity = \'P0\' AND status != \'fixed\', 用DISTINCT', check: (rows) => rows.length === 1 && rows[0].assignee === 'Bob' },
]

function selectChallenge(i) { chIdx.value = i; showHint.value = false; chFeedback.value = null }

async function checkChallenge() {
  chFeedback.value = null
  try {
    const r = await labs.sql(sql.value, 38)
    if (!r.ok) { chFeedback.value = { ok: false, msg: r.error }; return }
    const ok = challenges[chIdx.value].check(r.rows)
    if (ok) {
      chSolved.value[chIdx.value] = true
      chFeedback.value = { ok: true, msg: `查询正确！返回了 ${r.row_count} 行数据。` }
    } else {
      chFeedback.value = { ok: false, msg: `查询执行成功但结果不符合要求。返回了 ${r.row_count} 行，检查你的条件。` }
    }
  } catch (e) { chFeedback.value = { ok: false, msg: e.message } }
}
</script>

<style scoped>
.lab-page { max-width: 800px; margin: 0 auto; }
.breadcrumb a { color: var(--primary); text-decoration: none; }
.breadcrumb a:hover { text-decoration: underline; }
.scenario-bar { display: flex; gap: 8px; margin-bottom: var(--space-md); flex-wrap: wrap; }
.scenario-btn {
  padding: 8px 16px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .8rem; font-weight: 500;
  transition: all var(--fast); font-family: var(--font-sans);
}
.scenario-btn:hover { border-color: var(--primary); }
.scenario-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }
.schema-info { font-size: .8rem; color: var(--text-secondary); margin-bottom: 10px; font-family: var(--font-mono); }
.sql-input {
  width: 100%; padding: 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .84rem; line-height: 1.7;
  background: #1a1a2e; color: #e5e7eb; outline: none; resize: vertical;
}
.sql-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.hint-text { font-size: .74rem; color: var(--text-muted); }
.result-table { width: 100%; border-collapse: collapse; font-size: .82rem; }
.result-table th { background: var(--primary-light); color: var(--primary); padding: 10px 14px; text-align: left; font-weight: 600; font-size: .76rem; white-space: nowrap; }
.result-table td { padding: 8px 14px; border-top: 1px solid var(--border-light); }
.result-table tbody tr:hover { background: var(--surface-hover); }
.hints-card { margin-top: var(--space-md); font-size: .82rem; cursor: pointer; }
.hints-card summary { color: var(--primary); font-weight: 500; margin-bottom: 8px; }
.hints-card ul { padding-left: 20px; }
.hints-card li { margin-bottom: 4px; }
.hints-card code {
  background: var(--primary-light); padding: 2px 6px; border-radius: 4px;
  font-family: var(--font-mono); font-size: .78rem; color: var(--primary);
}

.challenge-bar { display: flex; gap: 6px; margin-bottom: 12px; }
.challenge-btn { padding: 6px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border); background: var(--surface); cursor: pointer; font-size: .76rem; transition: all var(--fast); font-family: var(--font-sans); }
.challenge-btn:hover { border-color: var(--primary); }
.challenge-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }
.challenge-btn.solved { border-color: var(--success); background: var(--success-light); }
.challenge-card { padding: 14px; background: var(--bg-subtle); border-radius: var(--radius); }
.ch-task { font-size: .86rem; font-weight: 600; margin-bottom: 8px; }
.ch-hint { font-size: .78rem; color: var(--primary); margin-bottom: 8px; padding: 8px; background: var(--primary-light); border-radius: 4px; font-family: var(--font-mono); }
.ch-actions { display: flex; justify-content: space-between; align-items: center; }
.ch-feedback { margin-top: 8px; padding: 8px 12px; border-radius: 6px; font-size: .8rem; font-weight: 500; }
.ch-feedback.pass { background: var(--success-light); color: #065f46; }
.ch-feedback.fail { background: var(--warning-light); color: #92400e; }
</style>
