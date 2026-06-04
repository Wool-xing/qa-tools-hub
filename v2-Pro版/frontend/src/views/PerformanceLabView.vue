<template>
  <div class="lab-page">
    <div class="perf-layout">
      <!-- LEFT: Configuration & Script Editor -->
      <div class="perf-left">
        <div class="card" style="margin-bottom:var(--space-md);">
          <div class="template-bar">
            <span class="template-label">📄 模板：</span>
            <button v-for="t in templates" :key="t.id" class="template-btn"
              :class="{ active: activeTemplate === t.id }" @click="applyTemplate(t)">
              {{ t.label }}
            </button>
          </div>

          <textarea v-model="script" class="script-editor" rows="12"
            placeholder="编写 k6 脚本..."
            spellcheck="false"></textarea>

          <div class="slider-group">
            <label class="slider-label">
              <span>👥 虚拟用户数 (VUs): <strong>{{ vus }}</strong></span>
            </label>
            <input type="range" v-model.number="vus" min="1" max="500" class="slider" />
            <span class="slider-range">1 — 500</span>
          </div>

          <div class="slider-group">
            <label class="slider-label">
              <span>⏱️ 持续时间: <strong>{{ duration }}s</strong></span>
            </label>
            <input type="range" v-model.number="duration" min="10" max="600" step="10" class="slider" />
            <span class="slider-range">10s — 600s</span>
          </div>

          <button class="btn-primary btn-run" :disabled="loading || !script.trim()" @click="runTest">
            <span v-if="loading" class="spinner"></span>
            <span>{{ loading ? ' 运行中...' : '▶ 运行测试' }}</span>
          </button>
        </div>
      </div>

      <!-- RIGHT: Results Panel -->
      <div class="perf-right">
        <div v-if="!result && !loading" class="card empty-state">
          <div class="empty-icon">📊</div>
          <p>点击「运行测试」查看负载测试结果</p>
        </div>

        <div v-if="loading" class="card" style="text-align:center;padding:32px;color:var(--text-secondary);">
          ⏳ 模拟负载测试中...
        </div>

        <div v-if="result" class="results-panel">
          <!-- Summary Cards -->
          <div class="stat-grid">
            <div class="stat-card">
              <span class="stat-num">{{ result.total_requests.toLocaleString() }}</span>
              <span class="stat-label">总请求数</span>
            </div>
            <div class="stat-card" :class="result.error_rate > 5 ? 'stat-warn' : 'stat-ok'">
              <span class="stat-num">{{ result.error_rate }}%</span>
              <span class="stat-label">错误率</span>
            </div>
            <div class="stat-card">
              <span class="stat-num">{{ result.throughput.avg_rps }}</span>
              <span class="stat-label">平均 RPS</span>
            </div>
            <div class="stat-card">
              <span class="stat-num">{{ result.latency.p95 }}<span class="stat-unit">ms</span></span>
              <span class="stat-label">P95 延迟</span>
            </div>
          </div>

          <!-- Endpoint info -->
          <div class="card" style="margin-bottom:var(--space-md);padding:12px 16px;">
            <div class="endpoint-info">
              <span class="ep-method" :class="'m-' + result.method">{{ result.method }}</span>
              <code class="ep-path">{{ result.endpoint }}</code>
              <span class="ep-meta">{{ result.vus }} VUs · {{ result.duration_sec }}s</span>
            </div>
          </div>

          <!-- Latency Percentiles -->
          <div class="card" style="margin-bottom:var(--space-md);">
            <h3 class="section-title">⏱️ 延迟分位数 (ms)</h3>
            <div class="latency-bars">
              <div v-for="p in percentiles" :key="p.key" class="latency-row">
                <span class="lat-key">{{ p.label }}</span>
                <div class="lat-bar-track">
                  <div class="lat-bar-fill" :style="{ width: barWidth(p.value) }"></div>
                </div>
                <span class="lat-val">{{ result.latency[p.key] }} ms</span>
              </div>
            </div>
          </div>

          <!-- Throughput Timeline -->
          <div class="card" style="margin-bottom:var(--space-md);">
            <h3 class="section-title">📈 吞吐量时间线 (RPS)</h3>
            <div class="timeline-chart">
              <svg :viewBox="'0 0 ' + chartW + ' 160'" class="chart-svg">
                <!-- Grid lines -->
                <line v-for="y in gridLines" :key="'g'+y" x1="0" :x2="chartW" :y1="y" :y2="y"
                  stroke="var(--border-light)" stroke-width="0.5" />
                <!-- RPS area fill -->
                <polygon :points="areaPoints" fill="var(--primary-light)" stroke="none" />
                <!-- RPS line -->
                <polyline :points="linePoints" fill="none" stroke="var(--primary)" stroke-width="2" />
                <!-- Error line -->
                <polyline :points="errLinePoints" fill="none" stroke="var(--danger)" stroke-width="1" stroke-dasharray="4,3" />
              </svg>
              <div class="chart-legend">
                <span class="legend-item"><span class="legend-dot rps-dot"></span> RPS</span>
                <span class="legend-item"><span class="legend-dot err-dot"></span> 错误数</span>
              </div>
            </div>
          </div>

          <!-- Checks -->
          <div class="card">
            <h3 class="section-title">✅ 检查结果</h3>
            <div class="checks-row">
              <span class="check-badge" :class="i < result.checks_passed ? 'check-pass' : 'check-fail'"
                v-for="i in result.checks_total" :key="i">
                {{ i <= result.checks_passed ? '✅' : '❌' }}
                {{ checkNames[i - 1] }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Educational Section -->
    <details class="edu-details">
      <summary>📖 这些指标是什么意思？</summary>
      <div class="edu-content">
        <div class="edu-grid">
          <div class="edu-card">
            <h4>📊 延迟分位数 (Latency Percentiles)</h4>
            <p><strong>P50 (中位数)：</strong>50% 的请求比这个值快。反映"典型用户体验"。</p>
            <p><strong>P95：</strong>95% 的请求比这个值快。SLA 常用指标——只允许 5% 的请求超过它。</p>
            <p><strong>P99：</strong>99% 的请求比这个值快。捕捉"长尾延迟"——那 1% 最慢的用户在经历什么。</p>
            <p class="edu-tip">💡 平均值会隐藏长尾问题。P95/P99 才是性能测试的核心关注点。</p>
          </div>
          <div class="edu-card">
            <h4>⚡ RPS vs VUs</h4>
            <p><strong>VUs (虚拟用户)：</strong>同时"在线"并发送请求的模拟用户数量。</p>
            <p><strong>RPS (每秒请求数)：</strong>系统实际每秒处理的请求数。这是吞吐量。</p>
            <p class="edu-tip">💡 VUs 增加不意味着 RPS 线性增长——当系统饱和时，延迟上升，RPS 反而可能下降。这就是瓶颈点。</p>
          </div>
          <div class="edu-card">
            <h4>🐌 错误率</h4>
            <p>负载测试中失败请求的百分比。高错误率通常意味着：</p>
            <ul>
              <li>连接池耗尽（数据库 / Redis 连接不够）</li>
              <li>超时（下游服务在高负载下响应变慢）</li>
              <li>资源限制（CPU / 内存 / 文件描述符）</li>
            </ul>
            <p class="edu-tip">💡 目标：生产环境错误率通常应 &lt; 1%。性能测试的目标是找到错误率开始飙升的那个拐点。</p>
          </div>
          <div class="edu-card">
            <h4>📐 吞吐量曲线</h4>
            <p>上面的折线图展示了测试期间 RPS 随时间变化的曲线：</p>
            <ul>
              <li><strong>上升阶段：</strong>VUs 逐步启动，RPS 爬升</li>
              <li><strong>稳态阶段：</strong>全部 VUs 运行，RPS 在均值附近波动</li>
              <li><strong>下降：</strong>如果 RPS 在 VUs 不变的情况下持续走低，说明系统在退化</li>
            </ul>
            <p class="edu-tip">💡 真实的 k6 测试中，你看的是同样的曲线。这个模拟器用对数正态分布生成逼真的延迟数据。</p>
          </div>
        </div>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { labs } from '../api'

const script = ref(`import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  const res = http.get('https://api.example.com/users');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}`);
const vus = ref(20)
const duration = ref(60)
const loading = ref(false)
const result = ref(null)
const activeTemplate = ref('quick')

const templates = [
  {
    id: 'quick',
    label: '快速入门',
    script: `import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  const res = http.get('https://api.example.com/users');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}`,
    vus: 10,
    duration: 30,
  },
  {
    id: 'ramp',
    label: '渐进加压',
    script: `import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const res = http.get('https://api.example.com/products');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}`,
    vus: 100,
    duration: 180,
  },
  {
    id: 'stress',
    label: '压力测试',
    script: `import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '1m', target: 100 },
    { duration: '1m', target: 200 },
    { duration: '2m', target: 200 },
    { duration: '1m', target: 0 },
  ],
};

export default function () {
  const res = http.post('https://api.example.com/orders',
    JSON.stringify({ productId: 1, quantity: 1 }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(res, { 'status is 201': (r) => r.status === 201 });
  sleep(0.5);
}`,
    vus: 200,
    duration: 300,
  },
]

const percentiles = [
  { key: 'min', label: 'Min' },
  { key: 'avg', label: 'Avg' },
  { key: 'p50', label: 'P50' },
  { key: 'p90', label: 'P90' },
  { key: 'p95', label: 'P95' },
  { key: 'p99', label: 'P99' },
  { key: 'max', label: 'Max' },
]

const checkNames = ['HTTP 状态码', '响应体非空', '响应时间 < P95 阈值']

function applyTemplate(t) {
  script.value = t.script
  vus.value = t.vus
  duration.value = t.duration
  activeTemplate.value = t.id
}

async function runTest() {
  loading.value = true
  result.value = null
  try {
    result.value = await labs.performance(script.value, vus.value, duration.value)
  } catch (e) {
    result.value = { ok: false, error: e.message }
  }
  loading.value = false
}

function barWidth(val) {
  if (!result.value) return '0%'
  const maxVal = result.value.latency.max || 1
  return Math.min((val / maxVal) * 100, 100) + '%'
}

// Chart dimensions
const chartW = 580
const chartH = 160

const gridLines = computed(() => {
  const lines = []
  for (let i = 1; i < 4; i++) lines.push((chartH / 4) * i)
  return lines
})

const linePoints = computed(() => {
  if (!result.value || !result.value.per_second) return ''
  const ps = result.value.per_second
  if (ps.length === 0) return ''
  const maxRps = Math.max(...ps.map(s => s.rps), 1)
  const xStep = chartW / Math.max(ps.length - 1, 1)
  return ps.map((s, i) => {
    const x = i * xStep
    const y = chartH - (s.rps / maxRps) * (chartH - 10) - 5
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
})

const areaPoints = computed(() => {
  const pts = linePoints.value
  if (!pts) return ''
  return `0,${chartH} ${pts} ${chartW},${chartH}`
})

const errLinePoints = computed(() => {
  if (!result.value || !result.value.per_second) return ''
  const ps = result.value.per_second
  if (ps.length === 0) return ''
  const maxErr = Math.max(...ps.map(s => s.errors), 1)
  const xStep = chartW / Math.max(ps.length - 1, 1)
  return ps.map((s, i) => {
    const x = i * xStep
    const y = chartH - (s.errors / maxErr) * (chartH - 10) - 5
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
})
</script>

<style scoped>
.lab-page { max-width: 1100px; margin: 0 auto; }

.perf-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
  align-items: start;
}

@media (max-width: 860px) {
  .perf-layout {
    grid-template-columns: 1fr;
  }
}

/* ---- LEFT: Editor ---- */
.template-bar { display: flex; gap: 6px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
.template-label { font-size: .78rem; color: var(--text-muted); margin-right: 4px; }
.template-btn {
  padding: 5px 12px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .74rem; font-family: var(--font-sans);
  transition: all var(--fast); color: var(--text-secondary);
}
.template-btn:hover { border-color: var(--primary); }
.template-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }

.script-editor {
  width: 100%; padding: 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .78rem; line-height: 1.65;
  background: #1a1a2e; color: #e5e7eb; outline: none; resize: vertical;
  tab-size: 2; min-height: 200px;
}
.script-editor:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.slider-group { margin-top: 14px; }
.slider-label { display: block; font-size: .82rem; color: var(--text); margin-bottom: 4px; }
.slider-label strong { color: var(--primary); font-family: var(--font-mono); }
.slider {
  width: 100%; appearance: none; height: 6px; border-radius: 3px;
  background: var(--border-light); outline: none; cursor: pointer;
}
.slider::-webkit-slider-thumb {
  appearance: none; width: 18px; height: 18px; border-radius: 50%;
  background: var(--primary); cursor: pointer; border: 2px solid #fff; box-shadow: 0 1px 3px rgba(0,0,0,.2);
}
.slider::-moz-range-thumb {
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--primary); cursor: pointer; border: 2px solid #fff;
}
.slider-range { font-size: .68rem; color: var(--text-muted); }

.btn-run {
  width: 100%; margin-top: 16px; padding: 12px 20px; font-size: .9rem;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}

/* ---- RIGHT: Results ---- */
.empty-state { text-align: center; padding: 48px 24px; color: var(--text-muted); }
.empty-icon { font-size: 3rem; margin-bottom: 12px; }

.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: var(--space-md); }
.stat-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 16px; text-align: center; box-shadow: var(--shadow-xs);
}
.stat-num { display: block; font-size: 1.5rem; font-weight: 700; font-family: var(--font-mono); color: var(--text-h); }
.stat-unit { font-size: .7rem; color: var(--text-muted); font-weight: 400; margin-left: 2px; }
.stat-label { display: block; font-size: .72rem; color: var(--text-muted); margin-top: 4px; }
.stat-ok .stat-num { color: var(--success); }
.stat-warn .stat-num { color: var(--danger); }

.endpoint-info { display: flex; align-items: center; gap: 10px; }
.ep-method {
  padding: 2px 8px; border-radius: 4px; font-family: var(--font-mono); font-size: .68rem; font-weight: 700;
}
.ep-method.m-GET { background: #dbeafe; color: #1d4ed8; }
.ep-method.m-POST { background: #d1fae5; color: #047857; }
.ep-method.m-PUT { background: #fef3c7; color: #b45309; }
.ep-method.m-DELETE { background: #fee2e2; color: #b91c1c; }
.ep-method.m-PATCH { background: #ede9fe; color: #6d28d9; }
.ep-path { font-size: .78rem; color: var(--text); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ep-meta { font-size: .7rem; color: var(--text-muted); white-space: nowrap; }

.section-title { font-size: .84rem; font-weight: 600; margin-bottom: 12px; }

/* Latency bars */
.latency-bars { display: flex; flex-direction: column; gap: 8px; }
.latency-row { display: flex; align-items: center; gap: 8px; }
.lat-key { width: 36px; font-size: .7rem; font-weight: 600; color: var(--text-secondary); text-align: right; font-family: var(--font-mono); }
.lat-bar-track { flex: 1; height: 14px; background: var(--border-light); border-radius: 7px; overflow: hidden; }
.lat-bar-fill { height: 100%; background: linear-gradient(90deg, var(--primary), #8b5cf6); border-radius: 7px; transition: width .4s ease; min-width: 2px; }
.lat-val { width: 60px; font-size: .74rem; font-family: var(--font-mono); color: var(--text); text-align: right; }

/* Timeline chart */
.timeline-chart { }
.chart-svg { width: 100%; height: 160px; background: var(--bg); border-radius: var(--radius-sm); }
.chart-legend { display: flex; gap: 16px; margin-top: 8px; justify-content: center; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: .72rem; color: var(--text-muted); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
.rps-dot { background: var(--primary); }
.err-dot { background: var(--danger); }

/* Checks */
.checks-row { display: flex; gap: 10px; flex-wrap: wrap; }
.check-badge { padding: 6px 14px; border-radius: var(--radius-sm); font-size: .78rem; font-weight: 500; }
.check-pass { background: var(--success-light); color: #065f46; }
.check-fail { background: var(--danger-light); color: #991b1b; }

/* Educational section */
.edu-details { margin-top: var(--space-xl); cursor: pointer; }
.edu-details summary { font-size: .9rem; font-weight: 600; color: var(--primary); padding: 12px 0; }
.edu-content { margin-top: var(--space-md); }
.edu-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md); }
@media (max-width: 700px) { .edu-grid { grid-template-columns: 1fr; } }
.edu-card {
  background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 18px; text-align: left;
}
.edu-card h4 { font-size: .84rem; font-weight: 600; margin: 0 0 10px; color: var(--text-h); }
.edu-card p { font-size: .78rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px; }
.edu-card ul { padding-left: 18px; margin: 4px 0; }
.edu-card li { font-size: .78rem; color: var(--text-secondary); line-height: 1.55; margin-bottom: 3px; }
.edu-tip { margin-top: 10px; padding: 8px 12px; background: var(--primary-light); border-radius: 6px; font-size: .76rem; color: var(--primary); font-weight: 500; }

/* Spinner */
.spinner {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,.3); border-top-color: #fff;
  border-radius: 50%; animation: spin .6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
