<template>
  <div>
    <AchievementToast v-if="newAchievement" :name="newAchievement.name" :desc="newAchievement.desc" />
    <div class="page-header">
      <h1>学习仪表板</h1>
      <p>追踪你的 QA 技能成长轨迹</p>
    </div>

    <div v-if="loading" class="card" style="text-align:center;padding:48px;color:var(--text-muted);">⏳ 加载中...</div>
    <template v-else>
    <div v-if="store.progress.total === 0" class="card" style="text-align:center;padding:40px;margin-bottom:var(--space-lg);">
      <p style="font-size:2rem;margin-bottom:8px;">🚀</p>
      <p style="font-weight:600;margin-bottom:4px;">尚未加载关卡数据</p>
      <p style="font-size:.82rem;color:var(--text-secondary);">请确认后端服务已启动</p>
    </div>
    <!-- Stats -->
    <div class="stats-row" v-else>
      <div class="stat-card" :aria-label="'已完成关卡 ' + (store.progress.completed || 0)">
        <span class="stat-icon" aria-hidden="true">✅</span>
        <div><span class="stat-num">{{ store.progress.completed || 0 }}</span><span class="stat-label">已完成关卡</span></div>
      </div>
      <div class="stat-card" :aria-label="'总积分 ' + (store.progress.points || 0)">
        <span class="stat-icon" aria-hidden="true">⭐</span>
        <div><span class="stat-num">{{ store.progress.points || 0 }}</span><span class="stat-label">总积分</span></div>
      </div>
      <div class="stat-card" :aria-label="'完成度 ' + pct + '%'">
        <span class="stat-icon" aria-hidden="true">📈</span>
        <div><span class="stat-num">{{ pct }}%</span><span class="stat-label">完成度</span></div>
      </div>
      <div class="stat-card" :aria-label="'学习模块 ' + totalStages + ' 个'">
        <span class="stat-icon" aria-hidden="true">🎯</span>
        <div><span class="stat-num">{{ totalStages }}</span><span class="stat-label">学习模块</span></div>
      </div>
    </div>

    <!-- Stage progress -->
    <div class="card" style="margin-bottom:var(--space-lg);">
      <h3 style="margin-bottom:var(--space-md);font-size:.95rem;">模块进度</h3>
      <div class="stage-bars">
        <div v-for="(s, k) in store.stages" :key="k" class="stage-bar-row">
          <span class="stage-bar-label">{{ stageName(k) }}</span>
          <div class="stage-bar-track">
            <div class="stage-bar-fill" :class="barColor(s)" :style="{width: s.total?s.completed/s.total*100+'%':'0%'}" role="progressbar" :aria-valuenow="s.total ? Math.round(s.completed/s.total*100) : 0" aria-valuemin="0" aria-valuemax="100" :aria-label="stageName(k) + ' 完成度'"></div>
          </div>
          <span class="stage-bar-num">{{ s.completed || 0 }}/{{ s.total }}</span>
        </div>
      </div>
    </div>

    <!-- Learning Path -->
    <div class="card" style="margin-bottom:var(--space-lg);">
      <h3 style="margin-bottom:var(--space-md);font-size:.95rem;">学习路径</h3>
      <div class="path-track">
        <div v-for="(m,i) in milestones" :key="i" class="path-milestone" :class="{ done: m.done, current: m.current }">
          <div class="path-dot">{{ m.done ? '✅' : m.current ? '📍' : '○' }}</div>
          <div class="path-info">
            <strong>{{ m.label }}</strong>
            <span>{{ m.desc }}</span>
          </div>
        </div>
      </div>
      <div v-if="nextActions.length" class="next-actions">
        <h4 style="font-size:.82rem;margin-bottom:6px;">建议下一步</h4>
        <div v-for="(a,i) in nextActions" :key="i" class="action-item">• {{ a }}</div>
      </div>
    </div>

    <!-- Skill Progress -->
    <div class="card" style="margin-bottom:var(--space-lg);">
      <h3 style="margin-bottom:var(--space-md);font-size:.95rem;">技能进度</h3>
      <div class="skill-bars">
        <div v-for="(v,k) in skillData" :key="k" class="skill-row">
          <span class="skill-name">{{ v.name }}</span>
          <div class="skill-track">
            <div class="skill-fill" :style="{width: v.pct+'%'}"></div>
          </div>
          <span class="skill-num">{{ v.completed }}/{{ v.total }}</span>
        </div>
        <p v-if="!skillData.length" style="color:var(--text-muted);font-size:.82rem;text-align:center;padding:16px;">暂无数据，完成关卡后显示</p>
      </div>
    </div>

    <!-- Achievements -->
    <div class="card" style="margin-bottom:var(--space-lg);">
      <h3 style="margin-bottom:var(--space-md);font-size:.95rem;">成就徽章</h3>
      <div class="ach-grid">
        <div v-for="a in achievements" :key="a.key" class="ach-badge" :class="{ earned: a.earned }">
          <span class="ach-icon">{{ a.earned ? a.icon : '🔒' }}</span>
          <span class="ach-name">{{ a.name }}</span>
          <span class="ach-desc">{{ a.desc }}</span>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="card">
      <h3 style="margin-bottom:var(--space-md);font-size:.95rem;">快速操作</h3>
      <div class="quick-actions">
        <router-link to="/levels" class="quick-action">
          <span class="qa-icon">🎯</span>
          <div><strong>继续闯关</strong><span>102 关覆盖 22 个测试领域</span></div>
        </router-link>
        <router-link to="/labs" class="quick-action">
          <span class="qa-icon">🧪</span>
          <div><strong>进入实验室</strong><span>SQL · Linux · API 实操</span></div>
        </router-link>
        <router-link to="/labs/sql" class="quick-action">
          <span class="qa-icon">🗄️</span>
          <div><strong>SQL 练习</strong><span>数据验证查询技能</span></div>
        </router-link>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLevelsStore } from '../stores/levels'
