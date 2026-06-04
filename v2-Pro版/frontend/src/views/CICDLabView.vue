<template>
  <div class="lab-page">
    <!-- Tabs -->
    <div class="tabs-bar">
      <button v-for="t in tabs" :key="t.id" class="tab-btn" :class="{ active: activeTab === t.id }" @click="activeTab = t.id">{{ t.icon }} {{ t.label }}</button>
    </div>

    <!-- ====== TAB 1: Pipeline Builder ====== -->
    <div v-if="activeTab === 'builder'" class="tab-content">
      <!-- Stage selector -->
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3 style="margin-bottom:10px;font-size:.9rem;">📦 添加管道阶段</h3>
        <div class="stage-picker">
          <button v-for="s in availableStages" :key="s.id" class="stage-chip" :class="{ used: pipelineStages.find(ps => ps.id === s.id) }" @click="addStage(s)" :disabled="!!pipelineStages.find(ps => ps.id === s.id)">
            <span class="chip-dot" :style="{ background: s.color }"></span>{{ s.icon }} {{ s.name }}
          </button>
        </div>
        <p v-if="pipelineStages.length === 0" style="margin-top:10px;font-size:.76rem;color:var(--text-muted);">点击上方阶段将其加入管道。为每个阶段配置并行数、超时和重试次数。</p>
      </div>

      <!-- Pipeline Canvas -->
      <div class="card" v-if="pipelineStages.length > 0">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
          <h3 style="margin:0;font-size:.9rem;">🔧 管道画布</h3>
          <button class="btn-outline" @click="clearPipeline" style="font-size:.74rem;padding:4px 12px;">清空管道</button>
        </div>
        <div class="pipeline-canvas">
          <div v-for="(stage, idx) in pipelineStages" :key="stage.id + '-' + idx">
            <div class="pipeline-stage" :class="getStageStatusClass(stage)" :style="{ borderLeftColor: stage.color }">
              <div class="stage-header">
                <span class="stage-icon" :style="{ color: stage.color }">{{ stage.icon }}</span>
                <span class="stage-name">{{ stage.name }}</span>
                <span class="stage-time">{{ stage.duration }}</span>
                <span v-if="isRunning && stage.status === 'running'" class="stage-elapsed">{{ stage.elapsed }}s</span>
                <span v-if="stage.retriesUsed > 0 && (stage.status === 'passed' || stage.status === 'flaky')" class="stage-retries-tag">重试 {{ stage.retriesUsed }} 次</span>
                <span v-if="stage.status === 'failed'" class="stage-fail-icon">❌</span>
                <span v-if="stage.status === 'passed'" class="stage-pass-icon">✅</span>
                <span v-if="stage.status === 'flaky'" class="stage-flaky-icon">⚠️</span>
                <button class="stage-remove" @click="removeStage(idx)" title="移除">✕</button>
              </div>

              <!-- Progress bar when running -->
              <div v-if="stage.status === 'running'" class="stage-progress-track">
                <div class="stage-progress-fill" :style="{ width: stage.progress + '%' }"></div>
              </div>

              <!-- Parallel workers visual -->
              <div v-if="stage.workers > 1 && (stage.status === 'running' || stage.status === 'waiting' || stage.status === 'passed' || stage.status === 'flaky' || stage.status === 'failed')" class="worker-shards">
                <div v-for="w in stage.workers" :key="w" class="worker-shard" :class="{ 'shard-passed': stage.status === 'passed' || stage.status === 'flaky', 'shard-failed': stage.status === 'failed', 'shard-running': stage.status === 'running' && w <= Math.ceil(stage.progress / 100 * stage.workers) }">
                  Shard {{ w }}
                </div>
              </div>

              <!-- Config -->
              <div v-if="!isRunning" class="stage-config">
                <div class="config-row">
                  <label class="config-label" title="并行 Worker 数量">
                    👥 Workers: <strong>{{ stage.workers }}</strong>
                    <input type="range" v-model.number="stage.workers" :min="1" :max="5" class="inline-slider" />
                  </label>
                  <label class="config-label" title="超时时间（秒）">
                    ⏱️ 超时: <strong>{{ stage.timeout }}s</strong>
                    <input type="range" v-model.number="stage.timeout" :min="10" :max="600" step="10" class="inline-slider" />
                  </label>
                  <label class="config-label" title="失败重试次数">
                    🔄 重试: <strong>{{ stage.retries }}</strong>
                    <input type="range" v-model.number="stage.retries" :min="0" :max="3" class="inline-slider" />
                  </label>
                </div>
              </div>
            </div>

            <!-- Connector arrow -->
            <div v-if="idx < pipelineStages.length - 1" class="pipeline-connector">
              <div class="connector-line"></div>
              <div class="connector-arrow">▼</div>
            </div>
          </div>
        </div>

        <!-- Run controls -->
        <div style="margin-top:var(--space-md);display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
          <button class="btn-primary" :disabled="isRunning || pipelineStages.length === 0" @click="runPipeline">▶ 运行管道</button>
          <button class="btn-outline" :disabled="!isRunning" @click="stopPipeline">⏹ 停止</button>
          <span v-if="pipelineTotalTime" class="total-time">⏱️ 总时长预估：<strong>{{ pipelineTotalTime }}</strong></span>
          <span v-if="isRunning" class="running-indicator">🟢 运行中...</span>
        </div>

        <!-- Summary bar -->
        <div v-if="pipelineSummary" class="summary-bar" :class="{ 'summary-failed': pipelineSummary.failed }">
          {{ pipelineSummary.text }}
        </div>
      </div>

      <!-- Export -->
      <div class="card" v-if="pipelineStages.length > 0" style="margin-top:var(--space-md);">
        <h3 style="margin-bottom:10px;font-size:.9rem;">📤 导出为 CI 配置</h3>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button class="btn-outline" :class="{ active: exportFormat === 'github' }" @click="exportFormat = 'github'; generateExport()">GitHub Actions</button>
          <button class="btn-outline" :class="{ active: exportFormat === 'jenkins' }" @click="exportFormat = 'jenkins'; generateExport()">Jenkinsfile</button>
          <button class="btn-outline" :class="{ active: exportFormat === 'gitlab' }" @click="exportFormat = 'gitlab'; generateExport()">GitLab CI</button>
        </div>
        <pre v-if="exportedYaml" class="export-code"><code>{{ exportedYaml }}</code></pre>
        <button v-if="exportedYaml" class="btn-outline" style="margin-top:8px;" @click="copyExport">📋 复制到剪贴板</button>
        <span v-if="copyMsg" class="copy-msg">{{ copyMsg }}</span>
      </div>

      <!-- Challenge 1: Speed -->
      <div class="card challenge-card" style="margin-top:var(--space-md);">
        <div class="challenge-header" @click="ch1Open = !ch1Open">
          <h3 style="margin:0;font-size:.9rem;">🏆 挑战 1：速度优化 <span class="tag tag-warning">CHALLENGE</span></h3>
          <span>{{ ch1Open ? '▲' : '▼' }}</span>
        </div>
        <div v-if="ch1Open">
          <p style="font-size:.82rem;color:var(--text-secondary);margin:12px 0;">你的管道需要 <strong>45 分钟</strong>。重新配置至 <strong>15 分钟以内</strong>，不可移除强制阶段（Lint、Unit Tests、Integration Tests、E2E Tests、Security Scan）。</p>
          <button class="btn-primary" @click="loadChallenge1">📥 加载挑战配置</button>
          <div v-if="ch1Result" class="challenge-result" :class="{ win: ch1Result.win }">{{ ch1Result.text }}</div>
        </div>
      </div>
    </div>

    <!-- ====== TAB 2: Flaky Detection ====== -->
    <div v-if="activeTab === 'flaky'" class="tab-content">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3 style="margin-bottom:6px;font-size:.9rem;">🔍 Flaky 测试检测模式</h3>
        <p style="font-size:.78rem;color:var(--text-secondary);margin-bottom:12px;">分析以下 8 个测试的最近 10 次运行历史，分类并选择处理措施。</p>
      </div>

      <div class="flaky-grid">
        <div v-for="(test, idx) in flakyTests" :key="idx" class="card flaky-card" :class="{ 'flaky-selected': flakyAnalysis[idx].action !== null }">
          <div class="flaky-test-header">
            <span class="flaky-test-name">{{ test.name }}</span>
            <span class="flaky-test-rate" :style="{ color: getRateColor(test.passRate) }">{{ test.passRate }}%</span>
          </div>
          <div class="flaky-history">
            <span v-for="(r, ri) in test.history" :key="ri" class="flaky-dot" :class="{ pass: r, fail: !r }">{{ r ? '✓' : '✗' }}</span>
          </div>
          <p style="font-size:.74rem;color:var(--text-secondary);margin:8px 0;">
            {{ test.passed }}/10 通过 ({{ test.passRate }}%)
          </p>

          <!-- User classification -->
          <div v-if="flakyAnalysis[idx].action === null" class="flaky-actions">
            <label class="flaky-label">你的判断：</label>
            <div class="flaky-radios">
              <label class="radio-item" v-for="cls in classifications" :key="cls.value">
                <input type="radio" :name="'cls-' + idx" :value="cls.value" v-model="flakyAnalysis[idx].classification" />
                {{ cls.label }}
              </label>
            </div>
            <label class="flaky-label" style="margin-top:6px;">处理建议：</label>
            <div class="flaky-radios">
              <label class="radio-item" v-for="act in actions" :key="act.value">
                <input type="radio" :name="'act-' + idx" :value="act.value" v-model="flakyAnalysis[idx].action" />
                {{ act.label }}
              </label>
            </div>
          </div>
          <div v-else class="flaky-reveal">
            <div v-if="flakyAnalysis[idx].classification === flakyAnalysis[idx].correctClass && flakyAnalysis[idx].action === flakyAnalysis[idx].correctAction" class="reveal-correct">✅ 正确！</div>
            <div v-else class="reveal-wrong">
              ❌ 应为：<strong>{{ classLabel(flakyAnalysis[idx].correctClass) }}</strong> → <strong>{{ actionLabel(flakyAnalysis[idx].correctAction) }}</strong>
            </div>
            <p class="reveal-reason">{{ flakyAnalysis[idx].recommendation }}</p>
          </div>
        </div>
      </div>

      <div v-if="flakyAllSubmitted && flakyScore === null" class="card" style="margin-top:var(--space-md);text-align:center;">
        <button class="btn-primary" @click="checkAllSubmitted">✅ 提交评分</button>
      </div>
      <div v-if="flakyScore !== null" class="card" style="margin-top:var(--space-md);text-align:center;">
        <h3 style="font-size:1rem;margin-bottom:6px;">你的得分：{{ flakyScore }} / {{ flakyTests.length * 2 }}</h3>
        <p style="font-size:.78rem;color:var(--text-secondary);">
          正确分类 {{ flakyCorrectCount }} / {{ flakyTests.length }} 个测试；
          正确措施 {{ flakyActionCount }} / {{ flakyTests.length }} 个
        </p>
        <button class="btn-outline" style="margin-top:8px;" @click="resetFlaky">🔄 重试</button>
        <details style="margin-top:10px;text-align:left;">
          <summary style="font-size:.8rem;font-weight:600;color:var(--primary);cursor:pointer;">💡 学习要点</summary>
          <ul style="padding-left:20px;font-size:.78rem;color:var(--text-secondary);line-height:1.8;margin-top:6px;">
            <li><strong>稳定测试</strong>：10 次全通过 — 保持，无需操作。</li>
            <li><strong>Flaky 测试</strong>：50%-95% 通过率 — 隔离调查，检查竞态条件或网络依赖。</li>
            <li><strong>已损坏测试</strong>：&lt;50% 通过率 — 紧急修复或删除，可能环境问题或代码回归。</li>
            <li><strong>不应删除</strong>有真实覆盖价值的 flaky 测试——隔离 + 修复，不要绕过。</li>
          </ul>
        </details>
      </div>

      <!-- Challenge 2: Flaky Hunt -->
      <div class="card challenge-card" style="margin-top:var(--space-md);">
        <div class="challenge-header" @click="ch2Open = !ch2Open">
          <h3 style="margin:0;font-size:.9rem;">🏆 挑战 2：Flaky 测试猎手 <span class="tag tag-warning">CHALLENGE</span></h3>
          <span>{{ ch2Open ? '▲' : '▼' }}</span>
        </div>
        <div v-if="ch2Open">
          <p style="font-size:.82rem;color:var(--text-secondary);margin:12px 0;"><strong>50 个测试</strong>中有 <strong>3 个 flaky</strong>。分析运行历史数据，找出它们。</p>
          <div class="hunt-table-wrap">
            <table class="hunt-table">
              <thead><tr><th>测试名称</th><th>10 轮历史</th><th>选中</th></tr></thead>
              <tbody>
                <tr v-for="(t, i) in huntTests" :key="i" :class="{ 'hunt-flagged': huntSelections[i] }">
                  <td class="hunt-name">{{ t.name }}</td>
                  <td class="hunt-pattern">
                    <span v-for="(r, ri) in t.history" :key="ri" :class="{ pass: r, fail: !r }">{{ r ? '✓' : '✗' }}</span>
                  </td>
                  <td><input type="checkbox" v-model="huntSelections[i]" /></td>
                </tr>
              </tbody>
            </table>
          </div>
          <button class="btn-primary" style="margin-top:10px;" @click="submitHunt" :disabled="huntSubmitted">🎯 提交</button>
          <div v-if="huntSubmitted" class="challenge-result" :class="{ win: huntScore.precision >= 0.8 }">
            精确率 {{ (huntScore.precision * 100).toFixed(0) }}% · 召回率 {{ (huntScore.recall * 100).toFixed(0) }}% · F1 {{ (huntScore.f1 * 100).toFixed(0) }}%
            <br /><small>（真正例 {{ huntScore.tp }} / 假正例 {{ huntScore.fp }} / 假负例 {{ huntScore.fn }}）</small>
          </div>
        </div>
      </div>
    </div>

    <!-- ====== TAB 3: Failure Triage ====== -->
    <div v-if="activeTab === 'triage'" class="tab-content">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3 style="margin-bottom:6px;font-size:.9rem;">🩺 故障分类 · 挑战 3</h3>
        <p style="font-size:.78rem;color:var(--text-secondary);">昨晚的管道失败了。以下是 4 个阶段的日志——找出根因。</p>
      </div>

      <!-- 4 Log panels -->
      <div class="triage-grid">
        <div v-for="(log, idx) in triageLogs" :key="idx" class="card triage-log-card" :class="{ 'triage-root': triageAnswer && idx === triageAnswer.rootStage }">
          <div class="triage-log-header">
            <span class="triage-log-icon">{{ log.icon }}</span>
            <span class="triage-log-name">{{ log.name }}</span>
            <span class="triage-log-status" :class="{ passed: log.status === 'passed', failed: log.status === 'failed' }">{{ log.status === 'passed' ? '✅' : '❌' }}</span>
          </div>
          <pre class="triage-log-body">{{ log.output }}</pre>
        </div>
      </div>

      <div class="card" style="margin-top:var(--space-md);" v-if="!triageAnswer">
        <h4 style="font-size:.84rem;margin-bottom:10px;">哪个阶段最先暴露了真正的问题？</h4>
        <div class="triage-options">
          <button v-for="(log, idx) in triageLogs" :key="idx" class="btn-outline triage-opt" @click="checkTriage(idx)">{{ log.icon }} {{ log.name }}</button>
        </div>
      </div>

      <div v-if="triageAnswer" class="card" style="margin-top:var(--space-md);">
        <h4 style="font-size:.84rem;margin-bottom:10px;">根因是什么？</h4>
        <div class="triage-options">
          <button v-for="(cause, idx) in triageCauses" :key="idx" class="btn-outline triage-opt" :class="{ 'triage-chosen': triageCauseChosen === idx, correct: triageCauseChosen === idx && idx === triageAnswer.correctCause, wrong: triageCauseChosen === idx && idx !== triageAnswer.correctCause }" :disabled="triageCauseChosen !== null" @click="checkTriageCause(idx)">{{ cause }}</button>
        </div>
        <div v-if="triageCauseChosen !== null" class="explain" :class="{ 'explain-correct': triageCauseChosen === triageAnswer.correctCause, 'explain-wrong': triageCauseChosen !== triageAnswer.correctCause }" style="margin-top:12px;">
          <strong>{{ triageCauseChosen === triageAnswer.correctCause ? '✅ 正确！' : '❌ 错误。' }}</strong>
          {{ triageAnswer.explanation }}
        </div>
        <button v-if="triageCauseChosen !== null" class="btn-outline" style="margin-top:10px;" @click="resetTriage">🔄 再试一次</button>
      </div>
    </div>

    <!-- ====== TAB 4: Report Dashboard ====== -->
    <div v-if="activeTab === 'report'" class="tab-content">
      <div class="card" style="margin-bottom:var(--space-md);text-align:center;" v-if="!reportData">
        <div style="padding:32px;color:var(--text-muted);">
          <span style="font-size:3rem;display:block;margin-bottom:12px;">📊</span>
          <p>先在「管道构建器」中运行一次管道，即可查看测试报告仪表板。</p>
        </div>
      </div>

      <template v-if="reportData">
        <!-- Pass Rate Trend -->
        <div class="card" style="margin-bottom:var(--space-md);">
          <h3 style="margin-bottom:10px;font-size:.9rem;">📈 通过率趋势（最近 10 次）</h3>
          <div class="trend-chart">
            <div class="trend-bar-wrap" v-for="(p, i) in reportData.passRateTrend" :key="i">
              <div class="trend-bar" :style="{ height: p + '%' }" :title="'Run #' + (i + 1) + ': ' + p + '%'">
                <span class="trend-bar-label">{{ p }}%</span>
              </div>
              <span class="trend-run-label">#{{ i + 1 }}</span>
            </div>
          </div>
          <!-- SVG line -->
          <svg class="trend-svg" viewBox="0 0 500 120">
            <polyline :points="trendLinePts" fill="none" stroke="var(--primary)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
            <polygon :points="trendAreaPts" fill="url(#trendGrad)" opacity="0.3" />
            <defs>
              <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="var(--primary)" stop-opacity="0.4" />
                <stop offset="100%" stop-color="var(--primary)" stop-opacity="0.05" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <div class="report-grid">
          <!-- Top 5 Slowest -->
          <div class="card">
            <h3 style="margin-bottom:10px;font-size:.9rem;">🐢 最慢的 5 个测试</h3>
            <div class="slow-bar-list">
              <div v-for="(t, i) in reportData.slowestTests" :key="i" class="slow-bar-row">
                <span class="slow-bar-name">{{ t.name }}</span>
                <div class="slow-bar-track"><div class="slow-bar-fill" :style="{ width: (t.duration / reportData.maxDuration * 100) + '%' }"></div></div>
                <span class="slow-bar-time">{{ t.duration }}s</span>
              </div>
            </div>
          </div>

          <!-- New vs Existing Failures -->
          <div class="card">
            <h3 style="margin-bottom:10px;font-size:.9rem;">🆕 新失败 vs 已有失败</h3>
            <table class="report-table">
              <thead><tr><th>测试</th><th>本次</th><th>上次</th><th>类型</th></tr></thead>
              <tbody>
                <tr v-for="(r, i) in reportData.failures" :key="i">
                  <td class="rt-name">{{ r.name }}</td>
                  <td :class="{ 'r-fail': true }">❌</td>
                  <td>{{ r.prevRun }}</td>
                  <td><span class="tag" :class="r.isNew ? 'tag-danger' : 'tag-warning'">{{ r.isNew ? 'NEW' : '已有' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Flaky Candidates -->
          <div class="card" style="grid-column: 1 / -1;">
            <h3 style="margin-bottom:10px;font-size:.9rem;">⚠️ Flaky 候选（通过率 50%-95%）</h3>
            <table class="report-table">
              <thead><tr><th>测试</th><th>通过率</th><th>最近 10 次</th><th>建议</th></tr></thead>
              <tbody>
                <tr v-for="(c, i) in reportData.flakyCandidates" :key="i">
                  <td class="rt-name">{{ c.name }}</td>
                  <td><span class="tag tag-warning">{{ c.passRate }}%</span></td>
                  <td class="rt-history">
                    <span v-for="(r, ri) in c.history" :key="ri" :class="{ pass: r, fail: !r }">{{ r ? '✓' : '✗' }}</span>
                  </td>
                  <td style="font-size:.74rem;color:var(--text-secondary);">{{ c.recommendation }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onBeforeUnmount } from 'vue'

// ==================== Tabs ====================
const tabs = [
  { id: 'builder', label: '管道构建器', icon: '🔧' },
  { id: 'flaky', label: 'Flaky检测', icon: '🔍' },
  { id: 'triage', label: '故障分类', icon: '🩺' },
  { id: 'report', label: '测试报告', icon: '📊' },
]
const activeTab = ref('builder')

// ==================== Pipeline Builder ====================
const availableStages = [
  { id: 'lint', name: 'Lint', icon: '🟢', duration: '30s', color: '#10b981', baseSec: 30, canFail: false },
  { id: 'unit', name: 'Unit Tests', icon: '🟡', duration: '2min', color: '#f59e0b', baseSec: 120, tests: 50 },
  { id: 'integration', name: 'Integration Tests', icon: '🟠', duration: '5min', color: '#f97316', baseSec: 300, tests: 20 },
  { id: 'e2e', name: 'E2E Tests', icon: '🔴', duration: '15min', color: '#ef4444', baseSec: 900, tests: 10 },
  { id: 'security', name: 'Security Scan', icon: '🔵', duration: '3min', color: '#3b82f6', baseSec: 180 },
  { id: 'build', name: 'Build', icon: '⚪', duration: '2min', color: '#9ca3af', baseSec: 120 },
  { id: 'deploy-staging', name: 'Deploy Staging', icon: '🟣', duration: '4min', color: '#8b5cf6', baseSec: 240 },
  { id: 'deploy-prod', name: 'Deploy Prod', icon: '🟤', duration: 'manual', color: '#78716c', baseSec: 0, manualGate: true },
]

const pipelineStages = ref([])
const isRunning = ref(false)
const pipelineSummary = ref(null)
const activeIntervals = []

function addStage(stageDef) {
  if (pipelineStages.value.find(s => s.id === stageDef.id)) return
  pipelineStages.value.push({
    ...stageDef,
    workers: stageDef.id === 'unit' ? 3 : (stageDef.id === 'integration' ? 2 : 1),
    timeout: stageDef.baseSec * 2 || 120,
    retries: 0,
    status: 'waiting',
    elapsed: 0,
    progress: 0,
    retriesUsed: 0,
  })
  pipelineSummary.value = null
}

function removeStage(idx) {
  pipelineStages.value.splice(idx, 1)
  pipelineSummary.value = null
}

function clearPipeline() {
  if (isRunning.value) return
  pipelineStages.value = []
  pipelineSummary.value = null
}

function getStageStatusClass(stage) {
  if (stage.status === 'running') return 'stage-running'
  if (stage.status === 'flaky') return 'stage-flaky'
  if (stage.status === 'passed') return 'stage-passed'
  if (stage.status === 'failed') return 'stage-failed'
  return 'stage-waiting'
}

const pipelineTotalTime = computed(() => {
  if (pipelineStages.value.length === 0) return ''
  let total = 0
  for (const s of pipelineStages.value) {
    if (s.manualGate) continue
    const effective = s.id === 'e2e' ? s.baseSec : Math.ceil(s.baseSec / s.workers)
    total += effective
  }
  total += pipelineStages.value.filter(s => s.id === 'deploy-prod').length * 300
  const m = Math.floor(total / 60)
  const sec = total % 60
  return m + ':' + String(sec).padStart(2, '0')
})

const exportFormat = ref('github')
const exportedYaml = ref('')
const copyMsg = ref('')

// Generate fake report data after run
const reportData = ref(null)

function generateFakeReport(stages) {
  const passRates = [85, 80, 78, 82, 88, 75, 85, 80, 90, 95]
  const trend = [85, 82, 78, 80, 88, 75, 85, 80, 90, passRates[9]]
  return {
    passRateTrend: trend,
    slowestTests: [
      { name: 'E2E_CheckoutFlow.test.js', duration: 245 },
      { name: 'Integration_PaymentAPI.test.js', duration: 182 },
      { name: 'Unit_UserModule.test.js', duration: 95 },
      { name: 'E2E_LoginRedirect.test.js', duration: 88 },
      { name: 'Integration_SearchAPI.test.js', duration: 71 },
    ],
    maxDuration: 245,
    failures: [
      { name: 'Integration_PaymentAPI.test.js', prevRun: '✅', isNew: false },
      { name: 'Unit_UserModule.test.js', prevRun: '✅', isNew: true },
      { name: 'E2E_CheckoutFlow.test.js', prevRun: '❌', isNew: false },
    ],
    flakyCandidates: [
      { name: 'Unit_LoginFlow.test.js', passRate: 80, history: [true, true, false, true, true, true, false, true, true, true], recommendation: '隔离调查：可能有时序依赖' },
      { name: 'Integration_UploadAPI.test.js', passRate: 60, history: [true, false, true, false, true, true, false, true, false, true], recommendation: '检查文件清理竞态条件' },
      { name: 'E2E_ProfileEdit.test.js', passRate: 70, history: [true, true, true, false, true, true, false, true, true, false], recommendation: '等待选择器不稳定，增加显式等待' },
    ],
  }
}

async function runPipeline() {
  isRunning.value = true
  pipelineSummary.value = null
  reportData.value = null
  for (const s of pipelineStages.value) {
    s.status = 'waiting'; s.elapsed = 0; s.progress = 0; s.retriesUsed = 0
  }

  for (const s of pipelineStages.value) {
    if (!isRunning.value) break
    s.status = 'running'
    const effectiveSec = s.manualGate ? 3 : Math.max(Math.ceil(s.baseSec / s.workers), 2)
    const totalTime = effectiveSec * 1000
    const stepMs = 150
    let elapsed = 0
    await new Promise(resolve => {
      const iv = setInterval(() => {
        if (!isRunning.value) { clearInterval(iv); activeIntervals.splice(activeIntervals.indexOf(iv), 1); resolve(); return }
        elapsed += stepMs
        s.elapsed = Math.floor(elapsed / 1000)
        s.progress = Math.min(Math.round(elapsed / totalTime * 100), 100)
        if (elapsed >= totalTime) { clearInterval(iv); activeIntervals.splice(activeIntervals.indexOf(iv), 1); resolve() }
      }, stepMs)
      activeIntervals.push(iv)
    })
    if (!isRunning.value) break

    // Simulate pass/fail
    let passed = true
    if (s.id === 'e2e' && s.retries === 0 && s.workers <= 1) passed = Math.random() > 0.3
    else if (s.id === 'integration' && s.retries === 0) passed = Math.random() > 0.15
    else passed = s.canFail === false ? true : Math.random() > 0.05

    if (!passed && s.retries > 0) {
      s.retriesUsed++
      await new Promise(resolve => setTimeout(resolve, 800))
      passed = Math.random() > 0.3
      if (!passed && s.retries > 1) {
        s.retriesUsed++
        await new Promise(resolve => setTimeout(resolve, 800))
        passed = Math.random() > 0.3
      }
      if (!passed && s.retries > 2) {
        s.retriesUsed++
        await new Promise(resolve => setTimeout(resolve, 800))
        passed = Math.random() > 0.3
      }
    }

    s.status = passed ? 'passed' : 'failed'
    if (passed && s.retriesUsed > 0) s.status = 'flaky'
    s.progress = 100
  }

  isRunning.value = false
  const passed = pipelineStages.value.filter(s => s.status === 'passed' || s.status === 'flaky').length
  const flakyCount = pipelineStages.value.filter(s => s.status === 'flaky').length
  const failedStage = pipelineStages.value.find(s => s.status === 'failed')
  const totalSec = pipelineStages.value.reduce((acc, s) => acc + (s.manualGate ? 0 : Math.ceil(s.baseSec / s.workers)), 0)
  const m = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  pipelineSummary.value = {
    text: `管道完成于 ${m}:${String(sec).padStart(2, '0')} | ${passed}/${pipelineStages.value.length} 阶段通过 | ${flakyCount} 测试 flaky${failedStage ? ' | ' + failedStage.name + ' 阶段失败' : ''}`,
    failed: !!failedStage,
  }
  reportData.value = generateFakeReport(pipelineStages.value)
}

function stopPipeline() {
  isRunning.value = false
}

onBeforeUnmount(() => {
  isRunning.value = false
  for (const iv of activeIntervals) {
    clearInterval(iv)
  }
  activeIntervals.length = 0
})

// ==================== Flaky Detection ====================
const flakyTests = [
  {
    name: 'LoginFlow.test.js',
    history: [true, true, false, true, true, true, false, true, true, true],
    passRate: 80, passed: 8,
    correctClass: 'flaky', correctAction: 'quarantine',
    recommendation: '80% 通过率 — Flaky。可能涉及时序或网络依赖，隔离并调查。',
  },
  {
    name: 'CheckoutFlow.test.js',
    history: [true, true, true, true, true, true, true, true, true, true],
    passRate: 100, passed: 10,
    correctClass: 'stable', correctAction: 'keep',
    recommendation: '100% 通过率 — 稳定。无需操作。',
  },
  {
    name: 'PaymentAPI.test.js',
    history: [false, false, false, false, false, false, false, false, false, false],
    passRate: 0, passed: 0,
    correctClass: 'broken', correctAction: 'fix',
    recommendation: '0% 通过率 — 已损坏。检查 API 端点是否变更或环境配置是否正确。',
  },
  {
    name: 'SearchResults.test.js',
    history: [true, true, true, true, true, true, true, true, true, false],
    passRate: 90, passed: 9,
    correctClass: 'stable', correctAction: 'keep',
    recommendation: '90% 通过率 — 基本稳定。仅一次失败可能是临时环境问题，监控即可。',
  },
  {
    name: 'UploadAPI.test.js',
    history: [true, false, true, false, true, true, false, true, false, true],
    passRate: 60, passed: 6,
    correctClass: 'flaky', correctAction: 'quarantine',
    recommendation: '60% 通过率 — Flaky。可能文件清理/竞态条件。隔离调查。',
  },
  {
    name: 'UserProfile.test.js',
    history: [true, true, false, true, true, false, true, true, false, true],
    passRate: 70, passed: 7,
    correctClass: 'flaky', correctAction: 'quarantine',
    recommendation: '70% 通过率 — Flaky。检查是否有异步状态依赖未正确等待。',
  },
  {
    name: 'Navigation.test.js',
    history: [true, true, true, true, true, true, true, true, true, true],
    passRate: 100, passed: 10,
    correctClass: 'stable', correctAction: 'keep',
    recommendation: '100% 通过率 — 稳定。无需操作。',
  },
  {
    name: 'ExportCSV.test.js',
    history: [false, false, false, true, false, false, false, false, false, false],
    passRate: 10, passed: 1,
    correctClass: 'broken', correctAction: 'fix',
    recommendation: '10% 通过率 — 已损坏。很可能是依赖的导出库版本更新导致接口变更。',
  },
]

const classifications = [
  { value: 'stable', label: '✓ 稳定' },
  { value: 'flaky', label: '⚠ Flaky' },
  { value: 'broken', label: '✗ 已损坏' },
]
const actions = [
  { value: 'keep', label: '保持' },
  { value: 'quarantine', label: '隔离调查' },
  { value: 'fix', label: '立即修复' },
  { value: 'delete', label: '删除' },
]

const flakyAnalysis = reactive(flakyTests.map(t => ({
  classification: null,
  action: null,
  correctClass: t.correctClass,
  correctAction: t.correctAction,
  recommendation: t.recommendation,
})))

const flakyScore = ref(null)
const flakyCorrectCount = ref(0)
const flakyActionCount = ref(0)

// Watch for all submitted
function checkAllSubmitted() {
  const allDone = flakyAnalysis.every(a => a.action !== null)
  if (allDone) {
    flakyCorrectCount.value = flakyAnalysis.filter((a, i) => a.classification === flakyTests[i].correctClass).length
    flakyActionCount.value = flakyAnalysis.filter((a, i) => a.action === flakyTests[i].correctAction).length
    flakyScore.value = flakyCorrectCount.value + flakyActionCount.value
  } else {
    flakyScore.value = null
  }
}

// We can't watch reactive array deeply easily, expose a submit button
const flakyAllSubmitted = computed(() => flakyAnalysis.every(a => a.action !== null))

function resetFlaky() {
  for (const a of flakyAnalysis) {
    a.classification = null
    a.action = null
  }
  flakyScore.value = null
  flakyCorrectCount.value = 0
  flakyActionCount.value = 0
}

function getRateColor(rate) {
  if (rate >= 95) return 'var(--success)'
  if (rate >= 50) return 'var(--warning)'
  return 'var(--danger)'
}

function classLabel(v) {
  const map = { stable: '稳定', flaky: 'Flaky', broken: '已损坏' }
  return map[v] || v
}
function actionLabel(v) {
  const map = { keep: '保持', quarantine: '隔离调查', fix: '立即修复', delete: '删除' }
  return map[v] || v
}

// ==================== Challenge 2: Flaky Hunt ====================
function generateHuntTests() {
  const names = [
    'AuthService.test.js', 'CartModule.test.js', 'OrderAPI.test.js', 'Inventory.test.js',
    'ShippingCalc.test.js', 'DiscountEngine.test.js', 'EmailNotify.test.js', 'SMSService.test.js',
    'PDFGenerator.test.js', 'ImageResizer.test.js', 'CacheManager.test.js', 'RateLimiter.test.js',
    'WebhookHandler.test.js', 'SessionStore.test.js', 'TokenRefresh.test.js', 'AuditLog.test.js',
    'GeoIPLookup.test.js', 'TaxCalculator.test.js', 'CurrencyConvert.test.js', 'FraudDetect.test.js',
    'UserRegister.test.js', 'PasswordReset.test.js', 'OTPVerify.test.js', 'KYCUpload.test.js',
    'ReportBuilder.test.js', 'DataExporter.test.js', 'BatchScheduler.test.js', 'QueueWorker.test.js',
    'DeadLetter.test.js', 'RetryPolicy.test.js', 'CircuitBreaker.test.js', 'FeatureFlag.test.js',
    'ConfigLoader.test.js', 'SecretManager.test.js', 'HealthCheck.test.js', 'MetricsCollector.test.js',
    'AlertManager.test.js', 'LogAggregator.test.js', 'TraceSampler.test.js', 'SpanContext.test.js',
    'DBMigration.test.js', 'SchemaValidator.test.js', 'BackupService.test.js', 'RestoreService.test.js',
    'FileScanner.test.js', 'ThumbnailGen.test.js', 'VideoEncoder.test.js', 'AudioTranscode.test.js',
    'SearchIndex.test.js', 'FulltextQuery.test.js',
  ]
  // 3 flaky: indices 7, 23, 41
  const flakyIndices = new Set([7, 23, 41])
  return names.map((name, i) => {
    let history
    if (flakyIndices.has(i)) {
      // Generate intermittent pattern
      const passes = 5 + Math.floor(Math.random() * 3) // 5-7 passes
      history = Array.from({ length: 10 }, (_, j) => j < passes)
      // Shuffle
      for (let k = history.length - 1; k > 0; k--) {
        const l = Math.floor(Math.random() * (k + 1));
        [history[k], history[l]] = [history[l], history[k]]
      }
    } else {
      // Stable: all pass
      history = Array(10).fill(true)
    }
    return { name, history, isFlaky: flakyIndices.has(i) }
  })
}

const huntTests = ref(generateHuntTests())
const huntSelections = ref(huntTests.value.map(() => false))
const huntSubmitted = ref(false)
const huntScore = ref({ precision: 0, recall: 0, f1: 0, tp: 0, fp: 0, fn: 0 })

function submitHunt() {
  let tp = 0, fp = 0, fn = 0
  for (let i = 0; i < huntTests.value.length; i++) {
    const selected = huntSelections.value[i]
    const isFlaky = huntTests.value[i].isFlaky
    if (selected && isFlaky) tp++
    else if (selected && !isFlaky) fp++
    else if (!selected && isFlaky) fn++
  }
  const precision = tp / (tp + fp) || 0
  const recall = tp / (tp + fn) || 0
  const f1 = (precision + recall) > 0 ? 2 * precision * recall / (precision + recall) : 0
  huntScore.value = { precision, recall, f1: Math.round(f1 * 100) / 100, tp, fp, fn }
  huntSubmitted.value = true
}

// ==================== Challenge 3: Failure Triage ====================
const triageLogs = [
  {
    id: 0, icon: '🟢', name: 'Lint', status: 'passed',
    output: '> npm run lint\n\nAll files passed linting.\n✅ 0 errors, 0 warnings\n\nDone in 12.34s.',
  },
  {
    id: 1, icon: '🟡', name: 'Unit Tests', status: 'failed',
    output: '> npm test -- --shard=1/3\n\nPASS UserModule.test.js (48 tests)\nFAIL UserModule_profile.test.js\n  ✗ should update avatar URL (timeout)\nFAIL UserModule_settings.test.js\n  ✗ should save preferences correctly\n\n48/50 passed. 2 failed.',
  },
  {
    id: 2, icon: '🟠', name: 'Integration Tests', status: 'failed',
    output: '> npm run test:integration\n\nFAIL PaymentAPI.test.js\n  Error: connect ECONNREFUSED 127.0.0.1:9090\nFAIL CheckoutFlow.test.js\n  Error: connect ECONNREFUSED 127.0.0.1:9090\nFAIL RefundProcess.test.js\n  Error: connect ECONNREFUSED 127.0.0.1:9090\n\nAll integration tests failed — cannot reach payment-mock service.',
  },
  {
    id: 3, icon: '🔴', name: 'E2E Tests', status: 'failed',
    output: '> npm run test:e2e\n\nFAIL CheckoutJourney.e2e.js\n  Timeout waiting for .checkout-button (30000ms)\nFAIL PaymentGateway.e2e.js\n  Timeout waiting for #card-number iframe\n\n2/10 passed. 8 failed with timeout.',
  },
]

const triageAnswer = ref(null)
const triageCauseChosen = ref(null)
const triageCauses = [
  'Lint 规则配置错误',
  '两个 Unit Test 用例写错了断言',
  'payment-mock 服务未启动（连接被拒）',
  'E2E 测试的选择器过期了',
  '代码有 bug 导致所有测试失败',
]

function checkTriage(idx) {
  triageAnswer.value = {
    rootStage: 2,
    correctCause: 2,
    explanation: 'Integration Tests 最先暴露了真正的问题：payment-mock 服务未启动导致 Connection Refused。这级联致 E2E 全部超时。两个 Unit Test 失败与 UserModule 相关，与支付无关——是独立的、已存在的问题。修复方案：重启 payment-mock 服务（docker-compose up -d payment-mock），然后重新运行管道。',
  }
}

function checkTriageCause(idx) {
  triageCauseChosen.value = idx
}

function resetTriage() {
  triageAnswer.value = null
  triageCauseChosen.value = null
}

// ==================== Challenge 1: Speed Optimization ====================
const ch1Open = ref(false)
const ch1Result = ref(null)
const ch2Open = ref(false)

function loadChallenge1() {
  clearPipeline()
  const stageDefs = ['lint', 'unit', 'integration', 'e2e', 'security']
  for (const id of stageDefs) {
    const def = availableStages.find(s => s.id === id)
    if (def) addStage(def)
  }
  ch1Result.value = {
    text: '已加载 5 个强制阶段（预估 45 分钟）。增加 Unit Tests Workers 至 5、Integration Tests Workers 至 4 可将时间压缩至 ~20 分钟。试试看！',
    win: false,
  }
  // Watch for achievement
  setTimeout(() => {
    const total = pipelineStages.value.reduce((acc, s) => acc + (s.manualGate ? 0 : Math.ceil(s.baseSec / s.workers)), 0)
    if (total <= 900) {
      ch1Result.value = { text: '🎉 太棒了！管道已优化至 15 分钟以内！增加并行是关键策略。', win: true }
    } else if (total <= 1200) {
      ch1Result.value = { text: '👍 接近了！管道约 20 分钟。再增加 Integration Tests 的 Workers 或减少不必要的重试。', win: false }
    }
  }, 300)
}

// ==================== Export ====================
function generateExport() {
  const stages = pipelineStages.value
  if (!stages.length) { exportedYaml.value = ''; return }
  if (exportFormat.value === 'github') {
    let yaml = 'name: QA Pipeline\non: [push]\njobs:\n'
    let prevJob = null
    for (const s of stages) {
      const jobId = s.id
      const needs = prevJob ? `\n    needs: ${prevJob}` : ''
      if (s.workers > 1 && !s.manualGate) {
        const mtxShard = '\\${{ matrix.shard }}'
        yaml += `  ${jobId}:${needs}\n    strategy:\n      matrix:\n        shard: [${Array.from({ length: s.workers }, (_, i) => i + 1).join(',')}]\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: echo "Running ${s.name} shard ${mtxShard}/${s.workers}"\n`
      } else if (s.manualGate) {
        yaml += `  ${jobId}:${needs}\n    runs-on: ubuntu-latest\n    environment: production\n    steps:\n      - run: echo "Manual approval required for ${s.name}"\n`
      } else {
        yaml += `  ${jobId}:${needs}\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: echo "Running ${s.name}"\n`
      }
      prevJob = jobId
    }
    exportedYaml.value = yaml
  } else if (exportFormat.value === 'jenkins') {
    let yaml = 'pipeline {\n    agent any\n    stages {\n'
    for (const s of stages) {
      if (s.workers > 1 && !s.manualGate) {
        yaml += `        stage('${s.name}') {\n            steps {\n                script {\n                    parallel (\n${Array.from({ length: s.workers }, (_, i) => `                        "shard-${i + 1}": { sh "echo Running shard ${i + 1}/${s.workers}" }`).join(',\n')}\n                    )\n                }\n            }\n        }\n`
      } else if (s.manualGate) {
        yaml += `        stage('${s.name}') {\n            steps {\n                input message: 'Approve deployment to Production?'\n                sh 'echo Deploying...'\n            }\n        }\n`
      } else {
        yaml += `        stage('${s.name}') {\n            steps {\n                sh 'echo Running ${s.name}'\n            }\n        }\n`
      }
    }
    yaml += '    }\n}'
    exportedYaml.value = yaml
  } else if (exportFormat.value === 'gitlab') {
    let yaml = 'stages:\n'
    for (const s of stages) {
      yaml += `  - ${s.id}\n`
    }
    for (const s of stages) {
      if (s.workers > 1 && !s.manualGate) {
        yaml += `\n${s.id}:\n  stage: ${s.id}\n  parallel: ${s.workers}\n  script:\n    - echo "Running ${s.name}"\n`
      } else if (s.manualGate) {
        yaml += `\n${s.id}:\n  stage: ${s.id}\n  when: manual\n  script:\n    - echo "Deploying to production..."\n`
      } else {
        yaml += `\n${s.id}:\n  stage: ${s.id}\n  script:\n    - echo "Running ${s.name}"\n`
      }
    }
    exportedYaml.value = yaml
  }
}

function copyExport() {
  navigator.clipboard.writeText(exportedYaml.value).then(() => {
    copyMsg.value = '已复制！'
    setTimeout(() => { copyMsg.value = '' }, 2000)
  }).catch(() => {
    copyMsg.value = '复制失败，请手动选择'
  })
}

// ==================== Report dashboard trends ====================
const trendLinePts = computed(() => {
  if (!reportData.value) return ''
  const vals = reportData.value.passRateTrend
  const w = 500
  const h = 120
  const pad = 10
  const max = 100
  const min = 60
  const xStep = (w - 2 * pad) / Math.max(vals.length - 1, 1)
  return vals.map((v, i) => `${pad + i * xStep},${h - pad - ((v - min) / (max - min)) * (h - 2 * pad)}`).join(' ')
})

const trendAreaPts = computed(() => {
  if (!reportData.value) return ''
  const vals = reportData.value.passRateTrend
  const w = 500
  const h = 120
  const pad = 10
  const max = 100
  const min = 60
  const xStep = (w - 2 * pad) / Math.max(vals.length - 1, 1)
  const pts = vals.map((v, i) => `${pad + i * xStep},${h - pad - ((v - min) / (max - min)) * (h - 2 * pad)}`).join(' ')
  return `10,${h - pad} ${pts} ${w - pad},${h - pad}`
})
</script>

<style scoped>
/* ==================== Layout ==================== */
.lab-page { max-width: 1100px; margin: 0 auto; }
.breadcrumb a { color: var(--primary); text-decoration: none; }
.breadcrumb a:hover { text-decoration: underline; }

/* ==================== Tabs ==================== */
.tabs-bar { display: flex; gap: 4px; margin-bottom: var(--space-lg); border-bottom: 1px solid var(--border); padding-bottom: 0; }
.tab-btn {
  padding: 8px 18px; border: none; background: transparent;
  font-size: .84rem; font-weight: 500; font-family: var(--font-sans);
  color: var(--text-secondary); cursor: pointer; border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: all var(--fast); border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.tab-btn:hover { color: var(--text); background: var(--surface-hover); }
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }

/* ==================== Stage Picker ==================== */
.stage-picker { display: flex; gap: 6px; flex-wrap: wrap; }
.stage-chip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 6px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); font-size: .78rem; font-family: var(--font-sans);
  cursor: pointer; transition: all var(--fast); color: var(--text);
}
.stage-chip:hover:not(:disabled) { border-color: var(--primary); background: var(--primary-light); }
.stage-chip.used { opacity: .4; cursor: not-allowed; background: var(--bg-subtle); }
.chip-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }

