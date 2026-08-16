<template>
  <div class="lab-page">
    <div class="tab-bar">
      <button v-for="t in tabs" :key="t.id" class="tab-btn" :class="{ active: activeTab === t.id }" @click="activeTab = t.id">
        <span class="tab-icon">{{ t.icon }}</span><span class="tab-label">{{ t.label }}</span>
      </button>
    </div>

    <!-- ====== Tab 1: Network Investigator ====== -->
    <div v-if="activeTab === 'network'" class="tab-content">
      <div class="card">
        <h3>网络请求分析</h3>
        <p class="task-desc"><strong>目标：</strong>{{ netScenarios[netIdx].task }}</p>
        <div class="scenario-bar">
          <button v-for="(s,i) in netScenarios" :key="i" class="scenario-btn" :class="{ active: netIdx === i }" @click="switchNet(i)">{{ s.label }}</button>
        </div>

        <div class="waterfall">
          <div class="wf-header"><span class="wf-url-h">资源</span><span class="wf-type-h">类型</span><span class="wf-size-h">大小</span><span class="wf-time-h">时间</span><span class="wf-status-h">状态</span></div>
          <div v-for="(r,i) in netScenarios[netIdx].resources" :key="i" class="wf-row" @click="netExpanded[i]=!netExpanded[i]">
            <span class="wf-url" :title="r.url">{{ r.url }}</span>
            <span class="wf-type" :class="'wf-type-' + r.type">{{ r.type.toUpperCase() }}</span>
            <span class="wf-size">{{ r.size }}</span>
            <div class="wf-bar-wrap"><div class="wf-bar" :class="'wf-bar-' + r.type" :style="{ width: (r.time / maxNetTime) * 100 + '%' }"></div><span class="wf-time">{{ r.time }}ms</span></div>
            <span class="wf-status" :class="r.status >= 400 ? 'wf-err' : r.status >= 300 ? 'wf-redir' : 'wf-ok'">{{ r.status }}</span>
          </div>
          <div v-for="(r,i) in netScenarios[netIdx].resources" :key="'hdr-'+i" v-if="netExpanded[i]" class="wf-headers">
            <div class="wf-hdr-block">
              <div class="wf-hdr-label">📤 Response Headers</div>
              <div v-for="(v,k) in r.respHeaders" :key="k" class="wf-hdr-line"><code>{{ k }}</code>: {{ v }}</div>
            </div>
            <div class="wf-hdr-block">
              <div class="wf-hdr-label">📥 Request Headers</div>
              <div v-for="(v,k) in r.reqHeaders" :key="k" class="wf-hdr-line"><code>{{ k }}</code>: {{ v }}</div>
            </div>
          </div>
        </div>

        <div class="quiz-q" style="margin-top:16px;">{{ netScenarios[netIdx].question }}</div>
        <textarea v-model="netAnswers[netIdx]" class="text-answer" placeholder="写下你的诊断..."></textarea>
        <button v-if="!netSubmitted[netIdx]" class="btn-primary" style="margin-top:8px;" @click="checkNet">提交诊断</button>
        <div v-if="netSubmitted[netIdx]" class="explain">{{ netScore[netIdx] >= 3 ? '✅' : netScore[netIdx] >= 1 ? '⚠️' : '❌' }} 得分: {{ netScore[netIdx] }}/{{ netScenarios[netIdx].keywords.length }} — {{ netScenarios[netIdx].explain }}</div>
      </div>
    </div>

    <!-- ====== Tab 2: Performance Profiler ====== -->
    <div v-if="activeTab === 'perf'" class="tab-content">
      <div class="card">
        <h3>性能火焰图分析</h3>
        <div class="scenario-bar">
          <button v-for="(s,i) in perfScenarios" :key="i" class="scenario-btn" :class="{ active: perfIdx === i }" @click="perfIdx = i; perfChosen = -1; perfResult = null">{{ s.label }}</button>
        </div>

        <div class="perf-stats">
          <div class="perf-stat"><span class="perf-stat-val" :class="perfScenarios[perfIdx].stats.fps < 30 ? 'danger' : 'success'">{{ perfScenarios[perfIdx].stats.fps }}</span><span class="perf-stat-label">FPS</span></div>
          <div class="perf-stat"><span class="perf-stat-val" :class="perfScenarios[perfIdx].stats.lcp > 2500 ? 'danger' : 'success'">{{ perfScenarios[perfIdx].stats.lcp }}ms</span><span class="perf-stat-label">LCP</span></div>
          <div class="perf-stat"><span class="perf-stat-val" :class="perfScenarios[perfIdx].stats.tbt > 200 ? 'danger' : 'success'">{{ perfScenarios[perfIdx].stats.tbt }}ms</span><span class="perf-stat-label">TBT</span></div>
          <div class="perf-stat"><span class="perf-stat-val">{{ perfScenarios[perfIdx].stats.jsHeap }}MB</span><span class="perf-stat-label">JS Heap</span></div>
        </div>

        <div class="flame-chart">
          <div v-for="(f,i) in perfScenarios[perfIdx].flame" :key="i" class="flame-bar" :style="{ marginLeft: f.nest * 18 + 'px', width: (f.dur / maxPerfDur) * 90 + '%', background: f.color || getFlameColor(f.dur) }">
            <span class="flame-label">{{ f.name }}</span><span class="flame-dur">{{ f.dur }}ms</span>
          </div>
        </div>

        <div class="quiz-q" style="margin-top:16px;">{{ perfScenarios[perfIdx].question }}</div>
        <button v-for="(o,i) in perfScenarios[perfIdx].options" :key="i" class="quiz-opt" :class="{ selected: perfChosen===i, correct: perfResult && i===perfScenarios[perfIdx].answer, wrong: perfResult && perfChosen===i && i!==perfScenarios[perfIdx].answer }" :disabled="perfResult !== null" @click="perfChosen=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span><span>{{ o }}</span>
        </button>
        <button v-if="perfResult===null" class="btn-primary" style="margin-top:10px;" :disabled="perfChosen===-1" @click="checkPerf">提交</button>
        <div v-if="perfResult!==null" class="explain">{{ perfResult ? '✅ 正确！' : '❌ 错误。' }} {{ perfScenarios[perfIdx].explain }}</div>
      </div>
    </div>

    <!-- ====== Tab 3: Console Detective ====== -->
    <div v-if="activeTab === 'console'" class="tab-content">
      <div class="card">
        <h3>控制台侦探</h3>
        <div class="scenario-bar">
          <button v-for="(s,i) in conScenarios" :key="i" class="scenario-btn" :class="{ active: conIdx === i }" @click="conIdx = i; conChosen = -1; conResult = null">{{ s.label }}</button>
        </div>

        <div class="console-panel">
          <div class="console-topbar"><span class="console-dot c-red"></span><span class="console-dot c-yellow"></span><span class="console-dot c-green"></span><span class="console-title">DevTools — Console</span></div>
          <div class="console-body">
            <div v-for="(entry,i) in conScenarios[conIdx].entries" :key="i" class="console-line" :class="'con-' + entry.level">
              <span class="con-icon">{{ entry.level === 'error' ? '❌' : entry.level === 'warn' ? '⚠️' : entry.level === 'info' ? 'ℹ️' : '📝' }}</span>
              <span class="con-text">{{ entry.text }}</span>
              <span v-if="entry.src" class="con-src">{{ entry.src }}</span>
            </div>
          </div>
        </div>

        <div class="quiz-q" style="margin-top:14px;">{{ conScenarios[conIdx].question }}</div>
        <button v-for="(o,i) in conScenarios[conIdx].options" :key="i" class="quiz-opt" :class="{ selected: conChosen===i, correct: conResult && i===conScenarios[conIdx].answer, wrong: conResult && conChosen===i && i!==conScenarios[conIdx].answer }" :disabled="conResult !== null" @click="conChosen=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span><span>{{ o }}</span>
        </button>
        <button v-if="conResult===null" class="btn-primary" style="margin-top:10px;" :disabled="conChosen===-1" @click="checkCon">提交</button>
        <div v-if="conResult!==null" class="explain">{{ conResult ? '✅ 正确！' : '❌ 错误。' }} {{ conScenarios[conIdx].explain }}</div>
      </div>
    </div>

    <!-- ====== Tab 4: Coverage Analyzer ====== -->
    <div v-if="activeTab === 'coverage'" class="tab-content">
      <div class="card">
        <h3>代码覆盖率分析</h3>
        <div class="scenario-bar">
          <button v-for="(s,i) in covScenarios" :key="i" class="scenario-btn" :class="{ active: covIdx === i }" @click="covIdx = i; clearCovChecked(); covResult = null">{{ s.label }}</button>
        </div>

        <div class="cov-overview">
          <div class="cov-type">
            <div class="cov-type-header">CSS</div>
            <div class="cov-bar-bg"><div class="cov-bar-fill cov-bar-bad" :style="{ width: covScenarios[covIdx].cssUsed + '%' }"></div></div>
            <div class="cov-stats"><span class="cov-pct">{{ covScenarios[covIdx].cssUsed }}% used</span><span class="cov-pct cov-unused">{{ 100 - covScenarios[covIdx].cssUsed }}% unused</span></div>
            <div class="cov-detail">{{ covScenarios[covIdx].cssDetail }}</div>
          </div>
          <div class="cov-type">
            <div class="cov-type-header">JavaScript</div>
            <div class="cov-bar-bg"><div class="cov-bar-fill cov-bar-bad" :style="{ width: covScenarios[covIdx].jsUsed + '%' }"></div></div>
            <div class="cov-stats"><span class="cov-pct">{{ covScenarios[covIdx].jsUsed }}% used</span><span class="cov-pct cov-unused">{{ 100 - covScenarios[covIdx].jsUsed }}% unused</span></div>
            <div class="cov-detail">{{ covScenarios[covIdx].jsDetail }}</div>
          </div>
        </div>

        <div class="quiz-q" style="margin-top:16px;">{{ covScenarios[covIdx].question }}</div>
        <div class="checklist-group">
          <label v-for="(rec,i) in covScenarios[covIdx].recommendations" :key="i" class="checklist-item" :class="{ 'cl-checked': covChecked[i] }">
            <input type="checkbox" v-model="covChecked[i]" class="cl-input" />
            <span class="cl-text">{{ rec.label }}</span>
            <span v-if="covResult !== null" class="cl-mark">{{ rec.correct ? '✅' : '➖' }}</span>
          </label>
        </div>
        <button v-if="covResult===null" class="btn-primary" style="margin-top:10px;" @click="checkCov">提交选择</button>
        <div v-if="covResult!==null" class="explain">得分: {{ covScore }}/{{ covScenarios[covIdx].recommendations.filter(r=>r.correct).length }} — {{ covScenarios[covIdx].explain }}</div>
      </div>
    </div>

    <!-- ====== Tab 5: Lighthouse Auditor ====== -->
    <div v-if="activeTab === 'lighthouse'" class="tab-content">
      <div class="card">
        <h3>🏠 Lighthouse 审计报告</h3>
        <div class="scenario-bar">
          <button v-for="(s,i) in lhScenarios" :key="i" class="scenario-btn" :class="{ active: lhIdx === i }" @click="lhIdx = i; lhOrder = []; lhResult = null">{{ s.label }}</button>
        </div>

        <div class="lh-scores">
          <div v-for="cat in lhScenarios[lhIdx].categories" :key="cat.name" class="lh-score-card">
            <div class="lh-score-circle" :class="lhScoreClass(cat.score)">{{ cat.score }}</div>
            <div class="lh-score-name">{{ cat.name }}</div>
          </div>
        </div>

        <div class="lh-opps">
          <h4>优化机会</h4>
          <div v-for="(opp,i) in lhScenarios[lhIdx].opportunities" :key="i" class="lh-opp" :class="{ 'lh-opp-selected': lhOrder.includes(i) }" @click="toggleLhPick(i)">
            <span class="lh-opp-num">{{ lhOrder.indexOf(i) >= 0 ? lhOrder.indexOf(i) + 1 : '·' }}</span>
            <div class="lh-opp-body">
              <span class="lh-opp-title">{{ opp.title }}</span>
              <span class="lh-opp-save">预计节省 {{ opp.saving }}</span>
            </div>
          </div>
        </div>

        <div class="quiz-q" style="margin-top:12px;">{{ lhScenarios[lhIdx].question }}</div>
        <div v-if="lhOrder.length > 0" class="lh-picks">已选顺序: {{ lhOrder.map(i => (i+1)).join(' → ') }}</div>
        <button v-if="lhResult===null" class="btn-primary" style="margin-top:8px;" :disabled="lhOrder.length < 3" @click="checkLh">提交排序 (选3项)</button>
        <div v-if="lhResult!==null" class="explain">得分: {{ lhScore }}/5 — {{ lhScenarios[lhIdx].explain }}</div>
      </div>
    </div>

    <!-- ====== Tab 6: Memory Detective ====== -->
    <div v-if="activeTab === 'memory'" class="tab-content">
      <div class="card">
        <h3>💾 内存侦探</h3>
        <div class="scenario-bar">
          <button v-for="(s,i) in memScenarios" :key="i" class="scenario-btn" :class="{ active: memIdx === i }" @click="memIdx = i; memLeakChosen = -1; memFixChosen = -1; memResult = null">{{ s.label }}</button>
        </div>

        <div class="mem-compare">
          <div class="mem-col">
            <div class="mem-col-header">📸 Before</div>
            <div class="mem-size">Heap: {{ memScenarios[memIdx].before.heap }}</div>
            <div class="mem-obj-list">
              <div v-for="(o,i) in memScenarios[memIdx].before.objects" :key="i" class="mem-obj">
                <span class="mem-obj-type">{{ o.type }}</span><span class="mem-obj-count">{{ o.count }}</span>
              </div>
            </div>
          </div>
          <div class="mem-arrow-col">→</div>
          <div class="mem-col">
            <div class="mem-col-header">📸 After</div>
            <div class="mem-size" :class="memScenarios[memIdx].deltaMB > 0 ? 'danger' : ''">Heap: {{ memScenarios[memIdx].after.heap }} <span v-if="memScenarios[memIdx].deltaMB > 0" class="mem-delta">(+{{ memScenarios[memIdx].deltaMB }}MB)</span></div>
            <div class="mem-obj-list">
              <div v-for="(o,i) in memScenarios[memIdx].after.objects" :key="i" class="mem-obj" :class="{ 'mem-obj-leak': o.delta > 0 }">
                <span class="mem-obj-type">{{ o.type }}</span><span class="mem-obj-count">{{ o.count }}</span>
                <span v-if="o.delta > 0" class="mem-delta">+{{ o.delta }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="quiz-q" style="margin-top:16px;">Q1: 什么在泄漏？</div>
        <button v-for="(o,i) in memScenarios[memIdx].leakOptions" :key="i" class="quiz-opt" :class="{ selected: memLeakChosen===i, correct: memResult && i===memScenarios[memIdx].leakAnswer, wrong: memResult && memLeakChosen===i && i!==memScenarios[memIdx].leakAnswer }" :disabled="memResult !== null" @click="memLeakChosen=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span><span>{{ o }}</span>
        </button>

        <div class="quiz-q" style="margin-top:12px;">Q2: 如何修复？</div>
        <button v-for="(o,i) in memScenarios[memIdx].fixOptions" :key="i" class="quiz-opt" :class="{ selected: memFixChosen===i, correct: memResult && i===memScenarios[memIdx].fixAnswer, wrong: memResult && memFixChosen===i && i!==memScenarios[memIdx].fixAnswer }" :disabled="memResult !== null" @click="memFixChosen=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span><span>{{ o }}</span>
        </button>

        <button v-if="memResult===null" class="btn-primary" style="margin-top:10px;" :disabled="memLeakChosen===-1 || memFixChosen===-1" @click="checkMem">提交</button>
        <div v-if="memResult!==null" class="explain">{{ memScore === 2 ? '✅ 全对！' : memScore === 1 ? '⚠️ 对一半。' : '❌ 再想想。' }} {{ memScenarios[memIdx].explain }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const activeTab = ref('network')
const tabs = [
  { id: 'network', label: 'Network', icon: '🔍' },
  { id: 'perf', label: 'Performance', icon: '⚡' },
  { id: 'console', label: 'Console', icon: '🐛' },
  { id: 'coverage', label: 'Coverage', icon: '📊' },
  { id: 'lighthouse', label: 'Lighthouse', icon: '🏠' },
  { id: 'memory', label: 'Memory', icon: '💾' },
]

// ==================== Tab 1: Network ====================
const netIdx = ref(0)
let netExpanded = reactive({})
const netAnswers = ref(['', '', '', ''])
const netSubmitted = ref([false, false, false, false])
const netScore = ref([0, 0, 0, 0])

const netScenarios = [
  {
    label: '🐢 8秒加载', task: '页面加载耗时8秒，找出根本原因',
    question: '诊断：页面为什么需要8秒才加载完成？列出你发现的问题。',
    keywords: ['阻塞脚本', '3rd-party', '未压缩', '2MB图片', '无压缩', '无gzip', '无brotli'],
    explain: '根因：①3个第三方阻塞脚本(analytics.js/chat.js/ad.js)在<head>中同步加载，阻塞渲染3.2秒；②两张2MB未优化图片加载耗时2.6秒；③main.js(1.8MB)未启用Gzip/Brotli压缩。修复：async/defer第三方脚本、压缩图片到WebP/AVIF、启用CDN压缩。',
    resources: [
      { url: '/', type: 'doc', size: '12KB', time: 180, status: 200, reqHeaders: { 'Accept': 'text/html' }, respHeaders: { 'Content-Type': 'text/html', 'Server': 'nginx' } },
      { url: '/analytics.js', type: 'js', size: '320KB', time: 1200, status: 200, reqHeaders: {}, respHeaders: { 'Cache-Control': 'no-cache' } },
      { url: '/chat-widget.js', type: 'js', size: '280KB', time: 980, status: 200, reqHeaders: {}, respHeaders: { 'Cache-Control': 'no-cache' } },
      { url: '/ad-loader.js', type: 'js', size: '180KB', time: 1020, status: 200, reqHeaders: {}, respHeaders: {} },
      { url: '/main.js', type: 'js', size: '1.8MB', time: 2400, status: 200, reqHeaders: {}, respHeaders: { 'Content-Type': 'application/javascript' } },
      { url: '/hero-banner.jpg', type: 'img', size: '2.1MB', time: 1400, status: 200, reqHeaders: {}, respHeaders: { 'Content-Type': 'image/jpeg' } },
      { url: '/product-grid.jpg', type: 'img', size: '1.9MB', time: 1200, status: 200, reqHeaders: {}, respHeaders: {} },
      { url: '/style.css', type: 'css', size: '86KB', time: 320, status: 200, reqHeaders: {}, respHeaders: {} },
    ],
  },
  {
    label: '⚠️ 200但报错', task: 'API返回200但页面显示错误，找出矛盾',
    question: 'API返回200 OK，但页面报错。问题出在哪里？',
    keywords: ['200状态码', 'error', 'body', '服务端', '配置', '状态码不匹配', '响应体'],
    explain: '根因：服务器配置错误——业务层返回了错误，但HTTP状态码仍然设为200。正确的RESTful做法是根据错误类型返回4xx或5xx状态码。响应体{"error":"INVALID_TOKEN","code":401}应该配HTTP 401，但服务器错误地返回了200。前端只检查status===200就认为成功，导致错误数据流入了渲染逻辑。',
    resources: [
      { url: '/api/users/me', type: 'xhr', size: '256B', time: 340, status: 200, reqHeaders: { 'Authorization': 'Bearer eyJ...' }, respHeaders: { 'Content-Type': 'application/json', 'X-Request-ID': 'a1b2c3' } },
      { url: '/api/orders/recent', type: 'xhr', size: '180B', time: 280, status: 200, reqHeaders: {}, respHeaders: { 'Content-Type': 'application/json' } },
      { url: '/api/notifications', type: 'xhr', size: '140B', time: 420, status: 200, reqHeaders: {}, respHeaders: { 'Content-Type': 'application/json' } },
      { url: '/app.js', type: 'js', size: '420KB', time: 560, status: 200, reqHeaders: {}, respHeaders: {} },
    ],
  },
  {
    label: '🖼️ 图片全挂', task: '页面加载完成但所有图片无法显示',
    question: '所有图片都显示为破损图标。根本原因是什么？',
    keywords: ['CORS', '403', 'CDN', '跨域', 'Access-Control', '跨源'],
    explain: '根因：CDN未配置CORS头(Access-Control-Allow-Origin)，导致浏览器阻止跨域图片加载。同时部分图片返回403(CDN token过期)。修复：①CDN添加CORS头Access-Control-Allow-Origin: *；②刷新CDN鉴权token；③img标签添加crossorigin="anonymous"属性。',
    resources: [
      { url: '/', type: 'doc', size: '14KB', time: 120, status: 200, reqHeaders: {}, respHeaders: {} },
      { url: 'https://cdn.example.com/img/logo.png', type: 'img', size: '0B', time: 180, status: 403, reqHeaders: { 'Origin': 'https://app.example.com' }, respHeaders: { 'X-CDN-Error': 'TokenExpired' } },
      { url: 'https://cdn.example.com/img/banner.jpg', type: 'img', size: '0B', time: 160, status: 200, reqHeaders: { 'Origin': 'https://app.example.com' }, respHeaders: { 'Content-Type': 'image/jpeg', 'X-CDN-HIT': '1' } },
      { url: 'https://cdn.example.com/img/icon.svg', type: 'img', size: '0B', time: 140, status: 403, reqHeaders: {}, respHeaders: { 'X-CDN-Error': 'TokenExpired' } },
      { url: '/app.js', type: 'js', size: '380KB', time: 400, status: 200, reqHeaders: {}, respHeaders: {} },
    ],
  },
  {
    label: '🔄 越刷越慢', task: '首次加载快，后续刷新变慢——缓存策略问题',
    question: '首次加载1秒，第二次加载反而要3秒。哪里出了问题？',
    keywords: ['Cache-Control', 'ETag', '缓存', 'no-cache', 'no-store', '重新下载', 'Last-Modified', '缓存策略'],
    explain: '根因：服务器完全没有设置缓存头——缺少Cache-Control、ETag、Last-Modified。浏览器每次重新下载所有资源(共2.8MB)。修复：①静态资源设Cache-Control: public, max-age=31536000, immutable；②启用ETag/Last-Modified用于条件请求(304 Not Modified)；③HTML设Cache-Control: no-cache(每次验证)。',
    resources: [
      { url: '/', type: 'doc', size: '14KB', time: 100, status: 200, reqHeaders: {}, respHeaders: { 'Content-Type': 'text/html' } },
      { url: '/app.js', type: 'js', size: '1.2MB', time: 800, status: 200, reqHeaders: {}, respHeaders: { 'Content-Type': 'application/javascript' } },
      { url: '/vendor.js', type: 'js', size: '900KB', time: 600, status: 200, reqHeaders: {}, respHeaders: { 'Content-Type': 'application/javascript' } },
      { url: '/style.css', type: 'css', size: '180KB', time: 200, status: 200, reqHeaders: {}, respHeaders: { 'Content-Type': 'text/css' } },
      { url: '/logo.svg', type: 'img', size: '24KB', time: 120, status: 200, reqHeaders: {}, respHeaders: {} },
    ],
  },
]
const maxNetTime = computed(() => Math.max(...netScenarios[netIdx.value].resources.map(r => r.time), 1))

function switchNet(i) { netIdx.value = i; Object.keys(netExpanded).forEach(k => delete netExpanded[k]) }
function checkNet() {
  netSubmitted.value[netIdx.value] = true
  const ans = netAnswers.value[netIdx.value].toLowerCase()
  let s = 0
  netScenarios[netIdx.value].keywords.forEach(k => { if (ans.includes(k.toLowerCase())) s++ })
  netScore.value[netIdx.value] = Math.min(s, netScenarios[netIdx.value].keywords.length)
}

// ==================== Tab 2: Performance ====================
const perfIdx = ref(0)
const perfChosen = ref(-1)
const perfResult = ref(null)
const perfScenarios = [
  {
    label: '📜 滚动卡顿', stats: { fps: 12, lcp: 1800, tbt: 340, jsHeap: 48 },
    question: '从火焰图看，滚动卡顿的根因是什么？',
    options: ['A. JS堆内存不足', 'B. 滚动事件处理器中触发了强制同步布局(Forced Reflow)', 'C. 图片太大导致解码慢', 'D. CSS动画过多'],
    answer: 1,
    explain: '火焰图中scroll handler → getBoundingClientRect() → Layout(120ms) 是典型的强制同步布局(Layout Thrashing)。滚动处理器中调用offsetHeight/getBoundingClientRect等会强制浏览器立即重排，每帧120ms远超16.67ms预算。修复：使用requestAnimationFrame批处理、用transform代替top/left、缓存布局值。',
    flame: [
      { name: 'scroll handler', dur: 128, nest: 0, color: '#ef4444' },
      { name: 'getBoundingClientRect()', dur: 8, nest: 1 },
      { name: 'Layout (forced reflow)', dur: 120, nest: 1, color: '#f59e0b' },
      { name: 'updatePosition()', dur: 6, nest: 2 },
      { name: 'Paint', dur: 14, nest: 1 },
      { name: 'requestAnimationFrame', dur: 2, nest: 0 },
      { name: 'Composite', dur: 4, nest: 0 },
    ],
  },
  {
    label: '🖱️ 点击延迟', stats: { fps: 55, lcp: 1200, tbt: 180, jsHeap: 62 },
    question: '按钮点击后500ms才响应，从火焰图中诊断根因。',
    options: ['A. 网络请求太慢', 'B. 主线程被GC(垃圾回收)阻塞400ms', 'C. 事件冒泡层级太深', 'D. CSS transition设置了500ms'],
    answer: 1,
    explain: '火焰图清晰显示：点击事件→400ms GC(垃圾回收) pause→100ms事件处理器。Major GC在主线程运行时会停止所有JS执行。可能原因：短时间内创建大量临时对象触发GC。修复：对象池复用、减少内存分配频率、使用WeakRef/WeakMap、分片处理大数据。',
    flame: [
      { name: 'click event', dur: 500, nest: 0, color: '#ef4444' },
      { name: 'Garbage Collection (Major GC)', dur: 400, nest: 1, color: '#f59e0b' },
      { name: 'Mark-Sweep', dur: 280, nest: 2 },
      { name: 'Compaction', dur: 120, nest: 2 },
      { name: 'handleClick()', dur: 100, nest: 1 },
      { name: 'updateDOM()', dur: 40, nest: 2 },
      { name: 'Layout', dur: 30, nest: 2 },
      { name: 'Paint', dur: 20, nest: 2 },
    ],
  },
  {
    label: '🧟 页面僵死', stats: { fps: 2, lcp: 4500, tbt: 8200, jsHeap: 380 },
    question: '打开页面10秒后完全无响应。火焰图显示的问题是什么？',
    options: ['A. 网络请求卡住', 'B. 内存泄漏——分离DOM节点持续累积导致GC频繁触发', 'C. Service Worker 阻塞主线程', 'D. WebSocket 消息过多'],
    answer: 1,
    explain: '火焰图显示Detached DOM nodes从初始的0增长到12,000+，JS堆从48MB→380MB。每次GC尝试回收但分离DOM节点被JS变量引用无法回收，导致GC频率越来越高(间隔从5秒→500ms)，最终主线程全被GC占满。典型的内存泄漏模式：removeChild后仍持有DOM引用、闭包捕获DOM节点、事件监听器未移除。',
    flame: [
      { name: 'Timer Fired', dur: 1600, nest: 0, color: '#ef4444' },
      { name: 'GC (attempt #14)', dur: 800, nest: 1, color: '#f59e0b' },
      { name: 'renderTable()', dur: 400, nest: 1 },
      { name: 'createRow() x40', dur: 300, nest: 2 },
      { name: 'removeChild()', dur: 80, nest: 2 },
      { name: 'GC (attempt #13)', dur: 720, nest: 0, color: '#f59e0b' },
      { name: 'Timer Fired', dur: 1200, nest: 0, color: '#ef4444' },
      { name: 'GC (attempt #12)', dur: 600, nest: 1, color: '#f59e0b' },
    ],
  },
]
const maxPerfDur = computed(() => Math.max(...perfScenarios[perfIdx.value].flame.map(f => f.dur), 1))
function getFlameColor(dur) { return dur > 200 ? '#ef4444' : dur > 50 ? '#f59e0b' : dur > 16 ? '#6366f1' : '#10b981' }
function checkPerf() { perfResult.value = perfChosen.value === perfScenarios[perfIdx.value].answer }

// ==================== Tab 3: Console ====================
const conIdx = ref(0)
const conChosen = ref(-1)
const conResult = ref(null)
const conScenarios = [
  {
    label: '🔐 Mixed Content', question: '根据控制台输出，根因是什么？',
    options: ['A. 服务器配置错误返回500', 'B. HTTPS页面加载了HTTP资源(Mixed Content)', 'C. JavaScript语法错误', 'D. 浏览器不兼容'],
    answer: 1,
    explain: 'Mixed Content：HTTPS页面中引用了HTTP资源。浏览器默认阻止Active Mixed Content(script/CSS)并警告Passive Mixed Content(image/video)。控制台显示3个HTTP脚本被阻止+4个HTTP图片产生警告。修复：所有资源使用HTTPS(//省略协议)或CSP upgrade-insecure-requests。',
    entries: [
      { level: 'error', text: 'Mixed Content: The page at \'https://app.example.com\' was loaded over HTTPS, but requested an insecure script \'http://cdn.example.com/jquery.js\'. This request has been blocked; the content must be served over HTTPS.', src: '' },
      { level: 'error', text: 'Mixed Content: ...requested an insecure script \'http://stats.example.com/tracker.js\'. This request has been blocked.', src: '' },
      { level: 'error', text: 'Mixed Content: ...requested an insecure script \'http://widget.example.com/chat.js\'. This request has been blocked.', src: '' },
      { level: 'warn', text: 'Mixed Content: ...requested an insecure image \'http://img.example.com/logo.png\'. This content should also be served over HTTPS.', src: '' },
      { level: 'warn', text: 'Mixed Content: ...requested an insecure image \'http://img.example.com/banner.jpg\'.', src: '' },
      { level: 'warn', text: 'Mixed Content: ...requested an insecure image \'http://img.example.com/icon.svg\'.', src: '' },
      { level: 'warn', text: 'Mixed Content: ...requested an insecure image \'http://img.example.com/avatar.webp\'.', src: '' },
    ],
  },
  {
    label: '🚫 404 + CSP', question: '页面空白无内容，控制台揭示了什么根因？',
    options: ['A. React组件渲染崩溃', 'B. API端点URL写错(404) + CSP阻止内联脚本', 'C. 浏览器缓存过期', 'D. CDN回源失败'],
    answer: 1,
    explain: '两个关键错误：①/api/v2/products拼写成了/api/v2/products(少个c)→404。CSP阻止了所有内联脚本执行。修复：修正API端点拼写、将内联脚本改为外部文件或使用nonce/hash。',
    entries: [
      { level: 'error', text: 'GET https://app.example.com/api/v2/products 404 (Not Found)', src: 'app.js:42' },
      { level: 'error', text: 'Refused to execute inline script because it violates the following Content Security Policy directive: "script-src \'self\'". Either the \'unsafe-inline\' keyword, a hash, or a nonce is required.', src: '(index):24' },
      { level: 'error', text: 'Refused to execute inline event handler because it violates CSP: "script-src \'self\'".', src: '(index):56' },
      { level: 'error', text: 'Uncaught (in promise) TypeError: Cannot read properties of undefined (reading \'map\')', src: 'app.js:128' },
      { level: 'info', text: 'Navigated to https://app.example.com/dashboard', src: '' },
    ],
  },
  {
    label: '📜 弃用警告', question: '控制台显示多个弃用警告，QA应该建议开发做什么？',
    options: ['A. 忽略，弃用不影响功能', 'B. 迁移到推荐的新API，制定升级计划', 'C. 降级浏览器版本', 'D. 加polyfill掩盖警告'],
    answer: 1,
    explain: '弃用API在未来浏览器版本中可能被移除。这些警告是主动发现问题的最佳时机。document.execCommand已弃用→用Clipboard API；navigator.plugins已弃用→用feature detection；::-webkit-scrollbar已弃用→用scrollbar-width/scrollbar-color。QA应记录这些警告作为技术债务条目。',
    entries: [
      { level: 'warn', text: '[Deprecation] document.execCommand() is deprecated. Use the Clipboard API instead.', src: 'editor.js:89' },
      { level: 'warn', text: '[Deprecation] navigator.plugins is deprecated. Use feature detection instead.', src: 'detect.js:12' },
      { level: 'warn', text: '[Deprecation] \'WebKitMutationObserver\' is deprecated. Use \'MutationObserver\' instead.', src: 'polyfills.js:5' },
      { level: 'warn', text: '[Deprecation] The \'::-webkit-scrollbar\' pseudo-element is deprecated. Use \'scrollbar-width\' and \'scrollbar-color\' instead.', src: 'theme.css:340' },
      { level: 'info', text: 'Page loaded in 1.2s', src: '' },
      { level: 'warn', text: '[Deprecation] Synchronous XMLHttpRequest on the main thread is deprecated.', src: 'legacy.js:143' },
    ],
  },
  {
    label: '💥 TypeError追踪', question: 'Uncaught TypeError显示在app.js:156。如何定位根因？',
    options: ['A. 重启浏览器', 'B. 点击app.js:156链接跳转到Sources面板，检查调用栈和变量值', 'C. 清除localStorage', 'D. 直接修改第156行代码'],
    answer: 1,
    explain: '控制台错误带有源映射链接(Source Map)，点击app.js:156直接打开Sources面板定位到出错行。调用栈显示：handleSubmit→validateForm→formatDate→第156行date.toISOString()。根因：date变量为null，未做空值检查。修复：在formatDate中添加null check (date?.toISOString() ?? "")。这是QA利用DevTools定位前端Bug的标准流程。',
    entries: [
      { level: 'error', text: 'Uncaught TypeError: Cannot read properties of null (reading \'toISOString\')', src: 'app.js:156:24' },
      { level: 'error', text: '  at formatDate (app.js:156:24)', src: '' },
      { level: 'error', text: '  at validateForm (app.js:203:15)', src: '' },
      { level: 'error', text: '  at HTMLFormElement.handleSubmit (app.js:340:8)', src: '' },
      { level: 'info', text: 'User clicked submit button', src: 'app.js:336' },
      { level: 'log', text: 'Form data: {name: "Test", date: null, email: "test@example.com"}', src: 'app.js:338' },
    ],
  },
]
function checkCon() { conResult.value = conChosen.value === conScenarios[conIdx.value].answer }

// ==================== Tab 4: Coverage ====================
const covIdx = ref(0)
let covChecked = reactive({})
const covResult = ref(null)
const covScore = ref(0)

function clearCovChecked() {
  Object.keys(covChecked).forEach(k => delete covChecked[k])
}
const covScenarios = [
  {
    label: '🏠 首页冗余', cssUsed: 22, jsUsed: 35,
    cssDetail: '总CSS 420KB → 使用92KB (22%)。960条规则中仅210条在首页生效。',
    jsDetail: '总JS 1.8MB → 使用630KB (35%)。包含完整的Admin面板/设置页/报表模块代码，首页用不到。',
    question: '选择正确的优化建议：',
    recommendations: [
      { label: '为首页拆分独立CSS bundle，只加载首屏需要的样式', correct: true },
      { label: '删除所有CSS，改用内联style', correct: false },
      { label: 'JS按路由懒加载——Admin/设置/报表模块独立chunk', correct: true },
      { label: '使用CSS @import合并所有样式', correct: false },
      { label: '通过PurgeCSS移除首页未使用的CSS规则', correct: true },
      { label: '把全部JS合并为一个更大的bundle避免多次请求', correct: false },
    ],
    explain: '正确做法：CSS Code-Splitting(首页独立bundle)+PurgeCSS清除未用样式+JS路由懒加载。合并全部JS反而恶化问题。@import会创建串行请求链，更应避免。关键认知：未用代码不只是浪费下载带宽，更重要的是浪费解析/编译时间——CSS阻塞渲染，JS阻塞主线程。',
  },
  {
    label: '📦 Vendor膨胀', cssUsed: 85, jsUsed: 6,
    cssDetail: '总CSS 180KB → 使用153KB (85%)。合理。',
    jsDetail: '总JS 3.1MB(含vendor) → 仅使用200KB (6%)。lodash全量(530KB)只用_.debounce，echarts全量(980KB)只用折线图。',
    question: '选择正确的优化建议：',
    recommendations: [
      { label: '用lodash-es + tree-shaking，或直接import debounce from lodash/debounce', correct: true },
      { label: 'echarts改为动态import()，仅在需要图表的路由加载', correct: true },
      { label: '删除vendor bundle，手写所有功能', correct: false },
      { label: '强制浏览器缓存vendor.js 10年', correct: false },
      { label: '用date-fns替代moment.js(若存在)、用native API替代小工具函数', correct: true },
      { label: '将vendor.js拆得更碎，每个函数一个请求', correct: false },
    ],
    explain: '核心策略：Tree-shaking(ES模块静态分析去掉未引用代码)+Code Splitting(动态import按需加载)。Lodash用路径导入(lodash/debounce)而非全量导入。ECharts/Chart.js等大型图表库最适合作动态import。过长的缓存时间会导致有bug时无法更新，需要配合文件名hash。',
  },
]
function checkCov() {
  covResult.value = true
  let correct = 0; let picked = 0
  covScenarios[covIdx.value].recommendations.forEach((r, i) => {
    if (covChecked[i]) { picked++; if (r.correct) correct++ }
    else if (r.correct) { /* missed */ }
  })
  covScore.value = correct
}

// ==================== Tab 5: Lighthouse ====================
const lhIdx = ref(0)
const lhOrder = ref([])
const lhResult = ref(null)
const lhScore = ref(0)
const lhScenarios = [
  {
    label: '🐢 Perf 45', question: '从以下6个优化机会中，选出3个优先级最高的修复(按影响/投入排序)：',
    explain: '最佳顺序：①图片优化(WebP+响应式)—影响最大(节省2.4s)+实现简单；②Gzip/Brotli压缩—影响大(节省1.6s)+Nginx一行配置；③关键CSS内联—消除渲染阻塞+影响首屏指标。JS延迟加载和字体优化可以后续做，收益递减。',
    categories: [
      { name: 'Performance', score: 45 }, { name: 'Accessibility', score: 78 }, { name: 'Best Practices', score: 90 }, { name: 'SEO', score: 82 },
    ],
    opportunities: [
      { title: '图片未优化：4张PNG可转WebP/AVIF', saving: '2.4s' },
      { title: '未启用文本压缩(Gzip/Brotli)', saving: '1.6s' },
      { title: '渲染阻塞CSS：首屏CSS未内联', saving: '0.8s' },
      { title: 'JS未延迟加载：3个非关键脚本阻塞渲染', saving: '0.6s' },
      { title: '字体文件未优化：未使用font-display:swap', saving: '0.3s' },
      { title: '未使用CDN：所有资源同域加载', saving: '0.5s' },
    ],
  },
  {
    label: '♿ A11y 62', question: '从以下6个无障碍问题中，选出3个最应先修复的(按影响/投入排序)：',
    explain: '最佳顺序：①表单标签—影响最大(键盘/屏幕阅读器用户无法操作表单)+修复简单(加label/aria-label)；②对比度—低对比度影响所有低视力用户+修复量稍大但标准明确；③跳过链接—键盘用户每次都要Tab过整个导航+添加简单。h1层级和图片alt文本也应修复，但影响面略小。',
    categories: [
      { name: 'Accessibility', score: 62 }, { name: 'Performance', score: 72 }, { name: 'Best Practices', score: 85 }, { name: 'SEO', score: 68 },
    ],
    opportunities: [
      { title: '表单控件缺少关联label标签', saving: '影响: 全部键盘/屏幕阅读器用户' },
      { title: '12处文本对比度低于4.5:1', saving: '影响: 低视力用户' },
      { title: '缺少跳过导航链接(skip link)', saving: '影响: 键盘导航用户' },
      { title: '图片缺少alt文本(8张)', saving: '影响: 屏幕阅读器用户' },
      { title: '标题层级不连续(h1→h3跳过了h2)', saving: '影响: 屏幕阅读器导航' },
      { title: '自定义组件缺少ARIA角色', saving: '影响: 屏幕阅读器用户' },
    ],
  },
  {
    label: '🔍 SEO 55', question: '从以下6个SEO问题中，选出3个最应先修复的(按影响/投入排序)：',
    explain: '最佳顺序：①meta description—搜索排名直接因子+修复只需一句话；②alt文本—图片搜索流量+无障碍双赢+修复量中等；③标题层级—搜索引擎用h1-h6理解内容结构+修复少量HTML。结构化数据是排名提升项但有技术门槛，canonical对重复内容重要但此场景次要。',
    categories: [
      { name: 'SEO', score: 55 }, { name: 'Performance', score: 68 }, { name: 'Accessibility', score: 74 }, { name: 'Best Practices', score: 88 },
    ],
    opportunities: [
      { title: '缺少meta description', saving: '搜索排名直接因子' },
      { title: '8张图片缺少alt文本', saving: '图片搜索流量' },
      { title: '标题层级不连续(h1→h3)', saving: '搜索爬虫理解内容结构' },
      { title: '缺少结构化数据(JSON-LD)', saving: '富文本搜索结果' },
      { title: '缺少canonical标签', saving: '重复内容惩罚风险' },
      { title: 'robots.txt未配置', saving: '爬虫抓取效率' },
    ],
  },
]
function lhScoreClass(s) { return s >= 90 ? 'lh-green' : s >= 50 ? 'lh-orange' : 'lh-red' }
function toggleLhPick(i) {
  const idx = lhOrder.value.indexOf(i)
  if (idx >= 0) { lhOrder.value.splice(idx, 1); return }
  if (lhOrder.value.length >= 3) { lhOrder.value.shift() }
  lhOrder.value.push(i)
}
function checkLh() {
  lhResult.value = true
  // Score: each pick in correct position gets points, correct items in any order get partial
  const ideal = [0, 1, 2] // simplified: first 3 are always ideal order
  let s = 0
  lhOrder.value.forEach((item, pos) => { if (ideal[pos] === item) s += 2; else if (ideal.includes(item)) s += 1 })
  lhScore.value = Math.min(s, 5)
}

// ==================== Tab 6: Memory ====================
const memIdx = ref(0)
const memLeakChosen = ref(-1)
const memFixChosen = ref(-1)
const memResult = ref(null)
const memScore = ref(0)
const memScenarios = [
  {
    label: '🪟 弹窗泄漏',
    deltaMB: 10,
    before: { heap: '24MB', objects: [{ type: 'HTMLDivElement', count: 12 }, { type: 'EventListener', count: 48 }, { type: 'Closure', count: 24 }, { type: 'Array', count: 30 }] },
    after: { heap: '34MB', objects: [{ type: 'HTMLDivElement (Detached)', count: 59, delta: 47 }, { type: 'EventListener', count: 86, delta: 38 }, { type: 'Closure', count: 56, delta: 32 }, { type: 'Array', count: 30, delta: 0 }] },
    question: '每次打开/关闭弹窗，堆内存增长10MB。什么在泄漏？如何修复？',
    leakOptions: ['A. 数组对象累积', 'B. 分离的HTMLDivElement(Detached DOM) — 弹窗DOM未正确移除被闭包引用', 'C. CSS动画占内存', 'D. console.log输出太多'],
    leakAnswer: 1,
    fixOptions: ['A. 使用innerHTML=\'\'清空弹窗', 'B. 移除弹窗时同时removeEventListener + 清空闭包引用 → el.remove() + el=null', 'C. 使用visibility:hidden代替remove', 'D. 限制弹窗打开次数'],
    fixAnswer: 1,
    explain: '分离DOM节点(Detached DOM)泄漏：modal.remove()将节点从DOM树移除，但JS变量仍持有引用(如闭包中的modalEl、事件监听器未removeEventListener)→GC无法回收。每次打开弹窗创建新DOM，旧的无法回收→10MB增长。修复：①组件卸载时removeEventListener；②将DOM引用置null；③使用WeakRef或框架的自动清理(onUnmounted)。',
  },
  {
    label: '📊 表格重渲染',
    deltaMB: 50,
    before: { heap: '32MB', objects: [{ type: 'HTMLTableRowElement', count: 20 }, { type: 'EventListener', count: 60 }, { type: 'Closure', count: 40 }, { type: 'Object', count: 80 }] },
    after: { heap: '82MB', objects: [{ type: 'HTMLTableRowElement (Detached)', count: 420, delta: 400 }, { type: 'EventListener', count: 860, delta: 800 }, { type: 'Closure', count: 440, delta: 400 }, { type: 'Object (retained)', count: 280, delta: 200 }] },
    question: '20次表格重渲染后堆增长50MB。什么在泄漏？如何修复？',
    leakOptions: ['A. 表格数据本身太大', 'B. 事件监听器未清理 + 闭包持有旧行引用 → 每次重渲染旧DOM和事件处理器泄漏', 'C. 浏览器渲染引擎bug', 'D. CSS选择器太复杂'],
    leakAnswer: 1,
    fixOptions: ['A. 减少表格行数到10行以内', 'B. 每次渲染前先移除旧监听器 + 使用事件委托(在table上监听而非每行) + 不在闭包中持有DOM引用', 'C. 使用display:none代替移除DOM', 'D. 每隔几次重渲染重启浏览器'],
    fixAnswer: 1,
    explain: '每次重渲染：①未调用removeEventListener导致旧的事件监听器堆积(每行3个监听器×20行×20次=1200个遗留监听器)；②闭包(如onClick=()=>rowData)持有已移除的DOM行引用→整个行对象链无法回收。修复：事件委托(在父元素上监听，利用冒泡)，避免闭包持有DOM引用，重渲染前清理。',
  },
]
function checkMem() {
  memResult.value = true
  let s = 0
  if (memLeakChosen.value === memScenarios[memIdx.value].leakAnswer) s++
  if (memFixChosen.value === memScenarios[memIdx.value].fixAnswer) s++
  memScore.value = s
}
</script>

<style scoped>
.lab-page { max-width: 920px; margin: 0 auto; }

/* Tab bar */
.tab-bar { display: flex; gap: 4px; margin-bottom: var(--space-lg); background: var(--surface); border-radius: var(--radius); padding: 4px; border: 1px solid var(--border); overflow-x: auto; }
.tab-btn { flex: 1; min-width: 90px; padding: 10px 6px; border: none; background: none; border-radius: 8px; cursor: pointer; font-size: .78rem; color: var(--text-secondary); font-weight: 500; transition: all var(--fast); font-family: var(--font-sans); display: flex; flex-direction: column; align-items: center; gap: 3px; }
.tab-btn.active { background: var(--primary); color: #fff; font-weight: 600; }
.tab-icon { font-size: 1.1rem; }
.tab-label { font-size: .68rem; white-space: nowrap; }

.tab-content h3 { font-size: 1rem; margin-bottom: 14px; }

/* Scenario bar */
.scenario-bar { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.scenario-btn { padding: 6px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border); background: var(--surface); cursor: pointer; font-size: .78rem; font-weight: 500; transition: all var(--fast); font-family: var(--font-sans); }
.scenario-btn:hover { border-color: var(--primary); }
.scenario-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }
.task-desc { font-size: .82rem; color: var(--text-secondary); margin-bottom: 12px; }

/* Waterfall */
.waterfall { background: #1a1a2e; border-radius: var(--radius); overflow: hidden; }
.wf-header { display: grid; grid-template-columns: 2fr 60px 60px 1.5fr 50px; gap: 8px; padding: 8px 14px; background: #16162a; font-size: .68rem; color: #a0a0b8; font-weight: 600; font-family: var(--font-mono); }
.wf-row { display: grid; grid-template-columns: 2fr 60px 60px 1.5fr 50px; gap: 8px; padding: 7px 14px; font-size: .72rem; font-family: var(--font-mono); color: #e5e7eb; cursor: pointer; transition: background var(--fast); align-items: center; border-bottom: 1px solid #222640; }
.wf-row:hover { background: #222640; }
.wf-url { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: .7rem; }
.wf-type { font-size: .62rem; padding: 1px 6px; border-radius: 3px; text-align: center; font-weight: 600; }
.wf-type-doc { background: #6366f1; color: #fff; }
.wf-type-js { background: #f59e0b; color: #000; }
.wf-type-css { background: #10b981; color: #fff; }
.wf-type-img { background: #8b5cf6; color: #fff; }
.wf-type-xhr { background: #3b82f6; color: #fff; }
.wf-size { font-size: .68rem; color: #a0a0b8; }
.wf-bar-wrap { position: relative; height: 14px; background: #16162a; border-radius: 3px; display: flex; align-items: center; }
.wf-bar { height: 100%; border-radius: 3px; min-width: 2px; }
.wf-bar-doc { background: #6366f1; }
.wf-bar-js { background: #f59e0b; }
.wf-bar-css { background: #10b981; }
.wf-bar-img { background: #8b5cf6; }
.wf-bar-xhr { background: #3b82f6; }
.wf-time { position: absolute; right: 4px; font-size: .6rem; color: #e5e7eb; }
.wf-status { font-size: .68rem; font-weight: 600; }
.wf-ok { color: #10b981; }
.wf-redir { color: #f59e0b; }
.wf-err { color: #ef4444; }
.wf-headers { grid-column: 1 / -1; padding: 8px 14px; background: #0f1117; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.wf-hdr-block { font-size: .64rem; }
.wf-hdr-label { color: #6366f1; font-weight: 600; margin-bottom: 4px; }
.wf-hdr-line { color: #a0a0b8; line-height: 1.6; font-family: var(--font-mono); word-break: break-all; }
.wf-hdr-line code { color: #e5e7eb; font-size: .62rem; background: #16162a; padding: 1px 4px; border-radius: 2px; }

/* Text answer */
.text-answer { width: 100%; min-height: 80px; padding: 12px; border: 2px solid var(--border); border-radius: var(--radius); font-family: var(--font-sans); font-size: .84rem; resize: vertical; background: var(--surface); color: var(--text); transition: border-color var(--fast); }
.text-answer:focus { outline: none; border-color: var(--primary); }

/* Performance */
.perf-stats { display: flex; gap: 14px; margin-bottom: 16px; }
.perf-stat { display: flex; flex-direction: column; align-items: center; padding: 10px 16px; background: var(--bg); border-radius: var(--radius); min-width: 70px; }
.perf-stat-val { font-size: 1.3rem; font-weight: 750; font-family: var(--font-mono); }
.perf-stat-val.danger { color: var(--danger); }
.perf-stat-val.success { color: var(--success); }
.perf-stat-label { font-size: .68rem; color: var(--text-muted); margin-top: 2px; }
.flame-chart { background: #1a1a2e; border-radius: var(--radius); padding: 10px; }
.flame-bar { display: flex; align-items: center; justify-content: space-between; height: 22px; margin-bottom: 2px; border-radius: 3px; padding: 0 6px; min-width: 40px; }
.flame-label { font-size: .66rem; font-family: var(--font-mono); color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.flame-dur { font-size: .62rem; font-family: var(--font-mono); color: rgba(255,255,255,.7); white-space: nowrap; margin-left: 8px; }

/* Console */
.console-panel { background: #1a1a2e; border-radius: var(--radius); overflow: hidden; }
.console-topbar { display: flex; align-items: center; gap: 8px; padding: 8px 14px; background: #16162a; }
.console-dot { width: 10px; height: 10px; border-radius: 50%; }
.c-red { background: #ef4444; } .c-yellow { background: #f59e0b; } .c-green { background: #10b981; }
.console-title { font-size: .68rem; color: #a0a0b8; font-family: var(--font-mono); margin-left: 8px; }
.console-body { padding: 10px 14px; max-height: 320px; overflow-y: auto; }
.console-line { display: flex; align-items: baseline; gap: 8px; padding: 3px 0; font-size: .72rem; font-family: var(--font-mono); line-height: 1.55; border-bottom: 1px solid #16162a; }
.con-error { color: #f87171; }
.con-warn { color: #fbbf24; }
.con-info { color: #60a5fa; }
.con-log { color: #a0a0b8; }
.con-icon { font-size: .65rem; flex-shrink: 0; }
.con-text { word-break: break-all; }
.con-src { font-size: .62rem; color: #6366f1; margin-left: auto; white-space: nowrap; flex-shrink: 0; }

/* Coverage */
.cov-overview { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
@media (max-width: 600px) { .cov-overview { grid-template-columns: 1fr; } }
.cov-type { background: var(--bg); border-radius: var(--radius); padding: 16px; }
.cov-type-header { font-weight: 700; font-size: .88rem; margin-bottom: 10px; }
.cov-bar-bg { height: 18px; background: #e5e7eb; border-radius: 9px; overflow: hidden; margin-bottom: 8px; }
.cov-bar-fill { height: 100%; border-radius: 9px; transition: width var(--normal); }
.cov-bar-good { background: var(--success); }
.cov-bar-bad { background: var(--danger); }
.cov-stats { display: flex; justify-content: space-between; margin-bottom: 6px; }
.cov-pct { font-size: .72rem; font-family: var(--font-mono); font-weight: 600; color: var(--success); }
.cov-unused { color: var(--danger); }
.cov-detail { font-size: .72rem; color: var(--text-secondary); line-height: 1.5; }

/* Checklist */
.checklist-group { display: flex; flex-direction: column; gap: 6px; }
.checklist-item { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border: 2px solid var(--border); border-radius: var(--radius); cursor: pointer; transition: all var(--fast); font-size: .84rem; }
.checklist-item:hover { border-color: var(--primary); background: var(--primary-light); }
.checklist-item.cl-checked { border-color: var(--primary); background: var(--primary-light); }
.cl-input { accent-color: var(--primary); width: 16px; height: 16px; cursor: pointer; }
.cl-text { flex: 1; }
.cl-mark { font-size: .8rem; }

/* Lighthouse */
.lh-scores { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.lh-score-card { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.lh-score-circle { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; font-weight: 750; font-family: var(--font-mono); color: #fff; }
.lh-green { background: #10b981; }
.lh-orange { background: #f59e0b; }
.lh-red { background: #ef4444; }
.lh-score-name { font-size: .72rem; color: var(--text-secondary); font-weight: 500; }
.lh-opps h4 { font-size: .88rem; margin-bottom: 10px; }
.lh-opp { display: flex; align-items: center; gap: 10px; padding: 10px 14px; margin-bottom: 6px; border: 2px solid var(--border); border-radius: var(--radius); cursor: pointer; transition: all var(--fast); }
.lh-opp:hover { border-color: var(--primary); }
.lh-opp-selected { border-color: var(--primary); background: var(--primary-light); }
.lh-opp-num { width: 24px; height: 24px; border-radius: 50%; background: var(--primary); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .7rem; flex-shrink: 0; }
.lh-opp:not(.lh-opp-selected) .lh-opp-num { background: var(--border-light); color: var(--text-muted); }
.lh-opp-body { display: flex; flex-direction: column; gap: 2px; }
.lh-opp-title { font-size: .82rem; font-weight: 600; }
.lh-opp-save { font-size: .72rem; color: var(--success); font-family: var(--font-mono); }
.lh-picks { font-size: .8rem; color: var(--primary); font-weight: 600; font-family: var(--font-mono); margin-top: 6px; }

/* Memory */
.mem-compare { display: grid; grid-template-columns: 1fr 40px 1fr; gap: 8px; align-items: start; margin-bottom: 16px; }
.mem-col { background: #1a1a2e; border-radius: var(--radius); padding: 14px; }
.mem-col-header { font-size: .78rem; font-weight: 700; color: #a0a0b8; margin-bottom: 8px; }
.mem-size { font-size: .84rem; font-family: var(--font-mono); font-weight: 600; color: #e5e7eb; margin-bottom: 10px; }
.mem-size.danger { color: #f87171; }
.mem-arrow-col { display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: var(--text-muted); }
.mem-obj-list { display: flex; flex-direction: column; gap: 4px; }
.mem-obj { display: flex; align-items: center; gap: 8px; padding: 4px 8px; background: #16162a; border-radius: 4px; font-size: .7rem; font-family: var(--font-mono); }
.mem-obj-leak { background: rgba(239,68,68,.15); border: 1px solid rgba(239,68,68,.3); }
.mem-obj-type { color: #a0a0b8; flex: 1; }
.mem-obj-count { color: #e5e7eb; font-weight: 600; }
.mem-delta { color: #f87171; font-weight: 600; font-size: .65rem; }

/* Shared quiz */
.quiz-q { font-size: .92rem; font-weight: 600; margin-bottom: 12px; line-height: 1.5; }
.quiz-opt { display: flex; align-items: center; gap: 12px; width: 100%; padding: 12px 16px; margin-bottom: 6px; border: 2px solid var(--border); border-radius: var(--radius); background: var(--surface); cursor: pointer; font-size: .86rem; text-align: left; transition: all var(--fast); font-family: var(--font-sans); }
.quiz-opt:hover:not(:disabled) { border-color: var(--primary); background: var(--primary-light); }
.quiz-opt.selected { border-color: var(--primary); background: var(--primary-light); font-weight: 600; }
.quiz-opt.correct { border-color: var(--success); background: var(--success-light); }
.quiz-opt.wrong { border-color: var(--danger); background: var(--danger-light); }
.quiz-opt:disabled { cursor: default; }
.opt-letter { width: 26px; height: 26px; border-radius: 6px; background: var(--border-light); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .76rem; flex-shrink: 0; }
.quiz-opt.selected .opt-letter { background: var(--primary); color: #fff; }
.quiz-opt.correct .opt-letter { background: var(--success); color: #fff; }
.quiz-opt.wrong .opt-letter { background: var(--danger); color: #fff; }
.explain { margin-top: 12px; padding: 14px; background: var(--primary-light); border-radius: var(--radius); font-size: .84rem; line-height: 1.6; }
</style>
