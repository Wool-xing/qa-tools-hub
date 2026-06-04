<template>
  <div class="lab-page">
    <div class="tab-bar">
      <button v-for="(t, i) in tabs" :key="i" class="tab-btn" :class="{ active: activeTab === i }" @click="activeTab = i">{{ t }}</button>
    </div>

    <!-- ═══════════════ TAB 0: 变异算子沙盒 ═══════════════ -->
    <div v-if="activeTab === 0" class="tab-content">
      <div class="card" style="margin-bottom:14px;">
        <label class="field-label">选择代码片段</label>
        <select v-model="sandboxSnippetIdx" class="field-select" @change="sandboxResult = null; sandboxOp = null">
          <option v-for="(s, i) in snippets" :key="s.id" :value="i">{{ s.name }}</option>
        </select>
        <p class="spec-desc" style="margin-top:6px;">{{ snippets[sandboxSnippetIdx].weakness }}</p>
      </div>

      <div class="sandbox-two-col">
        <div class="card">
          <h3 class="card-title">📝 原始代码</h3>
          <pre class="code-block">{{ snippets[sandboxSnippetIdx].code }}</pre>
          <h3 class="card-title" style="margin-top:14px;">🧪 现有测试</h3>
          <pre class="code-block test-block">{{ snippets[sandboxSnippetIdx].testCode }}</pre>
        </div>
        <div class="card">
          <h3 class="card-title">🔧 选择变异算子</h3>
          <div class="op-grid">
            <button
              v-for="op in snippets[sandboxSnippetIdx].mutations"
              :key="op.id"
              class="op-btn"
              :class="{ selected: sandboxOp?.id === op.id }"
              @click="sandboxOp = op; sandboxResult = null"
            >{{ op.operator }}</button>
          </div>
          <button class="btn-primary" style="margin-top:16px;width:100%;justify-content:center;" :disabled="!sandboxOp" @click="applyMutation">
            🧬 注入变异
          </button>
        </div>
      </div>

      <div v-if="sandboxResult" class="card result-card" :class="sandboxResult.killed ? 'result-pass' : 'result-fail'" style="margin-top:14px;">
        <div class="mutant-verdict">
          <span class="mutant-icon">{{ sandboxResult.killed ? '💀' : '🧟' }}</span>
          <div>
            <div class="mutant-status" :class="sandboxResult.killed ? 'text-success' : 'text-danger'">
              {{ sandboxResult.killed ? '变异体被杀死 (KILLED)' : '变异体存活 (SURVIVED)' }}
            </div>
            <p class="mutant-explain">{{ sandboxResult.explanation }}</p>
          </div>
        </div>
        <div style="margin-top:12px;">
          <span class="hint-text">变异后代码：</span>
          <pre class="code-block mutated">{{ sandboxResult.mutatedCode }}</pre>
        </div>
      </div>
    </div>

    <!-- ═══════════════ TAB 1: 杀灭率计算器 ═══════════════ -->
    <div v-if="activeTab === 1" class="tab-content">
      <div class="card" style="margin-bottom:14px;">
        <label class="field-label">选择代码片段</label>
        <select v-model="killRateSnippetIdx" class="field-select" @change="resetKillRate">
          <option v-for="(s, i) in snippets" :key="s.id" :value="i">{{ s.name }}</option>
        </select>
      </div>

      <div class="card" style="margin-bottom:14px;">
        <h3 class="card-title">📊 杀灭率</h3>
        <div class="kill-bar-wrap">
          <div class="kill-bar">
            <div class="kill-bar-fill" :style="{ width: killRatePct + '%' }" :class="killRateColor"></div>
          </div>
          <span class="kill-bar-label">{{ killRatePct }}%</span>
        </div>
        <p class="hint-text">{{ killStats.killed }} 杀灭 · {{ killStats.survived }} 存活 · 共 {{ killStats.total }} 变异体</p>
        <div v-if="killRatePct >= 95" class="kill-complete">🎉 达标！杀灭率 ≥ 95%</div>
      </div>

      <div class="card" style="margin-bottom:14px;">
        <h3 class="card-title">🧬 变异体状态</h3>
        <div class="mutant-list">
          <div v-for="m in killRateMutants" :key="m.id" class="mutant-row" :class="m.killed ? 'mutant-dead' : 'mutant-alive'">
            <span class="mutant-tag">{{ m.killed ? '💀' : '🧟' }}</span>
            <span class="mutant-op-name">{{ m.operator }}</span>
            <code class="mutant-code-snip">{{ m.mutatedBody }}</code>
          </div>
        </div>
      </div>

      <div class="card" style="margin-bottom:14px;">
        <h3 class="card-title">✍️ 编写改进的测试</h3>
        <p class="hint-text" style="margin-bottom:10px;">为以下函数参数添加测试用例，填补测试缺口</p>
        <div class="add-test-row">
          <span class="fn-sig">{{ snippets[killRateSnippetIdx].fnName }}(</span>
          <input v-model="newTestArgs" :placeholder="snippets[killRateSnippetIdx].paramHint" class="test-arg-input" @keyup.enter="addTestCase" />
          <span>)</span>
          <span style="margin:0 6px;">→</span>
          <input v-model="newTestExpected" placeholder="期望值" class="test-expected-input" @keyup.enter="addTestCase" />
          <button class="btn-primary btn-sm" @click="addTestCase">+ 添加</button>
        </div>
        <div v-if="userTestCases.length" class="user-tests-list">
          <div v-for="(tc, i) in userTestCases" :key="i" class="user-test-row">
            <code>{{ snippets[killRateSnippetIdx].fnName }}({{ tc.args.join(', ') }}) → {{ tc.expected }}</code>
            <button class="btn-ghost btn-sm" @click="userTestCases.splice(i, 1)">✕</button>
          </div>
        </div>
        <div class="toolbar">
          <span class="hint-text">{{ userTestCases.length ? userTestCases.length + ' 条测试' : '尚未添加测试' }}</span>
          <button class="btn-primary" :disabled="!userTestCases.length" @click="reRunKillRate">🔄 重新运行</button>
        </div>
      </div>
    </div>

    <!-- ═══════════════ TAB 2: 等价变异体检测 ═══════════════ -->
    <div v-if="activeTab === 2" class="tab-content">
      <div class="card" style="margin-bottom:14px;">
        <div class="eq-info">
          <span>进度：{{ eqAnswered }} / {{ equivalentMutants.length }}</span>
          <span>得分：{{ eqScore }} / {{ eqAnswered }}</span>
        </div>
      </div>

      <div v-for="(em, i) in equivalentMutants" :key="i" class="card" style="margin-bottom:10px;" :class="{ 'eq-correct': em.userChoice !== undefined && em.userChoice === em.equivalent, 'eq-wrong': em.userChoice !== undefined && em.userChoice !== em.equivalent }">
        <div class="eq-pair">
          <div class="eq-side">
            <span class="eq-label">原始</span>
            <code class="eq-code">{{ em.original }}</code>
          </div>
          <span class="eq-arrow">→</span>
          <div class="eq-side">
            <span class="eq-label">变异</span>
            <code class="eq-code">{{ em.mutated }}</code>
          </div>
        </div>
        <div v-if="em.userChoice === undefined" class="eq-actions">
          <button class="btn-equiv btn-equiv-yes" @click="answerEquivalent(i, true)">✅ 等效变异</button>
          <button class="btn-equiv btn-equiv-no" @click="answerEquivalent(i, false)">❌ 非等效变异</button>
        </div>
        <div v-else class="eq-feedback" :class="em.userChoice === em.equivalent ? 'fb-correct' : 'fb-wrong'">
          <strong>{{ em.userChoice === em.equivalent ? '✅ 正确！' : '❌ 错误！' }}</strong>
          <p>{{ em.explanation }}</p>
        </div>
      </div>

      <div v-if="eqAnswered === equivalentMutants.length" class="card result-card" :class="eqScore >= 5 ? 'result-pass' : 'result-fail'">
        <div class="score-big">{{ eqScore }}<span class="score-unit">/{{ equivalentMutants.length }}</span></div>
        <p style="text-align:center;">{{ eqScore >= 5 ? '出色！你对等价变异体有很好的理解。' : '继续练习，等价变异体是变异测试中的关键概念。' }}</p>
        <div style="text-align:center;margin-top:12px;">
          <button class="btn-ghost" @click="resetEquivalent">🔄 重新挑战</button>
        </div>
      </div>
    </div>

    <!-- ═══════════════ TAB 3: 测试弱点分析 ═══════════════ -->
    <div v-if="activeTab === 3" class="tab-content">
      <div class="card" style="margin-bottom:14px;">
        <div class="eq-info">
          <span>第 {{ weaknessRound + 1 }} / {{ weaknessRounds.length }} 轮</span>
          <span>得分：{{ weaknessScore }} / {{ weaknessRound }}</span>
        </div>
      </div>

      <div v-if="weaknessRound < weaknessRounds.length" class="card" style="margin-bottom:14px;">
        <div class="weakness-scenario">
          <p class="weakness-desc">{{ weaknessRounds[weaknessRound].scenario }}</p>
          <pre class="code-block" style="margin-top:8px;">{{ weaknessRounds[weaknessRound].code }}</pre>
          <p class="hint-text" style="margin-top:6px;">变异：<code>{{ weaknessRounds[weaknessRound].mutation }}</code> — 测试全部通过，变异存活。</p>
        </div>
        <h3 class="card-title" style="margin-top:14px;">测试的弱点是什么？</h3>
        <div class="weakness-options">
          <button
            v-for="(opt, oi) in weaknessRounds[weaknessRound].options"
            :key="oi"
            class="weakness-opt-btn"
            :class="{ 'opt-correct': weaknessResult !== null && oi === weaknessRounds[weaknessRound].correct, 'opt-wrong': weaknessResult !== null && weaknessChoice === oi && oi !== weaknessRounds[weaknessRound].correct, 'opt-selected': weaknessChoice === oi }"
            :disabled="weaknessResult !== null"
            @click="answerWeakness(oi)"
          >{{ ['A', 'B', 'C', 'D'][oi] }}. {{ opt }}</button>
        </div>
        <div v-if="weaknessResult !== null" class="eq-feedback" :class="weaknessResult ? 'fb-correct' : 'fb-wrong'">
          <strong>{{ weaknessResult ? '✅ 正确！' : '❌ 错误！' }}</strong>
          <p>{{ weaknessRounds[weaknessRound].explanation }}</p>
          <button class="btn-primary btn-sm" style="margin-top:10px;" @click="nextWeakness">下一轮 →</button>
        </div>
      </div>

      <div v-else class="card result-card" :class="weaknessScore >= 4 ? 'result-pass' : 'result-fail'">
        <div class="score-big">{{ weaknessScore }}<span class="score-unit">/{{ weaknessRounds.length }}</span></div>
        <p style="text-align:center;">{{ weaknessScore >= 4 ? '优秀！你掌握了测试弱点分析的核心思维。' : '继续练习——识别测试缺口是提高测试质量的关键技能。' }}</p>
        <div style="text-align:center;margin-top:12px;">
          <button class="btn-ghost" @click="resetWeakness">🔄 重新挑战</button>
        </div>
      </div>
    </div>

    <!-- ═══════════════ TAB 4: 变异分数热力图 ═══════════════ -->
    <div v-if="activeTab === 4" class="tab-content">
      <div class="card" style="margin-bottom:14px;">
        <h3 class="card-title">📁 项目文件变异分数</h3>
        <p class="hint-text">模拟一个真实项目的逐文件变异测试报告。颜色越深 = 分数越低 = 测试越弱。</p>
      </div>

      <div class="heatmap-grid">
        <div v-for="f in heatmapFiles" :key="f.name" class="heatmap-file" :style="{ background: heatmapBg(f.score) }">
          <div class="hf-top">
            <span class="hf-icon">{{ f.icon }}</span>
            <span class="hf-name">{{ f.name }}</span>
          </div>
          <div class="hf-score">{{ f.score }}%</div>
          <div class="hf-bar-bg">
            <div class="hf-bar-fill" :style="{ width: f.score + '%', background: heatmapBar(f.score) }"></div>
          </div>
          <div class="hf-detail">{{ f.killed }}/{{ f.total }} 杀灭</div>
        </div>
      </div>

      <div class="card" style="margin-top:14px;">
        <h3 class="card-title">🎯 哪 2 个文件需要优先改进测试？</h3>
        <div class="heatmap-pick">
          <select v-model="heatmapPick1" class="field-select" style="flex:1;">
            <option value="">-- 选择第一个文件 --</option>
            <option v-for="f in heatmapFiles" :key="f.name" :value="f.name">{{ f.name }} ({{ f.score }}%)</option>
          </select>
          <select v-model="heatmapPick2" class="field-select" style="flex:1;">
            <option value="">-- 选择第二个文件 --</option>
            <option v-for="f in heatmapFiles" :key="f.name" :value="f.name">{{ f.name }} ({{ f.score }}%)</option>
          </select>
          <button class="btn-primary" :disabled="!heatmapPick1 || !heatmapPick2" @click="submitHeatmap">✓ 提交</button>
        </div>
        <div v-if="heatmapResult !== null" class="eq-feedback" :class="heatmapResult ? 'fb-correct' : 'fb-wrong'" style="margin-top:12px;">
          <strong>{{ heatmapResult ? '✅ 正确！' : '❌ 不正确。' }}</strong>
          <p>优先改进测试分数最低的文件：notification.js (35%) 和 payment.js (45%)。变异分数越低，说明测试发现 bug 的能力越弱。</p>
          <button v-if="!heatmapResult" class="btn-ghost btn-sm" style="margin-top:6px;" @click="heatmapResult = null; heatmapPick1 = ''; heatmapPick2 = ''">重试</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const tabs = ['🔧 变异算子沙盒', '📊 杀灭率计算器', '⚖️ 等价变异体检测', '🔍 测试弱点分析', '🗺️ 变异分数热力图']