/* ==================== Pipeline Canvas ==================== */
.pipeline-canvas { display: flex; flex-direction: column; align-items: center; }

.pipeline-stage {
  background: var(--surface); border: 1px solid var(--border);
  border-left: 4px solid var(--border); border-radius: var(--radius);
  padding: 14px 18px; width: 100%; max-width: 640px; min-width: 320px;
  transition: all var(--normal); box-shadow: var(--shadow-xs);
  position: relative;
}
.pipeline-stage.stage-running {
  border-left-color: var(--primary) !important;
  box-shadow: 0 0 0 3px var(--primary-light), var(--shadow);
  animation: pulse-border 1.5s ease-in-out infinite;
}
@keyframes pulse-border {
  0%, 100% { box-shadow: 0 0 0 2px var(--primary-light), var(--shadow); }
  50% { box-shadow: 0 0 0 6px rgba(99,102,241,.1), var(--shadow); }
}
.pipeline-stage.stage-passed { border-left-color: var(--success) !important; background: var(--success-light); }
.pipeline-stage.stage-flaky { border-left-color: var(--warning) !important; background: var(--warning-light); }
.pipeline-stage.stage-failed { border-left-color: var(--danger) !important; background: var(--danger-light); }
.pipeline-stage.stage-waiting { opacity: .7; }