import AchievementToast from '../components/AchievementToast.vue'
const store = useLevelsStore()

const pct = computed(() => store.progress.total ? Math.round(store.progress.completed / store.progress.total * 100) : 0)
const totalStages = computed(() => Object.keys(store.stages).length)

function stageName(k) {
  return {
    beginner: '入门', intermediate: '进阶', advanced: '专家',
    web: 'Web', api: 'API', mobile: 'APP',
    performance: '性能', security: '安全',
    automotive: '车载', network: '网络',
    ops: '运维', cicd: 'CI/CD',
    accessibility: '无障碍', data: '数据测试',
    chaos: '混沌工程', visual: '视觉回归',
    risk: '风险驱动', metrics: '度量分析',
    'automation-arch': '自动化架构', 'advanced-api': '现代API',
    compliance: '合规测试', fintech: '金融测试',
  }[k] || k
}
function barColor(s) {
  const pct = s.total ? s.completed / s.total : 0
  if (pct >= 1) return 'fill-green'
  if (pct >= .5) return 'fill-blue'
  if (pct > 0) return 'fill-purple'
  return ''
}

const skillKeys = ['beginner','intermediate','advanced','web','api','mobile','performance','security','network','ops','cicd']
const skillData = computed(() => {
  const stages = store.stages || {}
  return skillKeys.map(k => {
    const s = stages[k]
    if (!s || !s.total) return null
    return {
      key: k,
      name: stageName(k),
      completed: s.completed || 0,
      total: s.total,
      pct: Math.round((s.completed || 0) / s.total * 100)
    }
  }).filter(Boolean)
})