const activeTab = ref(0)

// ═══════════════ SNIPPETS ═══════════════
const snippets = [
  {
    id: 1, name: 'isAdult — 边界测试', fnName: 'isAdult', params: ['age'],
    paramHint: '年龄, 如 18',
    code: 'function isAdult(age) {\n  return age > 18;\n}',
    testCode: '// 现有测试：仅覆盖 age=20\ntest("isAdult", () => {\n  expect(isAdult(20)).toBe(true);\n});',
    weakness: '弱点：测试仅检查 age=20（远超边界），边界值 age=18 完全未被测试。',
    originalBody: 'age > 18',
    originalTests: [{ args: [20], expected: true }],
    mutations: [
      { id: 'gt-gte', operator: '> → >=', mutatedBody: 'age >= 18', survives: true, explanation: '测试仅检查 age=20。age=18 处的边界行为从未被验证，改变比较运算符对 age=20 无影响。' },
      { id: 'gt-lt', operator: '> → <', mutatedBody: 'age < 18', survives: false, explanation: 'age=20 时 20<18=false，测试期望 true，变异体被杀死。' },
      { id: '18-21', operator: '18 → 21', mutatedBody: 'age > 21', survives: false, explanation: 'age=20 时 20>21=false，测试失败，变异体被杀死。' },
      { id: 'gt-lte', operator: '> → <=', mutatedBody: 'age <= 18', survives: false, explanation: 'age=20 时 20<=18=false，与期望冲突，变异体被杀死。' },
    ],
  },
  {
    id: 2, name: 'calculateDiscount — 条件覆盖', fnName: 'calculateDiscount', params: ['price', 'member'],
    paramHint: '价格, true/false',
    code: 'function calculateDiscount(price, member) {\n  if (member) return price * 0.9;\n  return price;\n}',
    testCode: '// 现有测试：从未传 member=false\ntest("discount", () => {\n  expect(calculateDiscount(100, true)).toBe(90);\n});',
    weakness: '弱点：测试从未覆盖 member=false 的分支路径。',
    originalBody: '((price, member) => { if (member) return price * 0.9; return price; })',
    originalTests: [{ args: [100, true], expected: 90 }],
    mutations: [
      { id: 'remove-if', operator: '删除 if 条件', mutatedBody: '((price, member) => { return price * 0.9; })', survives: true, explanation: '无测试覆盖 member=false 路径。移除条件后 member=true 的测试仍通过，变异存活。' },
      { id: 'mul-div', operator: '* → /', mutatedBody: '((price, member) => { if (member) return price / 0.9; return price; })', survives: false, explanation: '100/0.9≈111.11 ≠ 90，测试失败，变异被杀死。' },
      { id: '09-08', operator: '0.9 → 0.8', mutatedBody: '((price, member) => { if (member) return price * 0.8; return price; })', survives: false, explanation: '100*0.8=80 ≠ 90，测试捕获了数值变化，变异被杀。' },
      { id: 'swap-cond', operator: '交换 true/false', mutatedBody: '((price, member) => { if (!member) return price * 0.9; return price; })', survives: false, explanation: 'member=true 时 !member=false，走入 else 分支返回 100，测试失败。' },
    ],
  },
  {
    id: 3, name: 'validateEmail — 输入多样性', fnName: 'validateEmail', params: ['email'],
    paramHint: 'email 字符串',
    code: 'function validateEmail(email) {\n  return email.includes("@");\n}',
    testCode: '// 现有测试：仅检查基本格式\ntest("email", () => {\n  expect(validateEmail("test@ex.com")).toBe(true);\n  expect(validateEmail("a@b")).toBe(true);\n});',
    weakness: '弱点：测试仅使用有效邮箱，未测试无效或边界格式。',
    originalBody: '((email) => email.includes("@"))',
    originalTests: [{ args: ['test@ex.com'], expected: true }, { args: ['a@b'], expected: true }],
    mutations: [
      { id: 'includes-true', operator: '返回恒真', mutatedBody: '((email) => true)', survives: true, explanation: '测试仅使用有效邮箱。返回恒真后所有测试仍通过，变异存活——缺少无效邮箱的测试。' },
      { id: 'at-to-dot', operator: '@ → .', mutatedBody: '((email) => email.includes("."))', survives: false, explanation: '"a@b" 不含 "."，email.includes(".") 返回 false，与期望 true 冲突，变异被杀。' },
      { id: 'includes-startswith', operator: 'includes → startsWith', mutatedBody: '((email) => email.startsWith("@"))', survives: false, explanation: '任意正常邮箱均不以 @ 开头，测试立即失败，变异被杀。' },
    ],
  },
  {
    id: 4, name: 'withdraw — 精确边界', fnName: 'withdraw', params: ['balance', 'amount'],
    paramHint: '余额, 取款额 如 100,100',
    code: 'function withdraw(balance, amount) {\n  if (amount <= balance) return balance - amount;\n  return balance;\n}',
    testCode: '// 现有测试：覆盖正常与超额，漏边界\ntest("withdraw", () => {\n  expect(withdraw(100, 30)).toBe(70);\n  expect(withdraw(100, 200)).toBe(100);\n});',
    weakness: '弱点：未测试 amount === balance 的精确边界（取款额恰好等于余额）。',
    originalBody: '((balance, amount) => { if (amount <= balance) return balance - amount; return balance; })',
    originalTests: [{ args: [100, 30], expected: 70 }, { args: [100, 200], expected: 100 }],
    mutations: [
      { id: 'lte-lt', operator: '<= → <', mutatedBody: '((balance, amount) => { if (amount < balance) return balance - amount; return balance; })', survives: true, explanation: '测试未覆盖 amount===balance 边界。在此边界上 <= 和 < 行为不同，但现有测试全部通过，变异存活。' },
      { id: 'minus-plus', operator: '- → +', mutatedBody: '((balance, amount) => { if (amount <= balance) return balance + amount; return balance; })', survives: false, explanation: '100+30=130 ≠ 70，测试捕获算术错误，变异被杀。' },
      { id: 'ret-0', operator: 'return balance → return 0', mutatedBody: '((balance, amount) => { if (amount <= balance) return balance - amount; return 0; })', survives: false, explanation: '超额时返回 0 而非原始余额，withdraw(100,200) 期望 100 实际为 0，变异被杀。' },
    ],
  },
]