.stage-header { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.stage-icon { font-size: 1.1rem; }
.stage-name { font-weight: 600; font-size: .86rem; flex: 1; min-width: 100px; }
.stage-time { font-size: .72rem; color: var(--text-muted); font-family: var(--font-mono); }
.stage-elapsed { font-size: .72rem; color: var(--primary); font-family: var(--font-mono); font-weight: 600; animation: blink 1s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }
.stage-retries-tag { font-size: .68rem; color: var(--warning); background: var(--warning-light); padding: 1px 8px; border-radius: var(--radius-full); }
.stage-fail-icon, .stage-pass-icon, .stage-flaky-icon { font-size: 1rem; }
.stage-remove {
  border: none; background: none; cursor: pointer; color: var(--text-muted);
  font-size: .82rem; padding: 2px 6px; border-radius: 4px; transition: all var(--fast);
}
.stage-remove:hover { color: var(--danger); background: var(--danger-light); }

.stage-progress-track { height: 4px; background: var(--border-light); border-radius: 2px; margin-top: 10px; overflow: hidden; }
.stage-progress-fill { height: 100%; background: var(--primary); border-radius: 2px; transition: width .3s linear; }

.worker-shards { display: flex; gap: 4px; margin-top: 10px; }
.worker-shard {
  flex: 1; text-align: center; font-size: .68rem; padding: 3px 6px;
  border-radius: 4px; background: var(--border-light); color: var(--text-muted);
  font-family: var(--font-mono);
}
.worker-shard.shard-running { background: var(--primary-light); color: var(--primary); font-weight: 600; }
.worker-shard.shard-passed { background: var(--success-light); color: var(--success); }
.worker-shard.shard-failed { background: var(--danger-light); color: var(--danger); }

.stage-config { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-light); }
.config-row { display: flex; gap: 16px; flex-wrap: wrap; }
.config-label { font-size: .72rem; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; }
.config-label strong { color: var(--text); font-family: var(--font-mono); min-width: 28px; }
.inline-slider { width: 64px; height: 4px; cursor: pointer; accent-color: var(--primary); }