const milestones = computed(() => {
  const stages = store.stages || {}
  const completed = store.progress.completed || 0
  const allDone = {}

  const stageOrder = ['beginner','intermediate','advanced','web','api','mobile','performance','security','automotive','network','ops','cicd','accessibility','data','chaos','visual','risk','metrics','automation-arch','advanced-api','compliance']
  stageOrder.forEach(k => { allDone[k] = (stages[k]?.completed || 0) >= (stages[k]?.total || 1) && (stages[k]?.total || 0) > 0 })

  return [
    { key:'start', label:'入门小白', desc:'完成入门基础8关', done: allDone.beginner, current: completed < 8 },
    { key:'grow', label:'技能构建', desc:'完成进阶+专家+场景共15关', done: completed >= 23, current: completed >= 8 && completed < 23 },
    { key:'expand', label:'领域拓展', desc:'覆盖Web、API、移动、性能4域', done: allDone.web && allDone.api && allDone.mobile && allDone.performance, current: completed >= 23 && !(allDone.web && allDone.api && allDone.mobile && allDone.performance) },
    { key:'specialize', label:'专业深化', desc:'安全+网络+运维+CI/CD+车载', done: allDone.security && allDone.network && allDone.ops && allDone.cicd && allDone.automotive, current: completed >= 35 && !(allDone.security && allDone.network && allDone.ops && allDone.cicd && allDone.automotive) },
    { key:'master', label:'测试专家', desc:'完成全部102关', done: completed >= 102, current: completed >= 80 && completed < 102 },
  ]
})

const nextActions = computed(() => {
  const completed = store.progress.completed || 0
  const stages = store.stages || {}
  const actions = []
  if (completed < 8) actions.push('完成「入门基础」8关 —— 建立测试理论根基')
  else if (completed < 15) actions.push('挑战「进阶提升」和「专家进阶」关卡 —— 巩固核心技能')
  else if (!stages.security || stages.security.completed < stages.security.total) actions.push('完成「安全测试」关卡 —— 2026年最紧缺的技能之一')
  if (!stages.performance || stages.performance.completed < stages.performance.total) actions.push('完成「性能测试」关卡 —— 掌握k6和Core Web Vitals')
  if (!stages.accessibility || !stages.accessibility.total) actions.push('探索「无障碍测试」新关卡 —— 欧美合规必备')
  if (completed >= 68 && completed < 84) actions.push('冲刺完成最后16关，解锁「测试专家」成就')
  if (actions.length === 0) actions.push('你已完成全部学习路径！探索实验室或管理测试用例。')
  return actions.slice(0, 3)
})

const loading = ref(true)

const achievements = computed(() => {
  const completed = store.progress.completed || 0
  const stages = store.stages || {}
  const beginnerDone = (stages.beginner?.completed || 0) >= (stages.beginner?.total || 1)
  const webDone = (stages.web?.completed || 0) >= (stages.web?.total || 1)
  const labCount = parseInt(localStorage.getItem('qa-lab-count') || '0')
  return [
    { key: 'first', icon: '🌟', name: '初出茅庐', desc: '完成第 1 关', earned: completed >= 1 },
    { key: 'five', icon: '🔥', name: '小有所成', desc: '完成 5 关', earned: completed >= 5 },
    { key: 'ten', icon: '⚡', name: '中流砥柱', desc: '完成 10 关', earned: completed >= 10 },
    { key: 'half', icon: '💎', name: '半壁江山', desc: '完成 20 关', earned: completed >= 20 },
    { key: 'beginner', icon: '🌱', name: '入门毕业', desc: '完成全部入门关卡', earned: beginnerDone },
    { key: 'web', icon: '🌐', name: 'Web 专家', desc: '完成全部 Web 测试关卡', earned: webDone },
    { key: 'lab1', icon: '🧪', name: '实验室新人', desc: '使用 1 个实验室', earned: labCount >= 1 },
    { key: 'lab3', icon: '🔬', name: '实验达人', desc: '使用 3 个实验室', earned: labCount >= 3 },
  ]
})

const newAchievement = ref(null)

onMounted(async () => {
  try { await store.fetchList() } catch { /* store handles error */ }
  loading.value = false

  // Detect newly unlocked achievements
  const prevEarned = JSON.parse(localStorage.getItem('qa-achievements') || '[]')
  const currentEarned = achievements.value.filter(a => a.earned).map(a => a.key)
  const newlyEarned = currentEarned.find(k => !prevEarned.includes(k))
  if (newlyEarned) {
    const ach = achievements.value.find(a => a.key === newlyEarned)
    if (ach) newAchievement.value = ach
  }
  localStorage.setItem('qa-achievements', JSON.stringify(currentEarned))
})
</script>

