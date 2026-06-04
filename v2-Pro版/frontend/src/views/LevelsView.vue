<template>
  <div>
    <div class="page-header">
      <h1>测试技能闯关</h1>
      <p>{{ store.progress.completed || 0 }}/{{ store.progress.total || 0 }} 关已完成 · {{ store.progress.points || 0 }} 积分</p>
    </div>

    <!-- Search + Filter -->
    <div class="controls">
      <div class="search-box">
        <span>🔍</span>
        <input v-model="search" placeholder="搜索关卡名称或描述..." class="search-input" aria-label="搜索关卡名称或描述">
        <button v-if="search" @click="search=''" class="search-clear">✕</button>
      </div>
      <select v-model="filterType" class="filter-select">
        <option value="">全部题型</option>
        <option value="quiz">📝 选择题</option>
        <option value="code">编程题</option>
        <option value="explore">探索题</option>
      </select>
    </div>

    <!-- Overall progress -->
    <div class="overall-progress">
      <div class="op-bar"><div class="op-fill" :style="{width: pct+'%'}"></div></div>
      <span class="op-text">{{ pct }}%</span>
    </div>

    <!-- Stages (accordion) -->
    <div v-for="(key, idx) in visibleStages" :key="key" class="stage-block" role="list">
      <button class="stage-header" @click="openStages[key] = openStages[key] === undefined ? false : !openStages[key]" :class="{ open: openStages[key] }"
        :aria-expanded="openStages[key] ? 'true' : 'false'" :aria-controls="'stage-'+key">
        <span class="stage-chevron">▸</span>
        <span class="stage-name">{{ stageName(key) }}</span>
        <span class="stage-progress">{{ completedIn(key) }}/{{ totalIn(key) }}</span>
        <span class="stage-bar-mini"><span class="stage-bar-mini-fill" :style="{width: stagePct(key)+'%'}"></span></span>
      </button>
      <div :id="'stage-'+key" v-show="openStages[key]" class="level-grid" role="list">
        <div v-for="lv in filteredLevels(key)" :key="lv.id"
          class="level-card" :class="{ completed: lv.status==='completed', locked: lv.status==='locked', current: lv.status==='in_progress'||lv.status==='unlocked' }"
          role="button" tabindex="0"
          :aria-label="lv.title + ' — ' + lv.description"
          @click="openLevel(lv)"
          @keydown.enter="openLevel(lv)"
          @keydown.space.prevent="openLevel(lv)">
          <div class="lc-top">
            <span class="lc-num">#{{ lv.order }}</span>
            <span class="lc-status">{{ statusIcon(lv.status) }}</span>
          </div>
          <h3>{{ lv.title }}</h3>
          <p>{{ lv.description }}</p>
          <div class="lc-bottom">
            <span :class="['tag', levelTagClass(lv)]">{{ typeLabel(lv.task_type) }}</span>
            <span class="lc-pts">{{ lv.points }} 分</span>
          </div>
        </div>
        <div v-if="filteredLevels(key).length === 0" class="empty-stage">没有匹配的关卡</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLevelsStore } from '../stores/levels'
const store = useLevelsStore()
const router = useRouter()

const search = ref('')
const filterType = ref('')
const openStages = reactive({
  beginner: true, web: true, api: true, mobile: true,
  performance: true, security: true, network: true, ops: true, cicd: true, automotive: true,
  accessibility: true, data: true, chaos: true, visual: true, risk: true, metrics: true, 'automation-arch': true, 'advanced-api': true, compliance: true,
})

const visibleStages = computed(() => stageOrder.filter(k => totalIn(k) > 0))

const pct = computed(() => store.progress.total ? Math.round(store.progress.completed / store.progress.total * 100) : 0)

function stageName(k) {
  return {
    beginner: '入门基础', intermediate: '进阶提升', advanced: '专家进阶',
    web: 'Web测试', api: 'API测试', mobile: 'APP测试',
    performance: '性能测试', security: '安全测试',
    automotive: '车载测试', network: '网络 & 抓包',
    ops: '运维 & 数据库', cicd: 'CI/CD',
    accessibility: '无障碍测试', data: '数据测试',
    chaos: '混沌工程', visual: '视觉回归',
    risk: '风险驱动', metrics: '度量分析',
    'automation-arch': '自动化架构', 'advanced-api': '现代API',
    compliance: '合规测试', fintech: '金融测试',
  }[k] || k
}
const stageOrder = ['beginner', 'intermediate', 'advanced', 'web', 'api', 'mobile', 'performance', 'security', 'automotive', 'network', 'ops', 'cicd', 'accessibility', 'data', 'chaos', 'visual', 'risk', 'metrics', 'automation-arch', 'advanced-api', 'compliance', 'fintech']

function levelsByStage(s) { return store.levels.filter(l => l.stage === s) }
function completedIn(s) { return store.levels.filter(l => l.stage === s && l.status === 'completed').length }
function totalIn(s) { return store.levels.filter(l => l.stage === s).length }
function stagePct(s) { const t = totalIn(s); return t ? Math.round(completedIn(s) / t * 100) : 0 }