// ═══════════════ TAB 0: 变异算子沙盒 ═══════════════
const sandboxSnippetIdx = ref(0)
const sandboxOp = ref(null)
const sandboxResult = ref(null)

function applyMutation() {
  const s = snippets[sandboxSnippetIdx.value]
  const op = sandboxOp.value
  if (!op) return
  const killed = !op.survives
  sandboxResult.value = {
    killed,
    explanation: op.explanation,
    mutatedCode: buildMutatedCode(s, op),
  }
}

function buildMutatedCode(snippet, op) {
  // Reconstruct the full code with mutated body
  const c = snippet.code
  if (snippet.id === 2) {
    // calculateDiscount — show mutated version
    if (op.id === 'remove-if') return 'function calculateDiscount(price, member) {\n  return price * 0.9;  // ← if 条件已删除\n}'
    if (op.id === 'mul-div') return 'function calculateDiscount(price, member) {\n  if (member) return price / 0.9;  // ← * 变为 /\n  return price;\n}'
    if (op.id === '09-08') return 'function calculateDiscount(price, member) {\n  if (member) return price * 0.8;  // ← 0.9 变为 0.8\n  return price;\n}'
    if (op.id === 'swap-cond') return 'function calculateDiscount(price, member) {\n  if (!member) return price * 0.9;  // ← 条件取反\n  return price;\n}'
    return c
  }
  if (snippet.id === 1) {
    if (op.id === 'gt-gte') return 'function isAdult(age) {\n  return age >= 18;  // ← > 变为 >=\n}'
    if (op.id === 'gt-lt') return 'function isAdult(age) {\n  return age < 18;  // ← > 变为 <\n}'
    if (op.id === '18-21') return 'function isAdult(age) {\n  return age > 21;  // ← 18 变为 21\n}'
    if (op.id === 'gt-lte') return 'function isAdult(age) {\n  return age <= 18;  // ← > 变为 <=\n}'
    return c
  }
  if (snippet.id === 3) {
    if (op.id === 'includes-true') return 'function validateEmail(email) {\n  return true;  // ← 永远返回 true\n}'
    if (op.id === 'at-to-dot') return 'function validateEmail(email) {\n  return email.includes(".");  // ← @ 变为 .\n}'
    if (op.id === 'includes-startswith') return 'function validateEmail(email) {\n  return email.startsWith("@");  // ← includes 变为 startsWith\n}'
    return c
  }
  if (snippet.id === 4) {
    if (op.id === 'lte-lt') return 'function withdraw(balance, amount) {\n  if (amount < balance) return balance - amount;  // ← <= 变为 <\n  return balance;\n}'
    if (op.id === 'minus-plus') return 'function withdraw(balance, amount) {\n  if (amount <= balance) return balance + amount;  // ← - 变为 +\n  return balance;\n}'
    if (op.id === 'ret-0') return 'function withdraw(balance, amount) {\n  if (amount <= balance) return balance - amount;\n  return 0;  // ← balance 变为 0\n}'
    return c
  }
  return c
}

