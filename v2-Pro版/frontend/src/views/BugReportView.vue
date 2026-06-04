<template>
  <div class="lab-page">
    <!-- Scenario selector -->
    <div class="scenario-bar">
      <button v-for="(s,i) in scenarios" :key="i" class="scenario-btn" :class="{ active: current === i }"
        @click="selectScenario(i)">{{ s.label }}</button>
    </div>

    <!-- Scenario description -->
    <div class="card scenario-desc" style="margin-bottom:var(--space-md);">
      <div class="sd-header">
        <span class="sd-badge">{{ scenarios[current].module }}</span>
        <span class="sd-severity" :class="'sev-' + scenarios[current].trueSeverity">{{ scenarios[current].trueSeverity.toUpperCase() }}</span>
      </div>
      <h3>{{ scenarios[current].title }}</h3>
      <p class="sd-context">{{ scenarios[current].context }}</p>
      <div class="sd-screenshot" v-html="scenarios[current].visual"></div>
    </div>

    <!-- Bug report form -->
    <div class="card" style="margin-bottom:var(--space-md);">
      <h3 style="margin-bottom:var(--space-md);font-size:.95rem;">📝 撰写 Bug 报告</h3>

      <div class="field">
        <label>标题 <span class="hint">(清晰描述「什么条件下发生了什么」)</span></label>
        <input v-model="report.title" placeholder="例：[登录] 正确密码+空用户名点击登录后页面白屏" class="form-input">
      </div>

      <div class="field">
        <label>复现步骤 <span class="hint">(numbered, 任何人按步骤都能复现)</span></label>
        <textarea v-model="report.steps" rows="4" placeholder="1. 打开登录页&#10;2. 用户名留空&#10;3. 输入正确密码&#10;4. 点击「登录」按钮" class="form-input"></textarea>
      </div>

      <div class="field-row">
        <div class="field" style="flex:1;">
          <label>预期结果</label>
          <textarea v-model="report.expected" rows="2" placeholder="应显示「请输入用户名」提示" class="form-input"></textarea>
        </div>
        <div class="field" style="flex:1;">
          <label>实际结果</label>
          <textarea v-model="report.actual" rows="2" placeholder="页面白屏，控制台报错" class="form-input"></textarea>
        </div>
      </div>

      <div class="field-row">
        <div class="field" style="flex:1;">
          <label>严重程度</label>
          <select v-model="report.severity" class="form-input">
            <option value="">-- 选择 --</option>
            <option>P0 - 阻塞</option><option>P1 - 严重</option><option>P2 - 一般</option><option>P3 - 轻微</option><option>P4 - 建议</option>
          </select>
        </div>
        <div class="field" style="flex:1;">
          <label>测试环境</label>
          <input v-model="report.environment" placeholder="Chrome 120 / Windows 11 / v2.3.1" class="form-input">
        </div>
      </div>

      <button class="btn-primary" style="width:100%;justify-content:center;padding:12px;margin-top:12px;" @click="submitReport">
        📋 提交评审
      </button>
    </div>

    <!-- Score result -->
    <div v-if="result" class="card result-card" :class="result.grade">
      <div class="result-header">
        <span class="result-grade">{{ result.grade === 'excellent' ? '🏆' : result.grade === 'good' ? '👍' : '📝' }}</span>
        <div>
          <h2>{{ result.grade === 'excellent' ? '优秀！' : result.grade === 'good' ? '良好' : '需要改进' }}</h2>
          <p>总分: <strong>{{ result.total }}</strong>/100</p>
        </div>
      </div>

      <div class="score-breakdown">
        <div v-for="(s, key) in result.scores" :key="key" class="score-row">
          <span class="score-label">{{ s.label }}</span>
          <div class="score-bar-track"><div class="score-bar-fill" :class="s.pct >= 80 ? 'green' : s.pct >= 50 ? 'yellow' : 'red'" :style="{width:s.pct+'%'}"></div></div>
          <span class="score-num">{{ s.score }}/{{ s.max }}</span>
          <span v-if="s.feedback" class="score-feedback">{{ s.feedback }}</span>
        </div>
      </div>

      <!-- Reference example -->
      <details class="ref-example">
        <summary>📖 查看参考范例</summary>
        <div class="ref-content">
          <div v-for="(v,k) in scenarios[current].reference" :key="k" class="ref-field">
            <strong>{{ {title:'标题',steps:'复现步骤',expected:'预期结果',actual:'实际结果',severity:'严重程度',environment:'测试环境'}[k] }}</strong>
            <p>{{ v }}</p>
          </div>
        </div>
      </details>

      <button v-if="result.grade !== 'excellent'" class="btn-outline" style="margin-top:12px;width:100%;justify-content:center;" @click="result=null">
        🔄 修改后重新提交
      </button>
      <button v-else class="btn-primary" style="margin-top:12px;width:100%;justify-content:center;" @click="selectScenario((current+1)%scenarios.length)">
        ▶ 下一个场景
      </button>
    </div>

    <!-- Bonus: Bug Triage -->
    <div class="card" style="margin-top:var(--space-xl);">
      <h3 style="margin-bottom:10px;font-size:.9rem;">🏥 Bug 优先级分诊</h3>
      <p class="desc">5个Bug，你只有3个开发。按 P0→P4 排序。</p>
      <div class="triage-list">
        <div v-for="(b,i) in triageBugs" :key="i" class="triage-item" :class="{ ranked: triageRanks[i] !== null }">
          <span class="triage-id">#{{ i+1 }}</span>
          <div class="triage-info">
            <strong>{{ b.title }}</strong>
            <span>{{ b.context }}</span>
          </div>
          <select v-model="triageRanks[i]" class="triage-rank">
            <option :value="null">--</option>
            <option value="P0">P0</option><option value="P1">P1</option><option value="P2">P2</option><option value="P3">P3</option><option value="P4">P4</option>
          </select>
        </div>
      </div>
      <button class="btn-primary" style="width:100%;justify-content:center;padding:10px;margin-top:10px;" @click="checkTriage" :disabled="triageRanks.includes(null)">提交分诊</button>
      <div v-if="triageResult" class="triage-result" :class="triageResult.allCorrect ? 'pass' : 'fail'">
        <h4>{{ triageResult.allCorrect ? '🎉 全部分类正确！' : '📝 正确率 ' + triageResult.pct + '%' }}</h4>
        <div v-for="(b,i) in triageBugs" :key="i" class="triage-fb">
          <span :class="triageRanks[i]===b.correct ? 'correct' : 'wrong'">#{{ i+1 }}: {{ triageRanks[i] || '未选' }} {{ triageRanks[i]===b.correct ? '✅' : '→ 应为 '+b.correct }}</span>
          <span class="triage-why">{{ b.reason }}</span>
        </div>
      </div>
    </div>

    <!-- Bonus: Bug Report Comparison -->
    <div class="card" style="margin-top:var(--space-lg);">
      <h3 style="margin-bottom:10px;font-size:.9rem;">⚖️ Bug报告对比</h3>
      <p class="desc">同一个Bug，两份报告。哪份更好？为什么？</p>
      <div class="compare-grid">
        <div class="compare-col" :class="{ chosen: compareChoice===0, reveal: compareResult }" @click="compareChoice=0">
          <h4>报告 A</h4>
          <p><strong>标题：</strong>{{ compareReports[0].title }}</p>
          <p><strong>步骤：</strong>{{ compareReports[0].steps }}</p>
          <p><strong>实际：</strong>{{ compareReports[0].actual }}</p>
        </div>
        <div class="compare-col" :class="{ chosen: compareChoice===1, reveal: compareResult }" @click="compareChoice=1">
          <h4>报告 B</h4>
          <p><strong>标题：</strong>{{ compareReports[1].title }}</p>
          <p><strong>步骤：</strong>{{ compareReports[1].steps }}</p>
          <p><strong>实际：</strong>{{ compareReports[1].actual }}</p>
        </div>
      </div>
      <button class="btn-primary" style="width:100%;justify-content:center;padding:10px;margin-top:10px;" @click="checkCompare" :disabled="compareChoice===null">确认选择</button>
      <div v-if="compareResult" class="triage-result" :class="compareResult.correct ? 'pass' : 'fail'">
        <h4>{{ compareResult.correct ? '✅ 正确！' : '❌ 不对。' }}</h4>
        <p>{{ compareResult.correct ? 'B的标题包含关键信息（模块+症状+条件），步骤可复现，实际结果精确（报错信息+截图引用）。A太模糊——「不好使」不是Bug描述。' : 'B更好——标题清晰定位问题，步骤编号可复现，实际结果包含报错文本。A只说「不好使」——没有可操作的信息。' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const current = ref(0)

const scenarios = [
  {
    label: '🔐 登录崩溃', module: 'Auth', trueSeverity: 'p0',
    title: '密码含特殊字符时登录页崩溃',
    context: '用户反馈：密码中包含 & 符号时，点击登录后整个页面白屏，必须刷新才能恢复。Chrome 120, Windows 11, 应用版本 v2.3.1。',
    visual: `<div style="background:#1a1a2e;border-radius:6px;padding:12px;font-family:monospace;font-size:.72rem;color:#ef4444;line-height:1.6;">
Uncaught SyntaxError: Unexpected token '&' in JSON at position 47<br>
&nbsp;&nbsp;at JSON.parse (&lt;anonymous&gt;)<br>
&nbsp;&nbsp;at login (auth.js:23:28)<br>
&nbsp;&nbsp;at HTMLButtonElement.onclick (login.html:15)
</div>`,
    reference: {
      title: '[登录] 密码含 & 符号时，点击登录触发 JSON 解析异常导致页面白屏',
      steps: '1. 打开登录页 http://app.example.com/login\n2. 输入用户名: testuser\n3. 输入密码: pass&word\n4. 点击「登录」按钮',
      expected: '要么登录成功跳转首页，要么显示「用户名或密码错误」提示',
      actual: '页面白屏。Console 报错: Uncaught SyntaxError: Unexpected token \'&\' in JSON。刷新后恢复正常。',
      severity: 'P0 - 阻塞',
      environment: 'Chrome 120.0.6099 / Windows 11 Pro 23H2 / 应用版本 v2.3.1 / Screen 1920×1080',
    },
  },
  {
    label: '📊 数据显示错误', module: 'Dashboard', trueSeverity: 'p1',
    title: 'Dashboard 统计数据在切换时间范围后不一致',
    context: '测试发现：先选择「本月」，显示订单数 156。切换到「本周」显示 42，再切回「本月」显示 89 —— 同一个月的数据两次显示不同。',
    visual: `<div style="display:flex;gap:8px;font-family:monospace;font-size:.7rem;">
<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:6px;padding:10px;flex:1;text-align:center;">
  <span style="color:#991b1b;">第1次「本月」</span><br>
  <strong style="font-size:1.4rem;color:#dc2626;">156</strong><br>
  <span style="color:#991b1b;">订单数</span>
</div>
<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:6px;padding:10px;flex:1;text-align:center;">
  <span style="color:#991b1b;">第2次「本月」</span><br>
  <strong style="font-size:1.4rem;color:#dc2626;">89</strong><br>
  <span style="color:#991b1b;">订单数</span>
</div>
</div>`,
    reference: {
      title: '[Dashboard] 时间范围筛选器存在缓存污染——切回「本月」后数据与首次加载不一致',
      steps: '1. 登录，进入 Dashboard 页面\n2. 默认显示「本月」数据，记录订单数=156\n3. 点击时间筛选器，选择「本周」\n4. 记录本周数据=42\n5. 再次点击时间筛选器，选择「本月」',
      expected: '第二次「本月」应显示与第一次相同的数据 (156)',
      actual: '第二次「本月」显示 89，与第一次不一致。怀疑前端缓存或API参数去重逻辑有bug。',
      severity: 'P1 - 严重',
      environment: 'Chrome 120 / macOS 14.2 / 应用版本 v2.3.1',
    },
  },
  {
    label: '⚡ 竞态条件', module: 'Search', trueSeverity: 'p1',
    title: '快速连续输入时搜索结果错乱',
    context: '在搜索框快速输入 "test" 时，先输入 t-e-s 很慢，结果正常。但快速连续敲击 t-e-s-t 后，最终显示的是 "tes" 的搜索结果而不是 "test" 的结果。',
    visual: `<div style="font-family:monospace;font-size:.72rem;color:#a0a0b8;line-height:2;">
Request 1: GET /api/search?q=t &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ 200 OK (300ms)<br>
Request 2: GET /api/search?q=te &nbsp;&nbsp;&nbsp;→ 200 OK (250ms)<br>
Request 3: GET /api/search?q=tes &nbsp;&nbsp;→ 200 OK (420ms) ← 最慢<br>
Request 4: GET /api/search?q=test &nbsp;→ 200 OK (80ms) &nbsp;← 最快，但被 #3 覆盖
</div>`,
    reference: {
      title: '[搜索] 快速连续输入时，前一个慢请求覆盖后一个快请求，导致搜索结果与输入不一致',
      steps: '1. 打开任意有搜索功能的页面\n2. 在搜索框中快速连续输入 "test"（每字符间隔 <100ms）\n3. 观察搜索结果',
      expected: '最终显示 "test" 的搜索结果',
      actual: '显示 "tes" 的搜索结果。原因：GET /api/search?q=tes 的响应(420ms)比 GET /api/search?q=test 的响应(80ms)慢，后到达的旧响应覆盖了新响应。典型的竞态条件 bug。',
      severity: 'P1 - 严重',
      environment: 'Chrome 120 / Windows 11 / 应用版本 v2.3.1 / 网络: 4G',
    },
  },
]

const report = reactive({ title: '', steps: '', expected: '', actual: '', severity: '', environment: '' })
const result = ref(null)

// Bug Triage
const triageRanks = ref([null, null, null, null, null])
const triageResult = ref(null)
const triageBugs = [
  { title: '支付成功后余额未扣款', context: '生产环境，影响所有用户。已持续3小时。', correct: 'P0', reason: 'P0—阻塞核心业务（支付），影响100%用户，持续3小时。必须立即修复。' },
  { title: '个人中心头像上传失败', context: '部分用户（约5%），仅影响头像更新。', correct: 'P3', reason: 'P3—轻微。仅影响部分用户的非核心功能（头像），有替代方案（默认头像）。' },
  { title: '搜索框placeholder文字拼写错误', context: '全量用户可见，但不影响功能。', correct: 'P4', reason: 'P4—建议。纯UI文案错误，不影响功能，不阻塞任何流程。可以在下个迭代修复。' },
  { title: '订单列表偶尔显示「加载失败」', context: '约20%用户遇到，刷新后恢复。API偶发超时。', correct: 'P1', reason: 'P1—严重。影响核心功能（订单），20%用户可见，但刷新可恢复（有workaround）。需24小时内修复。' },
  { title: '管理后台「删除用户」按钮无确认弹窗', context: '仅管理员可见，操作不可逆。', correct: 'P1', reason: 'P1—严重。操作不可逆（删除用户），虽然影响范围小（仅管理员），但后果严重。' },
]

function checkTriage() {
  const correct = triageBugs.filter((b, i) => triageRanks.value[i] === b.correct).length
  triageResult.value = { allCorrect: correct === 5, pct: Math.round(correct / 5 * 100) }
}

// Bug Report Comparison
const compareChoice = ref(null), compareResult = ref(null)
const compareReports = [
  { title: '登录不好使', steps: '打开页面，输入账号密码，点登录，然后就不好使了', actual: '就是登录不上去' },
  { title: '[登录] Chrome 120环境下，正确账号+错误密码点击登录后页面白屏（Console报错）', steps: '1. 打开登录页\n2. 输入账号 admin\n3. 输入错误密码 wrongpass\n4. 点击登录按钮', actual: '页面白屏。Console报错：Uncaught TypeError: Cannot read property \'message\' of undefined at login.js:47。预期应显示「用户名或密码错误」提示。' },
]
function checkCompare() { compareResult.value = { correct: compareChoice.value === 1 } }

function selectScenario(i) {
  current.value = i
  report.title = ''; report.steps = ''; report.expected = ''; report.actual = ''; report.severity = ''; report.environment = ''
  result.value = null
}

function scoreField(value, minLen, goodLen, maxScore, checks) {
  let score = 0
  if (!value || !value.trim()) return { score: 0, max: maxScore, pct: 0, feedback: '未填写' }
  const v = value.trim()
  if (v.length >= minLen) score += Math.floor(maxScore * 0.4)
  if (v.length >= goodLen) score += Math.floor(maxScore * 0.3)
  for (const [pattern, desc, pts] of checks) {
    if (typeof pattern === 'string' ? v.includes(pattern) : pattern.test(v)) {
      score += Math.floor(maxScore * pts)
    } else {
      return { score: Math.min(score, maxScore), max: maxScore, pct: Math.min(100, Math.round(score/maxScore*100)), feedback: desc }
    }
  }
  return { score: Math.min(score, maxScore), max: maxScore, pct: Math.min(100, Math.round(score/maxScore*100)), feedback: score >= maxScore * 0.8 ? null : '可以更详细' }
}

function submitReport() {
  const scores = {
    title: { ...scoreField(report.title, 10, 20, 25, [
      [/\[.+\]/, '缺少模块标签 [模块名]', 0.3],
      [/[a-zA-Z]/, '英文关键词有助于搜索', 0.15],
      ['.{15,}', '标题太短，缺少关键信息', 0.15],
    ]), label: '标题 (25分)' },

    steps: { ...scoreField(report.steps, 30, 60, 25, [
      [/\d\./, '步骤没有编号', 0.25],
      [/http|页面|点击|输入/, '缺少具体操作描述', 0.25],
      ['.{40,}', '步骤太简略', 0.1],
    ]), label: '复现步骤 (25分)' },

    expected: { ...scoreField(report.expected, 8, 15, 15, [
      [/应|应该|期望|正确/, '缺少预期行为关键词', 0.4],
      ['.{10,}', '预期结果太短', 0.2],
    ]), label: '预期结果 (15分)' },

    actual: { ...scoreField(report.actual, 8, 20, 15, [
      [/错误|报错|白屏|显示|异常|返回/, '缺少实际异常描述', 0.4],
      ['.{10,}', '实际结果太短', 0.2],
    ]), label: '实际结果 (15分)' },

    severity: { ...scoreField(report.severity, 1, 3, 10, [
      [/P[0-4]/, '请选择 P0-P4 严重等级', 0.6],
      [/阻塞|严重|一般|轻微|建议/, '缺少严重程度说明', 0.2],
    ]), label: '严重程度 (10分)' },

    environment: { ...scoreField(report.environment, 5, 10, 10, [
      [/[0-9]/, '缺少版本号', 0.3],
      [/Chrome|Safari|Firefox|Edge|iOS|Android|Windows|macOS|Linux/, '缺少浏览器/OS信息', 0.4],
    ]), label: '测试环境 (10分)' },
  }

  const total = Object.values(scores).reduce((sum, s) => sum + s.score, 0)
  const grade = total >= 85 ? 'excellent' : total >= 60 ? 'good' : 'needs-work'
  result.value = { scores, total, grade }
}
</script>

<style scoped>
.lab-page { max-width: 800px; margin: 0 auto; }

.scenario-bar { display: flex; gap: 8px; margin-bottom: var(--space-md); flex-wrap: wrap; }
.scenario-btn {
  padding: 8px 16px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .8rem; font-weight: 500;
  transition: all var(--fast); font-family: var(--font-sans);
}
.scenario-btn:hover { border-color: var(--primary); }
.scenario-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }

.scenario-desc { position: relative; }
.sd-header { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }
.sd-badge { padding: 3px 10px; border-radius: 4px; background: var(--primary-light); color: var(--primary); font-size: .72rem; font-weight: 600; }
.sd-severity { padding: 3px 10px; border-radius: 4px; font-size: .7rem; font-weight: 700; }
.sd-severity.sev-p0 { background: #fef2f2; color: #dc2626; }
.sd-severity.sev-p1 { background: #fffbeb; color: #d97706; }
.sd-severity.sev-p2 { background: #eff6ff; color: #2563eb; }
.scenario-desc h3 { font-size: 1rem; margin-bottom: 6px; }
.sd-context { font-size: .84rem; color: var(--text-secondary); line-height: 1.6; }

.field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; }
.field label { font-size: .78rem; font-weight: 600; color: var(--text-secondary); }
.hint { font-weight: 400; color: var(--text-muted); font-size: .72rem; }
.form-input {
  padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .86rem; font-family: var(--font-sans); outline: none; background: var(--surface);
  color: var(--text); resize: vertical; line-height: 1.6; width: 100%;
  transition: border-color var(--fast);
}
.form-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
select.form-input { cursor: pointer; }
.field-row { display: flex; gap: 12px; }
@media (max-width: 600px) { .field-row { flex-direction: column; } }

.result-card.excellent { border-color: var(--success); }
.result-card.good { border-color: var(--primary); }
.result-card.needs-work { border-color: var(--warning); }

.result-header { display: flex; gap: 14px; align-items: center; margin-bottom: 20px; }
.result-grade { font-size: 2.5rem; }
.result-header h2 { font-size: 1.2rem; }
.result-header p { font-size: .84rem; color: var(--text-secondary); }

.score-breakdown { display: flex; flex-direction: column; gap: 10px; }
.score-row { display: grid; grid-template-columns: 100px 1fr 40px; gap: 12px; align-items: center; font-size: .8rem; }
.score-label { font-weight: 500; color: var(--text-secondary); }
.score-bar-track { height: 6px; background: var(--border-light); border-radius: 3px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 3px; transition: width .6s var(--ease); }
.score-bar-fill.green { background: var(--success); }
.score-bar-fill.yellow { background: var(--warning); }
.score-bar-fill.red { background: var(--danger); }
.score-num { font-weight: 700; font-family: var(--font-mono); font-size: .82rem; text-align: right; }
.score-feedback { grid-column: 2; font-size: .72rem; color: var(--warning); font-weight: 500; }

.ref-example { margin-top: 20px; }
.ref-example summary { cursor: pointer; color: var(--primary); font-weight: 500; font-size: .84rem; }
.ref-content { margin-top: 10px; }
.ref-field { margin-bottom: 10px; }
.ref-field strong { display: block; font-size: .76rem; color: var(--text-muted); margin-bottom: 2px; text-transform: uppercase; letter-spacing: .5px; }
.ref-field p { font-size: .84rem; color: var(--text); line-height: 1.6; background: var(--bg); padding: 8px 12px; border-radius: 6px; }

.triage-list { display: flex; flex-direction: column; gap: 6px; }
.triage-item { display: flex; gap: 10px; align-items: center; padding: 10px 14px; background: var(--bg); border-radius: var(--radius); border: 1px solid var(--border); }
.triage-item.ranked { border-color: var(--primary); }
.triage-id { font-weight: 700; font-family: var(--font-mono); font-size: .78rem; color: var(--text-muted); min-width: 28px; }
.triage-info { flex: 1; }
.triage-info strong { display: block; font-size: .82rem; }
.triage-info span { font-size: .74rem; color: var(--text-secondary); }
.triage-rank { padding: 4px 8px; border: 1px solid var(--border); border-radius: 4px; font-size: .74rem; font-family: var(--font-mono); background: var(--surface); color: var(--text); cursor: pointer; }

.triage-result { margin-top: 10px; padding: 14px; border-radius: var(--radius); }
.triage-result.pass { background: var(--success-light); border: 1px solid var(--success); }
.triage-result.fail { background: var(--warning-light); border: 1px solid var(--warning); }
.triage-result h4 { font-size: .86rem; margin-bottom: 8px; }
.triage-fb { margin-bottom: 4px; }
.triage-fb .correct { font-size: .78rem; color: #059669; font-weight: 500; }
.triage-fb .wrong { font-size: .78rem; color: #dc2626; font-weight: 500; }
.triage-why { display: block; font-size: .73rem; color: var(--text-secondary); margin-top: 2px; }

.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.compare-col { border: 2px solid var(--border); border-radius: var(--radius); padding: 14px; cursor: pointer; transition: all var(--fast); font-size: .78rem; line-height: 1.6; }
.compare-col:hover { border-color: var(--primary); }
.compare-col.chosen { border-color: var(--primary); background: var(--primary-light); }
.compare-col h4 { font-size: .86rem; margin-bottom: 8px; }
.compare-col strong { font-size: .76rem; color: var(--text-muted); }
.compare-col.reveal { border-color: var(--success); }
.compare-col.reveal.chosen { border-color: var(--success); background: var(--success-light); }
</style>