<style scoped>
.stats-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; margin-bottom: var(--space-lg); }
.stat-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: 18px 20px; display: flex; align-items: center; gap: 14px;
  box-shadow: var(--shadow-xs); transition: all var(--fast);
}
.stat-card:hover { box-shadow: var(--shadow); transform: translateY(-1px); }
.stat-icon { font-size: 1.6rem; flex-shrink: 0; }
.stat-num { display: block; font-size: 1.5rem; font-weight: 800; color: var(--primary); line-height: 1.1; }
.stat-label { font-size: .75rem; color: var(--text-muted); font-weight: 500; }

.stage-bars { display: flex; flex-direction: column; gap: 10px; }
.stage-bar-row { display: flex; align-items: center; gap: 12px; }
.stage-bar-label { width: 90px; font-size: .78rem; color: var(--text-secondary); font-weight: 500; text-align: right; flex-shrink: 0; }
.stage-bar-track { flex: 1; height: 8px; background: var(--border-light); border-radius: 4px; overflow: hidden; }
.stage-bar-fill { height: 100%; border-radius: 4px; transition: width .6s var(--ease); }
.stage-bar-fill.fill-purple { background: var(--primary); }
.stage-bar-fill.fill-blue { background: linear-gradient(90deg, var(--primary), #8b5cf6); }
.stage-bar-fill.fill-green { background: var(--success); }
.stage-bar-num { font-size: .75rem; color: var(--text-muted); font-weight: 600; min-width: 36px; }

.quick-actions { display: flex; flex-direction: column; gap: 8px; }
.quick-action {
  display: flex; align-items: center; gap: 14px; padding: 14px 16px;
  border-radius: var(--radius); border: 1px solid var(--border);
  text-decoration: none; color: var(--text); transition: all var(--fast);
}
.quick-action:hover { border-color: var(--primary); background: var(--primary-light); box-shadow: var(--shadow-xs); }
.qa-icon { font-size: 1.5rem; flex-shrink: 0; }
.quick-action strong { display: block; font-size: .88rem; }
.quick-action span { font-size: .76rem; color: var(--text-secondary); }

.ach-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }
.ach-badge { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 14px 10px; border-radius: var(--radius); border: 1px solid var(--border); text-align: center; opacity: .4; transition: all var(--fast); }
.ach-badge.earned { opacity: 1; border-color: var(--warning); background: var(--warning-light); }

.skill-bars { display: flex; flex-direction: column; gap: 10px; }
.skill-row { display: flex; align-items: center; gap: 12px; }
.skill-name { width: 70px; font-size: .8rem; color: var(--text-secondary); font-weight: 500; text-align: right; flex-shrink: 0; }
.skill-track { flex: 1; height: 8px; background: var(--border-light); border-radius: 4px; overflow: hidden; }
.skill-fill { height: 100%; background: var(--primary); border-radius: 4px; transition: width .6s var(--ease); min-width: 2px; }
.skill-num { font-size: .75rem; color: var(--text-muted); font-weight: 600; min-width: 36px; }

.path-track { display: flex; flex-direction: column; gap: 0; position: relative; padding-left: 28px; }
.path-track::before { content: ''; position: absolute; left: 14px; top: 8px; bottom: 8px; width: 2px; background: var(--border); }
.path-milestone { display: flex; gap: 12px; align-items: flex-start; padding: 10px 0; position: relative; }
.path-dot { width: 28px; height: 28px; border-radius: 50%; background: var(--border-light); display: flex; align-items: center; justify-content: center; font-size: .8rem; flex-shrink: 0; z-index: 1; margin-left: -28px; }
.path-milestone.done .path-dot { background: var(--success); color: #fff; }
.path-milestone.current .path-dot { background: var(--primary); color: #fff; box-shadow: 0 0 0 4px var(--primary-light); }
.path-info strong { font-size: .84rem; display: block; }
.path-info span { font-size: .76rem; color: var(--text-secondary); }
.next-actions { margin-top: 14px; padding: 12px 16px; background: var(--primary-light); border-radius: var(--radius); }
.action-item { font-size: .8rem; color: var(--text); padding: 4px 0; }
.ach-icon { font-size: 1.6rem; }
.ach-name { font-size: .76rem; font-weight: 650; }
.ach-desc { font-size: .68rem; color: var(--text-muted); line-height: 1.3; }
</style>