// ═══════════════ TAB 1: 杀灭率计算器 ═══════════════
const killRateSnippetIdx = ref(0)
const userTestCases = ref([])
const newTestArgs = ref('')
const newTestExpected = ref('')
const killRateMutants = ref([])
const killStats = ref({ killed: 0, survived: 0, total: 0 })
const killRatePct = ref(0)

function initKillRate() {
  const s = snippets[killRateSnippetIdx.value]
  killRateMutants.value = s.mutations.map(m => ({
    ...m,
    killed: !m.survives,
  }))
  updateKillStats()
}

function updateKillStats() {
  const ms = killRateMutants.value
  const killed = ms.filter(m => m.killed).length
  killStats.value = { killed, survived: ms.length - killed, total: ms.length }
  killRatePct.value = ms.length ? Math.round((killed / ms.length) * 100) : 0
}

const killRateColor = computed(() => {
  if (killRatePct.value >= 95) return 'bar-green'
  if (killRatePct.value >= 70) return 'bar-yellow'
  return 'bar-red'
})

function addTestCase() {
  const s = snippets[killRateSnippetIdx.value]
  const argsStr = newTestArgs.value.trim()
  const expectedStr = newTestExpected.value.trim()
  if (!argsStr || !expectedStr) return

  let args
  try {
    args = JSON.parse('[' + argsStr + ']')
    if (!Array.isArray(args)) throw new Error()
  } catch {
    // Treat as single value or comma-separated
    args = argsStr.split(',').map(a => {
      const t = a.trim()
      if (t === 'true') return true
      if (t === 'false') return false
      const n = Number(t)
      return isNaN(n) ? t.replace(/^["']|["']$/g, '') : n
    })
  }

  let expected
  try {
    expected = JSON.parse(expectedStr)
  } catch {
    const t = expectedStr.trim()
    if (t === 'true') expected = true
    else if (t === 'false') expected = false
    else { const n = Number(t); expected = isNaN(n) ? t : n }
  }

  userTestCases.value.push({ args, expected })
  newTestArgs.value = ''
  newTestExpected.value = ''
}

function evaluateMutant(mutatedBody, params, args) {
  try {
    const fn = new Function(...params, 'return (' + mutatedBody + ')(...arguments)')
    return fn(...args)
  } catch {
    return undefined
  }
}

function reRunKillRate() {
  const s = snippets[killRateSnippetIdx.value]
  const allTests = [...s.originalTests, ...userTestCases.value]

  killRateMutants.value = s.mutations.map(m => {
    const killed = allTests.some(tc => {
      const result = evaluateMutant(m.mutatedBody, s.params, tc.args)
      return result !== tc.expected
    })
    return { ...m, killed }
  })
  updateKillStats()
}

function resetKillRate() {
  userTestCases.value = []
  initKillRate()
}

initKillRate()

// ═══════════════ TAB 2: 等价变异体检测 ═══════════════
const equivalentMutants = [
  { original: 'i++;', mutated: 'i += 1;', equivalent: true, explanation: '作为独立语句时，i++ 与 i += 1 语义完全等价，都使 i 增加 1。' },
  { original: 'i < 10', mutated: 'i <= 10', equivalent: false, explanation: '当 i=10 时，i<10 为 false，i<=10 为 true，行为不同。边界值决定了它们不等价。' },
  { original: 'return x ? a : b;', mutated: 'if (x) return a; return b;', equivalent: true, explanation: '两者控制流等价，在相同输入下返回相同结果。仅语法形式不同。' },
  { original: 'x * 2', mutated: 'x << 1', equivalent: false, explanation: '对负数、浮点数或溢出场景，位运算与乘法结果不同。例如 -1*2=-2 但 -1<<1=-2（JS 中碰巧相同），但 3.5*2=7 而 3.5<<1=6。' },
  { original: '!!x', mutated: 'Boolean(x)', equivalent: true, explanation: '!!x 与 Boolean(x) 都将任意值转换为布尔值，对所有输入返回相同结果。' },
  { original: 'a + b', mutated: 'b + a', equivalent: false, explanation: '对字符串拼接，"a"+"b"= "ab"，而 "b"+"a"= "ba"，顺序影响结果。加法交换律不适用于字符串。' },
]

const eqAnswered = ref(0)
const eqScore = ref(0)

function answerEquivalent(index, choice) {
  const em = equivalentMutants[index]
  if (em.userChoice !== undefined) return
  em.userChoice = choice
  eqAnswered.value++
  if (choice === em.equivalent) eqScore.value++
}

function resetEquivalent() {
  eqAnswered.value = 0
  eqScore.value = 0
  equivalentMutants.forEach(em => { em.userChoice = undefined })
}

// ═══════════════ TAB 3: 测试弱点分析 ═══════════════
const weaknessRounds = [
  {
    scenario: '变异将 > 改为 >=，所有测试通过。',
    code: 'function isAdult(age) { return age > 18; }',
    mutation: '> → >=',
    options: ['测试从未检查边界值 age=18', '测试用例数量不够多', '函数名不符合命名规范', '测试框架版本过旧'],
    correct: 0,
    explanation: '边界值 age=18 是 > 和 >= 行为不同的唯一位置。测试仅覆盖 age=20，无法区分这两种实现。',
  },
  {
    scenario: '变异删除了 null 检查，测试仍然全绿。',
    code: 'function getName(user) {\n  if (user === null) return "Guest";\n  return user.name;\n}',
    mutation: '移除 null 检查',
    options: ['测试从未传入 null', '测试命名不够清晰', '缺少性能测试', '未使用 TypeScript'],
    correct: 0,
    explanation: '如果 null 检查被删除且测试仍然通过，说明所有测试都传入有效 user 对象——null 路径从未被测试，是典型的空值覆盖缺失。',
  },
  {
    scenario: '变异将 price * 0.9 改为 price * 0.8，测试通过。',
    code: 'function applyDiscount(price) { return price * 0.9; }',
    mutation: '0.9 → 0.8',
    options: ['测试仅断言 "小于原价"，未检查精确金额', '测试数据量太小', '缺少并发测试', '未使用 mock'],
    correct: 0,
    explanation: '若测试只验证 "结果小于原价"，则 80 < 100 和 90 < 100 都通过。必须断言精确值才能捕获折扣率错误。',
  },
  {
    scenario: '变异将 return balance 改为 return 0，超额取款测试仍通过。',
    code: 'function withdraw(balance, amount) {\n  if (amount <= balance) return balance - amount;\n  return balance;\n}',
    mutation: 'return balance → return 0',
    options: ['超额测试未检查返回值（仅验证不抛异常）', '测试缺少 setup 阶段', '变量命名不规范', '未使用参数化测试'],
    correct: 0,
    explanation: '如果超额测试只检查 "不抛异常" 而未断言返回值，那么 return balance 和 return 0 都能通过。测试必须对返回值做精确断言。',
  },
  {
    scenario: '变异移除了正则中的 ^ 和 $ 锚点，测试全部通过。',
    code: 'function isDigits(str) { return /^\\d+$/.test(str); }',
    mutation: '/^\\d+$/ → /\\d+/',
    options: ['测试未包含部分匹配的字符串（如 "abc123def"）', '测试数量不足', '缺少集成测试', '未测试空字符串'],
    correct: 0,
    explanation: '无锚点时 "abc123def" 通过（包含数字），有锚点时失败（需全数字）。若测试从未包含此类输入，则无法区分。',
  },
  {
    scenario: '变异将 Math.max(a, b) 改为 Math.min(a, b)，测试通过。',
    code: 'function getLarger(a, b) { return Math.max(a, b); }',
    mutation: 'Math.max → Math.min',
    options: ['测试仅传入相等的值（a === b），max 与 min 结果相同', '测试框架有缓存', '函数过于简单', '缺少文档'],
    correct: 0,
    explanation: '当 a === b 时，max(a,b) = min(a,b) = a。若所有测试都传入相等参数，变异无法被检测。需要不同的输入值。',
  },
]

const weaknessRound = ref(0)
const weaknessScore = ref(0)
const weaknessChoice = ref(null)
const weaknessResult = ref(null)

function answerWeakness(choice) {
  if (weaknessResult.value !== null) return
  weaknessChoice.value = choice
  const correct = choice === weaknessRounds[weaknessRound.value].correct
  weaknessResult.value = correct
  if (correct) weaknessScore.value++
}

function nextWeakness() {
  weaknessRound.value++
  weaknessChoice.value = null
  weaknessResult.value = null
}

function resetWeakness() {
  weaknessRound.value = 0
  weaknessScore.value = 0
  weaknessChoice.value = null
  weaknessResult.value = null
}

// ═══════════════ TAB 4: 变异分数热力图 ═══════════════
const heatmapFiles = [
  { name: 'login.js', icon: '🔐', score: 92, killed: 46, total: 50 },
  { name: 'checkout.js', icon: '🛒', score: 78, killed: 39, total: 50 },
  { name: 'payment.js', icon: '💳', score: 45, killed: 18, total: 40 },
  { name: 'profile.js', icon: '👤', score: 88, killed: 37, total: 42 },
  { name: 'search.js', icon: '🔍', score: 62, killed: 28, total: 45 },
  { name: 'notification.js', icon: '🔔', score: 35, killed: 12, total: 34 },
]

const heatmapPick1 = ref('')
const heatmapPick2 = ref('')
const heatmapResult = ref(null)

function heatmapBg(score) {
  if (score >= 85) return '#f0fdf4'
  if (score >= 70) return '#fffbeb'
  if (score >= 50) return '#fff7ed'
  return '#fef2f2'
}

function heatmapBar(score) {
  if (score >= 85) return 'var(--success)'
  if (score >= 70) return 'var(--warning)'
  if (score >= 50) return '#f97316'
  return 'var(--danger)'
}

function submitHeatmap() {
  const worst = ['notification.js', 'payment.js']
  const picks = [heatmapPick1.value, heatmapPick2.value].sort()
  heatmapResult.value = picks[0] === worst[0] && picks[1] === worst[1]
}
</script>

<style scoped>
.lab-page { max-width: 860px; margin: 0 auto; }

.tab-bar { display: flex; gap: 2px; margin-bottom: var(--space-md); border-bottom: 2px solid var(--border); flex-wrap: wrap; }
.tab-btn {
  padding: 10px 18px; border: none; background: transparent; cursor: pointer;
  font-size: .84rem; font-weight: 500; color: var(--text-secondary);
  border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: all var(--fast); font-family: var(--font-sans); white-space: nowrap;
}
.tab-btn:hover { color: var(--primary); }
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 650; }

.tab-content { animation: fadeIn .2s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

.field-label { display: block; font-size: .8rem; font-weight: 600; margin-bottom: 6px; color: var(--text-secondary); }
.field-select {
  width: 100%; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .86rem; background: var(--surface); color: var(--text); outline: none;
  font-family: var(--font-sans);
}
.field-select:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.spec-desc { font-size: .78rem; color: var(--text-muted); }
.card-title { font-size: .9rem; font-weight: 650; margin-bottom: 12px; }
.card-title .hint-text { font-weight: 400; }
.hint-text { font-size: .74rem; color: var(--text-muted); }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; }

.code-block {
  padding: 14px 16px; background: #1a1a2e; color: #e5e7eb; border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .8rem; line-height: 1.7; overflow-x: auto;
  white-space: pre; margin: 0;
}
.code-block.mutated { border: 1px solid var(--danger); }
.test-block { background: #1a2e1a; }

/* Sandbox */
.sandbox-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 700px) { .sandbox-two-col { grid-template-columns: 1fr; } }

.op-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.op-btn {
  padding: 8px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--surface); cursor: pointer; font-size: .78rem; font-family: var(--font-mono);
  transition: all var(--fast); color: var(--text);
}
.op-btn:hover { border-color: var(--primary); background: var(--primary-light); }
.op-btn.selected { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 650; }