function filteredLevels(s) {
  return levelsByStage(s).filter(l => {
    if (search.value) {
      const q = search.value.toLowerCase()
      if (!l.title.toLowerCase().includes(q) && !l.description.toLowerCase().includes(q)) return false
    }
    if (filterType.value && l.task_type !== filterType.value) return false
    return true
  })
}

function statusIcon(s) { return { locked: '🔒', unlocked: '▶️', in_progress: '📖', completed: '✅' }[s] || '' }
function typeLabel(t) { return { quiz: '选择题', code: '编程题', explore: '探索题', debug: 'Debug', scenario: '场景', analyze: '分析题' }[t] || t }
function levelTagClass(l) {
  if (l.task_type === 'code') return 'tag-primary'
  if (l.task_type === 'quiz') return 'tag-warning'
  if (l.task_type === 'debug') return 'tag-danger'
  if (l.task_type === 'scenario') return 'tag-primary'
  return 'tag-success'
}
function openLevel(lv) { if (lv.status !== 'locked') router.push('/level/' + lv.id) }

onMounted(() => store.fetchList())
</script>

<style scoped>
/* Controls */
.controls { display: flex; gap: 10px; margin-bottom: var(--space-md); }
.search-box {
  flex: 1; display: flex; align-items: center; gap: 8px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 0 14px; transition: border-color var(--fast);
}
.search-box:focus-within { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.search-box span { font-size: .9rem; flex-shrink: 0; }
.search-input { flex: 1; border: none; outline: none; padding: 10px 0; font-size: .86rem; background: transparent; color: var(--text); font-family: var(--font-sans); }
.search-clear { padding: 4px 8px; border: none; background: var(--border); border-radius: var(--radius-full); cursor: pointer; font-size: .7rem; color: var(--text-secondary); }
.filter-select {
  padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--surface); color: var(--text); font-size: .84rem; outline: none; cursor: pointer;
  font-family: var(--font-sans);
}
.filter-select:focus { border-color: var(--primary); }

/* Overall progress */
.overall-progress { display: flex; align-items: center; gap: 12px; margin-bottom: var(--space-lg); }
.op-bar { flex: 1; height: 8px; background: var(--border-light); border-radius: 4px; overflow: hidden; }
.op-fill { height: 100%; background: linear-gradient(90deg, var(--primary), #8b5cf6, #ec4899); border-radius: 4px; transition: width .6s var(--ease); }
.op-text { font-size: .82rem; font-weight: 700; color: var(--primary); min-width: 40px; text-align: right; }

/* Stage accordion */
.stage-block { margin-bottom: 6px; }
.stage-header {
  width: 100%; display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--surface); cursor: pointer; font-size: .88rem;
  transition: all var(--fast); font-family: var(--font-sans); text-align: left;
}
.stage-header:hover { border-color: var(--primary); background: var(--primary-light); }
.stage-header.open { border-radius: var(--radius) var(--radius) 0 0; border-bottom-color: transparent; }
.stage-chevron { font-size: .7rem; transition: transform var(--fast); width: 14px; text-align: center; color: var(--text-muted); }
.stage-header.open .stage-chevron { transform: rotate(90deg); }
.stage-name { font-weight: 650; flex-shrink: 0; }
.stage-progress { font-size: .76rem; color: var(--text-muted); font-weight: 500; }
.stage-bar-mini { flex: 1; height: 5px; background: var(--border-light); border-radius: 3px; overflow: hidden; min-width: 40px; }
.stage-bar-mini-fill { height: 100%; background: var(--primary); border-radius: 3px; transition: width .4s var(--ease); }

/* Level grid */
.level-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 8px;
  padding: 12px; border: 1px solid var(--border); border-top: none;
  border-radius: 0 0 var(--radius) var(--radius); background: var(--bg);
}
.level-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 16px; cursor: pointer; transition: all var(--fast);
  display: flex; flex-direction: column; gap: 6px;
}
.level-card:hover:not(.locked) { box-shadow: var(--shadow); transform: translateY(-2px); border-color: var(--primary); }
.level-card.completed { border-left: 3px solid var(--success); background: var(--success-light); }
.level-card.current { border-left: 3px solid var(--primary); }
.level-card.locked { opacity: .5; cursor: not-allowed; filter: grayscale(.3); }
.lc-top { display: flex; justify-content: space-between; align-items: center; }
.lc-num { font-size: .68rem; color: var(--text-muted); font-weight: 700; letter-spacing: .5px; }
.lc-status { font-size: .85rem; }
.level-card h3 { font-size: .88rem; font-weight: 650; line-height: 1.3; }
.level-card p { font-size: .76rem; color: var(--text-secondary); line-height: 1.45; flex: 1; }
.lc-bottom { display: flex; justify-content: space-between; align-items: center; }
.lc-pts { font-size: .72rem; color: var(--text-muted); font-weight: 600; }
.empty-stage { grid-column: 1/-1; text-align: center; padding: 20px; color: var(--text-muted); font-size: .82rem; }
</style>