/* ==================== Connector ==================== */
.pipeline-connector { display: flex; flex-direction: column; align-items: center; padding: 2px 0; }
.connector-line { width: 2px; height: 20px; background: var(--border); }
.connector-arrow { font-size: .6rem; color: var(--border); line-height: 1; }

/* ==================== Summary ==================== */
.total-time { font-size: .78rem; color: var(--text-secondary); font-family: var(--font-mono); }
.running-indicator { font-size: .78rem; color: var(--success); font-weight: 600; animation: blink 1s step-end infinite; }
.summary-bar {
  margin-top: var(--space-md); padding: 12px 18px; border-radius: var(--radius);
  background: var(--success-light); color: var(--success); font-size: .82rem; font-weight: 600;
  text-align: center;
}
.summary-bar.summary-failed { background: var(--danger-light); color: var(--danger); }

/* ==================== Export ==================== */
.export-code {
  background: #1a1a2e; color: #e5e7eb; padding: 16px; border-radius: var(--radius);
  font-family: var(--font-mono); font-size: .72rem; line-height: 1.7; overflow-x: auto;
  margin-top: 10px; max-height: 400px; overflow-y: auto; white-space: pre;
}
.copy-msg { font-size: .74rem; color: var(--success); margin-left: 8px; }

/* ==================== Flaky Detection ==================== */
.flaky-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 700px) { .flaky-grid { grid-template-columns: 1fr; } }