.result-card { margin-top: var(--space-md); }
.result-pass { border-left: 4px solid var(--success); }
.result-fail { border-left: 4px solid var(--danger); }

.mutant-verdict { display: flex; gap: 14px; align-items: flex-start; }
.mutant-icon { font-size: 2rem; flex-shrink: 0; }
.mutant-status { font-size: 1.05rem; font-weight: 750; margin-bottom: 4px; }
.text-success { color: var(--success); }
.text-danger { color: var(--danger); }
.mutant-explain { font-size: .82rem; color: var(--text-secondary); line-height: 1.6; }

/* Kill Rate */
.kill-bar-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.kill-bar { flex: 1; height: 20px; background: var(--border-light); border-radius: 10px; overflow: hidden; }
.kill-bar-fill { height: 100%; border-radius: 10px; transition: width .4s var(--ease); }
.kill-bar-fill.bar-green { background: var(--success); }
.kill-bar-fill.bar-yellow { background: var(--warning); }
.kill-bar-fill.bar-red { background: var(--danger); }
.kill-bar-label { font-size: 1.2rem; font-weight: 750; color: var(--text); min-width: 48px; text-align: right; }
.kill-complete {
  margin-top: 10px; padding: 10px 16px; background: var(--success-light); border-radius: var(--radius-sm);
  font-size: .9rem; font-weight: 650; color: var(--success); text-align: center;
}