.flaky-card { transition: all var(--fast); }
.flaky-card.flaky-selected { border-color: var(--primary); }
.flaky-test-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.flaky-test-name { font-weight: 600; font-size: .82rem; font-family: var(--font-mono); }
.flaky-test-rate { font-weight: 700; font-size: .9rem; font-family: var(--font-mono); }
.flaky-history { display: flex; gap: 3px; flex-wrap: wrap; }
.flaky-dot {
  width: 22px; height: 22px; display: flex; align-items: center; justify-content: center;
  border-radius: 4px; font-size: .68rem; font-family: var(--font-mono);
}
.flaky-dot.pass { background: var(--success-light); color: var(--success); }
.flaky-dot.fail { background: var(--danger-light); color: var(--danger); }

.flaky-actions { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border-light); }
.flaky-label { font-size: .72rem; color: var(--text-secondary); display: block; margin-bottom: 3px; }
.flaky-radios { display: flex; gap: 8px; flex-wrap: wrap; }
.radio-item { font-size: .72rem; display: flex; align-items: center; gap: 4px; cursor: pointer; color: var(--text); }

.flaky-reveal { margin-top: 8px; padding: 10px; border-radius: var(--radius-sm); background: var(--bg-subtle); }
.reveal-correct { color: var(--success); font-weight: 700; font-size: .8rem; margin-bottom: 4px; }
.reveal-wrong { color: var(--danger); font-weight: 700; font-size: .8rem; margin-bottom: 4px; }
.reveal-reason { font-size: .74rem; color: var(--text-secondary); line-height: 1.5; }

/* ==================== Triage ==================== */
.triage-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 700px) { .triage-grid { grid-template-columns: 1fr; } }

.triage-log-card { padding: 14px; }
.triage-log-card.triage-root { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.triage-log-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.triage-log-icon { font-size: 1.2rem; }
.triage-log-name { font-weight: 600; font-size: .82rem; flex: 1; }
.triage-log-status { font-size: 1rem; }
.triage-log-body {
  font-family: var(--font-mono); font-size: .68rem; line-height: 1.6;
  background: #1a1a2e; color: #e5e7eb; padding: 10px; border-radius: var(--radius-sm);
  overflow-x: auto; white-space: pre-wrap; max-height: 220px; overflow-y: auto;
  margin: 0;
}
.triage-options { display: flex; gap: 8px; flex-wrap: wrap; }
.triage-opt { font-size: .82rem; }
.triage-opt.correct { border-color: var(--success); background: var(--success-light); color: var(--success); }
.triage-opt.wrong { border-color: var(--danger); background: var(--danger-light); color: var(--danger); }
.triage-opt.triage-chosen { font-weight: 700; }

.explain { padding: 12px 16px; border-radius: var(--radius); font-size: .8rem; line-height: 1.6; }
.explain-correct { background: var(--success-light); color: var(--success); }
.explain-wrong { background: var(--danger-light); color: var(--danger); }

/* ==================== Challenge Card ==================== */
.challenge-card { border: 1px dashed var(--warning); background: var(--warning-light); }
.challenge-header { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.challenge-result { margin-top: 10px; padding: 12px; border-radius: var(--radius-sm); background: var(--bg-subtle); font-size: .8rem; line-height: 1.6; }
.challenge-result.win { background: var(--success-light); color: var(--success); font-weight: 600; }

/* ==================== Hunt Table ==================== */
.hunt-table-wrap { max-height: 360px; overflow-y: auto; border: 1px solid var(--border); border-radius: var(--radius-sm); }
.hunt-table { width: 100%; border-collapse: collapse; font-size: .74rem; }
.hunt-table th { position: sticky; top: 0; background: var(--surface); padding: 8px 10px; text-align: left; font-size: .7rem; color: var(--text-secondary); border-bottom: 1px solid var(--border); }
.hunt-table td { padding: 6px 10px; border-bottom: 1px solid var(--border-light); }
.hunt-table tr.hunt-flagged { background: var(--warning-light); }
.hunt-name { font-family: var(--font-mono); font-size: .72rem; }
.hunt-pattern { font-family: var(--font-mono); font-size: .7rem; letter-spacing: 2px; }
.hunt-pattern .pass { color: var(--success); }
.hunt-pattern .fail { color: var(--danger); }

/* ==================== Report Dashboard ==================== */
.report-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 700px) { .report-grid { grid-template-columns: 1fr; } }

.trend-chart { display: flex; align-items: flex-end; gap: 6px; height: 120px; padding: 0 10px; }
.trend-bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.trend-bar {
  width: 100%; max-width: 36px; background: var(--primary); border-radius: 4px 4px 0 0;
  min-height: 4px; transition: height .4s var(--ease); position: relative;
  display: flex; align-items: flex-start; justify-content: center;
}
.trend-bar-label { font-size: .58rem; color: #fff; padding-top: 2px; font-weight: 600; }
.trend-run-label { font-size: .6rem; color: var(--text-muted); margin-top: 4px; }
.trend-svg { width: 100%; height: 120px; }

.slow-bar-list { display: flex; flex-direction: column; gap: 8px; }
.slow-bar-row { display: flex; align-items: center; gap: 8px; }
.slow-bar-name { width: 140px; font-size: .68rem; font-family: var(--font-mono); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-secondary); }
.slow-bar-track { flex: 1; height: 12px; background: var(--border-light); border-radius: 6px; overflow: hidden; }
.slow-bar-fill { height: 100%; background: linear-gradient(90deg, var(--warning), #f97316); border-radius: 6px; transition: width .4s var(--ease); }
.slow-bar-time { width: 40px; font-size: .7rem; font-family: var(--font-mono); color: var(--text); text-align: right; }

.report-table { width: 100%; border-collapse: collapse; font-size: .72rem; }
.report-table th { padding: 6px 8px; text-align: left; font-size: .68rem; color: var(--text-secondary); border-bottom: 1px solid var(--border); }
.report-table td { padding: 6px 8px; border-bottom: 1px solid var(--border-light); }
.rt-name { font-family: var(--font-mono); font-size: .7rem; }
.rt-history { font-family: var(--font-mono); font-size: .68rem; letter-spacing: 1px; }
.rt-history .pass { color: var(--success); }
.rt-history .fail { color: var(--danger); }
.r-fail { color: var(--danger); }
</style>