.mutant-list { display: flex; flex-direction: column; gap: 6px; }
.mutant-row { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 6px; font-size: .8rem; }
.mutant-row.mutant-dead { background: #f0fdf4; }
.mutant-row.mutant-alive { background: #fef2f2; }
.mutant-tag { flex-shrink: 0; }
.mutant-op-name { font-weight: 600; min-width: 100px; color: var(--text); }
.mutant-code-snip { font-size: .76rem; color: var(--text-secondary); }

.add-test-row { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-bottom: 10px; font-family: var(--font-mono); font-size: .82rem; }
.fn-sig { color: var(--text-secondary); }
.test-arg-input {
  width: 180px; padding: 6px 10px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .8rem; font-family: var(--font-mono); background: var(--bg); color: var(--text); outline: none;
}
.test-arg-input:focus { border-color: var(--primary); }
.test-expected-input {
  width: 100px; padding: 6px 10px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .8rem; font-family: var(--font-mono); background: var(--surface); outline: none;
}
.test-expected-input:focus { border-color: var(--primary); }

.user-tests-list { margin-bottom: 10px; display: flex; flex-direction: column; gap: 4px; }
.user-test-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 6px 10px; background: var(--primary-light); border-radius: 4px; font-size: .78rem;
}

/* Equivalent Mutant */
.eq-info { display: flex; justify-content: space-between; font-size: .84rem; color: var(--text-secondary); font-weight: 550; }
.eq-pair { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.eq-side { display: flex; flex-direction: column; gap: 4px; }
.eq-label { font-size: .68rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
.eq-code { font-size: .84rem; padding: 6px 12px; background: var(--bg); border-radius: 4px; font-family: var(--font-mono); }
.eq-arrow { font-size: 1.2rem; color: var(--text-muted); }
.eq-actions { display: flex; gap: 10px; }
.btn-equiv {
  padding: 10px 22px; border-radius: var(--radius-sm); font-size: .84rem; font-weight: 600;
  cursor: pointer; border: 2px solid; transition: all var(--fast); font-family: var(--font-sans);
}
.btn-equiv-yes { background: #d1fae5; border-color: var(--success); color: #065f46; }
.btn-equiv-yes:hover { background: #a7f3d0; }
.btn-equiv-no { background: #fecaca; border-color: var(--danger); color: #991b1b; }
.btn-equiv-no:hover { background: #fca5a5; }

.eq-feedback { padding: 14px; border-radius: var(--radius-sm); margin-top: 10px; font-size: .82rem; line-height: 1.6; }
.eq-feedback.fb-correct { background: #f0fdf4; border: 1px solid #bbf7d0; }
.eq-feedback.fb-wrong { background: #fef2f2; border: 1px solid #fecaca; }
.eq-correct { border-left: 3px solid var(--success); }
.eq-wrong { border-left: 3px solid var(--danger); }

.score-big { font-size: 2.8rem; font-weight: 800; text-align: center; margin: 8px 0; }
.score-unit { font-size: 1rem; color: var(--text-muted); font-weight: 400; }

/* Weakness */
.weakness-scenario { padding: 14px; background: var(--bg); border-radius: var(--radius-sm); }
.weakness-desc { font-size: .88rem; font-weight: 550; line-height: 1.5; color: var(--text); }
.weakness-options { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
.weakness-opt-btn {
  text-align: left; padding: 12px 16px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--surface); cursor: pointer; font-size: .84rem; font-family: var(--font-sans);
  transition: all var(--fast); color: var(--text); line-height: 1.4;
}
.weakness-opt-btn:hover:not(:disabled) { border-color: var(--primary); background: var(--primary-light); }
.weakness-opt-btn:disabled { cursor: default; }
.weakness-opt-btn.opt-selected { border-color: var(--primary); }
.weakness-opt-btn.opt-correct { border-color: var(--success); background: #f0fdf4; color: #065f46; font-weight: 650; }
.weakness-opt-btn.opt-wrong { border-color: var(--danger); background: #fef2f2; color: #991b1b; }

/* Heatmap */
.heatmap-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 10px; }
.heatmap-file {
  padding: 16px; border-radius: var(--radius); border: 1px solid var(--border);
  display: flex; flex-direction: column; gap: 8px;
}
.hf-top { display: flex; align-items: center; gap: 8px; }
.hf-icon { font-size: 1.1rem; }
.hf-name { font-weight: 650; font-size: .86rem; font-family: var(--font-mono); color: var(--text); }
.hf-score { font-size: 1.6rem; font-weight: 800; color: var(--text); }
.hf-bar-bg { height: 6px; background: var(--border-light); border-radius: 3px; overflow: hidden; }
.hf-bar-fill { height: 100%; border-radius: 3px; transition: width .5s var(--ease); }
.hf-detail { font-size: .72rem; color: var(--text-muted); }

.heatmap-pick { display: flex; gap: 10px; align-items: center; margin-top: 10px; flex-wrap: wrap; }

.btn-sm { font-size: .76rem; padding: 6px 14px; }
</style>
