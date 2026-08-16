<template>
  <div class="lab-page">
    <div class="tab-bar">
      <button v-for="(t, i) in tabs" :key="i" class="tab-btn" :class="{ active: activeTab === i }" @click="activeTab = i; clearTabState()">{{ t }}</button>
    </div>

    <!-- TAB 1: 需求审查 -->
    <div v-if="activeTab === 0" class="tab-content">
      <div class="card">
        <label class="field-label">选择需求文档</label>
        <select v-model="specIndex" class="field-select" @change="reviewResults = null; editingClause = null; annotations = {}">
          <option v-for="(s, i) in specs" :key="s.id" :value="i">{{ s.icon }} {{ s.title }}</option>
        </select>
        <p class="spec-desc">{{ specs[specIndex].description }}</p>
      </div>

      <div class="card">
        <h3 class="card-title">📄 需求文档内容 <span class="hint-text">（点击可疑的句子进行标注）</span></h3>
        <div class="spec-doc">
          <div
            v-for="(clause, ci) in specs[specIndex].clauses" :key="ci"
            class="spec-clause"
            :class="clauseClasses(specIndex, ci)"
            @click="startAnnotate(specIndex, ci)"
          >
            <span class="clause-num">{{ ci + 1 }}.</span>
            <span class="clause-text">{{ clause }}</span>
            <span v-if="getAnnotation(specIndex, ci)" class="anno-badge" :class="'badge-' + catSlug(getAnnotation(specIndex, ci).category)">
              {{ getAnnotation(specIndex, ci).category }}
            </span>
          </div>
        </div>

        <div v-if="editingClause" class="anno-popup">
          <p class="anno-popup-title">选择问题类型</p>
          <div class="anno-cats">
            <button
              v-for="cat in annotationCategories" :key="cat"
              class="anno-cat-btn"
              :class="{ selected: tempCategory === cat }"
              @click="tempCategory = cat"
            >{{ catIcon(cat) }} {{ cat }}</button>
          </div>
          <input v-model="tempNote" placeholder="补充说明（可选）" class="anno-note" />
          <div class="anno-actions">
            <button class="btn-primary btn-sm" @click="confirmAnnotation">确认标注</button>
            <button v-if="getAnnotation(editingClause.si, editingClause.ci)" class="btn-ghost btn-sm" @click="removeAnnotation(editingClause.si, editingClause.ci)">🗑 删除</button>
            <button class="btn-ghost btn-sm" @click="editingClause = null">取消</button>
          </div>
        </div>

        <div class="toolbar">
          <span class="hint-text">已标注 {{ annotationCount }} 处</span>
          <button class="btn-primary" :disabled="annotationCount === 0" @click="submitReview">📝 提交评审</button>
        </div>
      </div>

      <div v-if="reviewResults" class="card result-card" :class="reviewResults.score >= 60 ? 'result-pass' : 'result-fail'">
        <h3>评审结果 — {{ specs[specIndex].title }}</h3>
        <div class="score-big">{{ reviewResults.score }}<span class="score-unit">分</span></div>
        <div class="result-detail">
          <div class="rd-row"><span>正确发现</span><span>{{ reviewResults.correctHits }} / {{ reviewResults.total }}</span></div>
          <div class="rd-row"><span>遗漏</span><span>{{ reviewResults.missed }}</span></div>
          <div class="rd-row"><span>❌ 误报</span><span>{{ reviewResults.falsePositiveCount }}</span></div>
          <div class="rd-row"><span>分类错误</span><span>{{ reviewResults.wrongCat }}</span></div>
        </div>
        <div v-if="reviewResults.missedList.length" style="margin-top:12px;">
          <p class="missed-title">遗漏的问题：</p>
          <div v-for="m in reviewResults.missedList" :key="m.ci" class="missed-item">
            <span class="missed-cat">{{ m.category }}</span>
            <span>{{ m.text }}</span>
          </div>
        </div>
        <button class="btn-ghost" style="margin-top:12px;" @click="reviewResults = null">重新审查</button>
      </div>
    </div>

    <!-- TAB 2: 边界枚举 -->
    <div v-if="activeTab === 1" class="tab-content">
      <div class="card">
        <label class="field-label">选择场景</label>
        <select v-model="ecScenario" class="field-select" @change="ecResults = null; ecAnswers = {}">
          <option v-for="(s, i) in edgeCaseScenarios" :key="i" :value="i">{{ s.title }}</option>
        </select>
        <div class="requirement-box">
          <span class="req-icon">📌</span>
          <span>{{ edgeCaseScenarios[ecScenario].requirement }}</span>
        </div>
      </div>

      <div class="card">
        <h3 class="card-title">枚举边界条件</h3>
        <p class="hint-text">为每个维度写出你想到的边界条件</p>
        <div v-for="(cat, ci) in edgeCaseScenarios[ecScenario].categories" :key="ci" class="ec-category">
          <label class="ec-cat-label">{{ cat.icon }} {{ cat.label }}</label>
          <textarea v-model="ecAnswers[ci]" :placeholder="cat.placeholder" rows="2" class="ec-textarea"></textarea>
        </div>
        <div class="toolbar">
          <span class="hint-text">已填写 {{ filledEdgeCaseCount }} / {{ edgeCaseScenarios[ecScenario].categories.length }} 项</span>
          <button class="btn-primary" :disabled="filledEdgeCaseCount === 0" @click="submitEdgeCases">📝 提交</button>
        </div>
      </div>

      <div v-if="ecResults" class="card result-card">
        <h3>边界枚举结果</h3>
        <div class="score-big">{{ ecResults.score }}<span class="score-unit">分</span></div>
        <div class="result-detail">
          <div class="rd-row"><span>命中</span><span>{{ ecResults.hits }} / {{ ecResults.total }}</span></div>
          <div class="rd-row"><span>💡 部分命中</span><span>{{ ecResults.partial }}</span></div>
          <div class="rd-row"><span>❌ 遗漏</span><span>{{ ecResults.missed }}</span></div>
        </div>
        <div style="margin-top:12px;">
          <p class="missed-title">逐项分析：</p>
          <div v-for="(d, i) in ecResults.details" :key="i" class="ec-answer-item" :class="d.status">
            <span class="ec-answer-status">{{ d.status === 'hit' ? '✅' : d.status === 'partial' ? '💡' : '❌' }}</span>
            <div style="flex:1;">
              <strong>{{ d.category }}</strong>
              <p class="ec-answer-text">{{ d.expected }}</p>
              <p v-if="d.yourAnswer" class="ec-your-answer">你的回答：{{ d.yourAnswer }}</p>
            </div>
          </div>
        </div>
        <button class="btn-ghost" style="margin-top:12px;" @click="ecResults = null">重试</button>
      </div>
    </div>

    <!-- TAB 3: 歧义检测 -->
    <div v-if="activeTab === 2" class="tab-content">
      <div v-if="!agStarted" class="card" style="text-align:center;">
        <h3 style="margin-bottom:12px;">歧义检测挑战</h3>
        <p style="color:var(--text-secondary);margin-bottom:12px;">15条需求语句 · 60秒 · 判断「模糊」还是「明确」</p>
        <p style="color:var(--text-muted);font-size:.78rem;margin-bottom:20px;">模糊词：快速、可靠、安全、用户友好、足够、合理、按需、等等、适当、高效</p>
        <button class="btn-primary btn-lg" @click="startAmbiguityGame">▶ 开始挑战</button>
      </div>

      <div v-else-if="agRound < ambiguityRounds.length" class="card" style="text-align:center;">
        <div class="ag-timer-bar">
          <div class="ag-timer-fill" :style="{ width: (agTimeLeft / 60 * 100) + '%' }" :class="{ 'timer-low': agTimeLeft <= 10 }"></div>
        </div>
        <div class="ag-info">
          <span>第 {{ agRound + 1 }} / {{ ambiguityRounds.length }} 轮</span>
          <span>得分：{{ agScore }}</span>
          <span>⏱ {{ agTimeLeft }}s</span>
        </div>
        <div class="ag-question-card">
          <p class="ag-question-text">"{{ ambiguityRounds[agRound].text }}"</p>
        </div>
        <div v-if="!agRoundResult" class="ag-buttons">
          <button class="btn-ambiguous" @click="answerAmbiguity(true)">模糊</button>
          <button class="btn-clear" @click="answerAmbiguity(false)">明确</button>
        </div>
        <div v-else class="ag-feedback" :class="agRoundResult.correct ? 'fb-correct' : 'fb-wrong'">
          <p><strong>{{ agRoundResult.correct ? '✅ 正确！' : '❌ 错误' }}</strong></p>
          <p style="margin-top:6px;">{{ agRoundResult.explanation }}</p>
          <button class="btn-primary btn-sm" style="margin-top:12px;" @click="nextAmbiguityRound">{{ agRound + 1 < ambiguityRounds.length ? '继续 →' : '查看结果' }}</button>
        </div>
      </div>

      <div v-else class="card" style="text-align:center;">
        <h3>🏁 挑战结束！</h3>
        <div class="score-big">{{ agScore }}<span class="score-unit">分</span></div>
        <p style="color:var(--text-secondary);margin-bottom:16px;">正确 {{ agHistory.filter(h => h.correct).length }} / {{ ambiguityRounds.length }} 轮</p>
        <button class="btn-primary" @click="resetAmbiguityGame">再来一次</button>
      </div>
    </div>

    <!-- TAB 4: 用例生成 -->
    <div v-if="activeTab === 3" class="tab-content">
      <div class="card">
        <h3 class="card-title">需求规格</h3>
        <div class="req-list">
          <div v-for="(req, i) in tcSpec.requirements" :key="i" class="req-item">
            <span class="req-tag">{{ req.id }}</span>
            <span>{{ req.text }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="card-title">✍️ 编写测试用例</h3>
        <p class="hint-text">为上述需求编写测试用例，每行一个。描述场景 + 预期结果。</p>
        <textarea v-model="tcAnswers" placeholder="验证有效信用卡可完成支付&#10;验证无效信用卡被拒绝并显示错误&#10;验证支付金额与订单总额一致&#10;..." rows="8" class="sql-input"></textarea>
        <div class="toolbar">
          <span class="hint-text">{{ tcAnswers.trim() ? tcAnswers.split('\n').filter(l => l.trim()).length : 0 }} 条用例</span>
          <button class="btn-primary" :disabled="!tcAnswers.trim()" @click="submitTestCases">📝 提交</button>
        </div>
      </div>

      <div v-if="tcResults" class="card result-card" :class="tcResults.coverage >= 60 ? 'result-pass' : 'result-fail'">
        <h3>用例覆盖度</h3>
        <div class="score-big">{{ tcResults.coverage }}<span class="score-unit">%</span></div>
        <div class="result-detail">
          <div class="rd-row"><span>覆盖的测试点</span><span>{{ tcResults.covered }} / {{ tcResults.total }}</span></div>
          <div class="rd-row"><span>💡 部分覆盖</span><span>{{ tcResults.partial }}</span></div>
          <div class="rd-row"><span>❌ 遗漏</span><span>{{ tcResults.missed.length }}</span></div>
        </div>
        <div v-if="tcResults.missed.length" style="margin-top:12px;">
          <p class="missed-title">遗漏的测试概念：</p>
          <div v-for="(m, i) in tcResults.missed" :key="i" class="missed-item">
            <span class="missed-cat">{{ m.reqId }}</span>
            <span>{{ m.concept }}</span>
          </div>
        </div>
        <button class="btn-ghost" style="margin-top:12px;" @click="tcResults = null">重试</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

// ── Tab state ──
const tabs = ['📄 需求审查', '🔍 边界枚举', '⚡ 歧义检测', '✍️ 用例生成']
const activeTab = ref(0)

function clearTabState() {
  editingClause.value = null
  reviewResults.value = null
  ecResults.value = null
  tcResults.value = null
  agRoundResult.value = null
}

// ═══════════════════════════════════════════
// TAB 1: 需求审查 (Spec Reader)
// ═══════════════════════════════════════════
const annotationCategories = ['Ambiguity', 'Missing Constraint', 'Contradiction', 'Missing Edge Case', 'Undefined Behavior']
function catIcon(c) {
  const m = { 'Ambiguity': '❓', 'Missing Constraint': '📏', 'Contradiction': '⚡', 'Missing Edge Case': '🔲', 'Undefined Behavior': '❔' }
  return m[c] || '📌'
}
function catSlug(c) { return c.toLowerCase().replace(/\s+/g, '-') }

const specs = [
  {
    id: 'login', title: '用户登录功能', icon: '🔐',
    description: '某电商平台登录模块 PRD 摘录 — 含3处歧义/缺失',
    clauses: [
      '用户可通过手机号+密码登录系统。',
      '系统应验证手机号格式是否符合规范。',
      '密码验证通过后，用户进入主页。',
      '系统支持快速登录功能，减少用户操作步骤。',
      '登录成功后保持会话状态，用户可继续操作。',
      '连续5次登录失败后，锁定账户30分钟。',
      '用户可在登录页面点击"忘记密码"自行重置密码。',
      '系统应记录每次登录的IP地址和时间戳。',
      '新用户首次登录后强制修改初始密码。',
      '登录页面响应时间应尽可能快。',
    ],
    answerKey: {
      2: 'Ambiguity',
      3: 'Ambiguity',
      4: 'Missing Constraint',
      9: 'Ambiguity',
    },
  },
  {
    id: 'payment', title: '支付接口', icon: '💳',
    description: '支付网关 API 规格说明摘录 — 含2处矛盾 + 1处缺失边界',
    clauses: [
      'POST /api/pay 接受订单ID和支付金额，完成扣款。',
      '支付操作必须是原子性的——要么完全成功，要么完全失败。',
      '系统支持部分退款功能，用户可对已支付订单发起部分金额退款。',
      '支付超时时间为30秒，超时后自动取消交易。',
      '同一订单不允许重复支付。',
      '支付成功后，系统向用户发送短信和邮件通知。',
      '支付金额必须与订单总额一致，不允许差额支付。',
      '退款金额不能超过原支付金额。',
      '系统应记录每笔交易的完整审计日志。',
    ],
    answerKey: {
      1: 'Contradiction',
      2: 'Contradiction',
      4: 'Missing Edge Case',
    },
  },
  {
    id: 'search', title: '搜索功能', icon: '🔍',
    description: '全局搜索功能 PRD 摘录 — 含2处模糊 + 1处缺失约束',
    clauses: [
      '用户在搜索框输入关键词后，系统返回相关结果。',
      '搜索结果按相关度从高到低排序。',
      '系统应在合理时间内返回搜索结果。',
      '支持按类别筛选搜索结果。',
      '搜索关键词长度限制为1-200个字符。',
      '系统记录热门搜索词用于优化排序算法。',
      '搜索结果分页显示，每页默认20条。',
      '空搜索或纯空格搜索返回提示信息。',
    ],
    answerKey: {
      0: 'Ambiguity',
      2: 'Ambiguity',
      4: 'Missing Constraint',
    },
  },
  {
    id: 'notification', title: '消息通知', icon: '🔔',
    description: '消息通知系统 PRD 摘录 — 含时区歧义 + 重试策略缺失 + 限流未定义',
    clauses: [
      '系统在触发事件后向用户推送通知消息。',
      '通知方式包括站内信、Push推送和邮件三种渠道。',
      '系统每天上午9点发送日报摘要给所有用户。',
      '消息发送失败时系统进行重试。',
      '用户可在设置页面关闭任意通知渠道。',
      '通知内容包含事件标题、简要描述和发生时间。',
      '系统应确保重要通知的送达率。',
      '单个用户每小时最多接收50条通知。',
      '营销类通知默认关闭，用户需主动订阅。',
    ],
    answerKey: {
      2: 'Ambiguity',
      3: 'Missing Constraint',
      6: 'Ambiguity',
      7: 'Undefined Behavior',
    },
  },
]

const specIndex = ref(0)
const editingClause = ref(null)
const tempCategory = ref('')
const tempNote = ref('')
const annotations = ref({})
const reviewResults = ref(null)

function getAnnotation(si, ci) {
  return (annotations.value[si] || {})[ci] || null
}

const annotationCount = computed(() => {
  const specAnno = annotations.value[specIndex.value] || {}
  return Object.keys(specAnno).length
})

function clauseClasses(si, ci) {
  const anno = getAnnotation(si, ci)
  const classes = []
  if (anno) {
    classes.push('annotated')
    classes.push('cat-' + catSlug(anno.category))
  }
  if (editingClause.value && editingClause.value.si === si && editingClause.value.ci === ci) {
    classes.push('is-editing')
  }
  if (reviewResults.value) {
    const r = reviewResults.value
    if (r.missedSet.has(ci) && !anno) classes.push('missed')
    if (r.fpSet.has(ci) && anno) classes.push('false-positive')
    if (r.wrongCatSet.has(ci)) classes.push('wrong-cat')
  }
  return classes
}

function startAnnotate(si, ci) {
  if (reviewResults.value) return
  editingClause.value = { si, ci }
  const existing = getAnnotation(si, ci)
  tempCategory.value = existing?.category || ''
  tempNote.value = existing?.note || ''
}

function confirmAnnotation() {
  if (!editingClause.value || !tempCategory.value) return
  const { si, ci } = editingClause.value
  if (!annotations.value[si]) annotations.value[si] = {}
  annotations.value[si][ci] = { category: tempCategory.value, note: tempNote.value }
  editingClause.value = null
}

function removeAnnotation(si, ci) {
  if (annotations.value[si]) {
    delete annotations.value[si][ci]
    if (Object.keys(annotations.value[si]).length === 0) delete annotations.value[si]
  }
  editingClause.value = null
}

function submitReview() {
  const spec = specs[specIndex.value]
  const specAnno = annotations.value[specIndex.value] || {}
  const answerKey = spec.answerKey

  let correctHits = 0
  let wrongCat = 0
  const fpSet = new Set()
  const missedSet = new Set()
  const wrongCatSet = new Set()
  const missedList = []

  // Check annotated clauses
  for (const ciStr of Object.keys(specAnno)) {
    const ci = parseInt(ciStr)
    if (answerKey[ci] !== undefined) {
      if (specAnno[ci].category === answerKey[ci]) {
        correctHits++
      } else {
        wrongCat++
        wrongCatSet.add(ci)
      }
    } else {
      fpSet.add(ci)
    }
  }

  // Check missed
  for (const ciStr of Object.keys(answerKey)) {
    const ci = parseInt(ciStr)
    if (!specAnno[ci]) {
      missedSet.add(ci)
      missedList.push({ ci, category: answerKey[ci], text: spec.clauses[ci] })
    }
  }

  const total = Object.keys(answerKey).length
  const score = total > 0 ? Math.round((correctHits / total) * 100) : 0

  reviewResults.value = {
    score, total, correctHits, wrongCat, missed: missedSet.size,
    falsePositiveCount: fpSet.size, missedSet, fpSet, wrongCatSet, missedList,
  }
}

// ═══════════════════════════════════════════
// TAB 2: 边界枚举 (Edge Case Enumerator)
// ═══════════════════════════════════════════
const ecScenario = ref(0)
const ecAnswers = ref({})
const ecResults = ref(null)

const edgeCaseScenarios = [
  {
    title: '🏦 用户每天最多提现500元',
    requirement: '用户每天最多提现500元。超出限额的提现请求应被拒绝并提示用户。',
    categories: [
      { icon: '🌍', label: '时区边界', placeholder: '例如：UTC+14 与 UTC-12 的"同一天"如何定义？' },
      { icon: '💱', label: '货币与精度', placeholder: '例如：500.00 vs 500 vs 500.01 如何处理？' },
      { icon: '🔄', label: '并发提现', placeholder: '例如：同一时刻发起多笔提现请求？' },
      { icon: '⏳', label: '待处理交易', placeholder: '例如：处理中的提现是否计入当日额度？' },
      { icon: '📅', label: '"每天"定义', placeholder: '例如：自然日(00:00-23:59) 还是 滚动24小时？' },
      { icon: '🌐', label: '多币种账户', placeholder: '例如：账户有USD和CNY，500元指哪种货币？' },
      { icon: '🕛', label: '跨日边界', placeholder: '例如：23:59:59发起的提现，何时计入？' },
      { icon: '🛡️', label: '退款与撤销', placeholder: '例如：提现后撤销，额度是否立即恢复？' },
    ],
    answerKeywords: [
      ['时区', 'UTC', '国际日期变更线', 'timezone', '时差', '全球'],
      ['精度', '500.00', '500.01', '分', '小数', '四舍五入', 'precision', 'decimal'],
      ['并发', '同时', 'race', '锁', '原子', 'concurrent', '并行'],
      ['pending', '待处理', '处理中', '未完成', '进行中', 'in-flight'],
      ['自然日', '日历日', '24小时', '滚动', 'calendar', 'rolling', '零点', '0点'],
      ['货币', '币种', '汇率', 'CNY', 'USD', 'currency', '多币种', '换算'],
      ['午夜', '零点', '跨天', '23:59', '00:00', 'midnight', '边界'],
      ['退款', '撤销', '恢复', '回滚', 'refund', 'reverse', 'rollback', '退还'],
    ],
  },
  {
    title: '🧮 价格计算器必须精确到分',
    requirement: '电商平台价格计算器必须精确到分。商品价格、折扣、税费计算后最终金额精确到小数点后两位（分），不得出现精度误差。',
    categories: [
      { icon: '🔢', label: '舍入模式', placeholder: '例如：四舍五入、向上取整、向下取整、银行家舍入？' },
      { icon: '➖', label: '负数价格', placeholder: '例如：退款/退货导致负数价格如何处理？' },
      { icon: '∞', label: '数值溢出', placeholder: '例如：极大数量 × 极高单价 是否溢出？' },
      { icon: '💱', label: '多币种精度', placeholder: '例如：日元(无小数位) vs 美元(2位) 混合计算？' },
      { icon: '🏷️', label: '折扣叠加', placeholder: '例如：多折扣叠加时的计算顺序和中间精度？' },
      { icon: '📊', label: '税费计算', placeholder: '例如：含税/不含税价格互相转换时的精度？' },
      { icon: '🔗', label: '浮点数陷阱', placeholder: '例如：0.1 + 0.2 = 0.30000000000000004？' },
    ],
    answerKeywords: [
      ['舍入', '四舍五入', '向上取整', '向下取整', '银行家', 'round', 'ceil', 'floor', 'ROUND_HALF_UP', 'ROUND_HALF_EVEN'],
      ['负', '退款', '退货', 'negative', 'minus', 'refund', 'return', '逆向'],
      ['溢出', '极大', 'overflow', 'MAX', 'Integer.MAX', '超出范围', '很大', '天文数字'],
      ['币种', '日元', '无小数', '0位小数', '3位小数', '科威特', '不同精度', 'decimals'],
      ['叠加', '顺序', '先后', 'stack', 'order', '优先级', '累计', '叠加折扣'],
      ['含税', '不含税', '税率', '÷1.', '×1.', 'tax', 'VAT', 'inclusive', 'exclusive'],
      ['浮点', '0.1+0.2', 'IEEE', 'double', 'float', 'BigDecimal', 'decimal', '浮点数', '精度损失'],
    ],
  },
]

const filledEdgeCaseCount = computed(() => {
  const scene = edgeCaseScenarios[ecScenario.value]
  let count = 0
  for (let i = 0; i < scene.categories.length; i++) {
    if ((ecAnswers.value[i] || '').trim()) count++
  }
  return count
})

function submitEdgeCases() {
  const scene = edgeCaseScenarios[ecScenario.value]
  const details = []
  let hits = 0
  let partial = 0
  let missed = 0

  for (let i = 0; i < scene.categories.length; i++) {
    const answer = (ecAnswers.value[i] || '').trim().toLowerCase()
    const keywords = scene.answerKeywords[i]
    const expected = scene.categories[i].label + '相关边界条件'
    let status = 'missed'

    if (answer) {
      const matchCount = keywords.filter(kw => answer.includes(kw.toLowerCase())).length
      if (matchCount >= 2) { status = 'hit'; hits++ }
      else if (matchCount >= 1) { status = 'partial'; partial++ }
      else { missed++ }
    } else {
      missed++
    }

    details.push({
      category: scene.categories[i].label,
      expected: scene.answerKeywords[i].slice(0, 3).join(' / '),
      yourAnswer: answer || null,
      status,
    })
  }

  const total = scene.categories.length
  const score = Math.round((hits * 100 + partial * 50) / total)

  ecResults.value = { score, hits, partial, missed, total, details }
}

// ═══════════════════════════════════════════
// TAB 3: 歧义检测 (Ambiguity Detector Game)
// ═══════════════════════════════════════════
const agStarted = ref(false)
const agTimeLeft = ref(60)
const agRound = ref(0)
const agScore = ref(0)
const agHistory = ref([])
const agRoundResult = ref(null)
let agTimer = null

const ambiguityRounds = [
  { text: '系统应在2秒内响应用户请求。', ambiguous: false, explanation: '"2秒"是可量化的明确指标，可直接测试验证。' },
  { text: '系统应快速响应用户请求。', ambiguous: true, explanation: '"快速"没有量化标准。应指定具体时间，如"2秒内"。' },
  { text: '错误率应低于0.1%。', ambiguous: false, explanation: '"0.1%"是明确的可量化指标，定义了测量方法和阈值。' },
  { text: '系统应提供可靠的网络连接。', ambiguous: true, explanation: '"可靠"未定义。应指定可用性指标，如"99.9% uptime"。' },
  { text: '用户数据应以安全方式存储。', ambiguous: true, explanation: '"安全方式"过于模糊。应指定加密算法、密钥管理等具体措施。' },
  { text: '支持最多10000个并发用户。', ambiguous: false, explanation: '"10000个并发用户"是具体的、可测量的性能指标。' },
  { text: '界面应美观且用户友好。', ambiguous: true, explanation: '"美观""用户友好"是主观描述，无法客观测试。应用具体可用性标准替代。' },
  { text: '所有API请求必须包含Authorization头。', ambiguous: false, explanation: '明确指定了请求格式要求，可自动化验证。' },
  { text: '系统应有足够的错误处理能力。', ambiguous: true, explanation: '"足够"没有定义。应列举需要处理的错误类型和处理方式。' },
  { text: '订单确认邮件在支付成功后30秒内发送。', ambiguous: false, explanation: '"30秒内"是明确的SLA指标，可测试。' },
  { text: '系统在高峰期应保持合理性能。', ambiguous: true, explanation: '"高峰期""合理性能"均未定义。应指定具体负载和响应时间要求。' },
  { text: '密码长度至少8个字符，包含大小写字母和数字。', ambiguous: false, explanation: '明确的密码复杂度规则，可直接实现和验证。' },
  { text: '搜索功能应根据需要返回结果。', ambiguous: true, explanation: '"根据需要"毫无约束力。应定义排序规则、分页和相关性标准。' },
  { text: '文件上传大小限制为10MB。', ambiguous: false, explanation: '"10MB"是明确的大小限制，可精确验证。' },
  { text: '系统应定期备份用户数据。', ambiguous: true, explanation: '"定期"没有指定频率。应明确备份周期，如"每日凌晨3点"。' },
]

function startAmbiguityGame() {
  agStarted.value = true
  agTimeLeft.value = 60
  agRound.value = 0
  agScore.value = 0
  agHistory.value = []
  agRoundResult.value = null
  startTimer()
}

function startTimer() {
  stopTimer()
  agTimer = setInterval(() => {
    agTimeLeft.value--
    if (agTimeLeft.value <= 0) {
      stopTimer()
      if (!agRoundResult.value) {
        agHistory.value.push({ round: agRound.value, correct: false, timedOut: true })
        agRoundResult.value = {
          correct: false,
          explanation: '⏰ 时间到！' + (ambiguityRounds[agRound.value].ambiguous ? '此语句是模糊的。' : '此语句是明确的。') + ' ' + ambiguityRounds[agRound.value].explanation,
        }
      }
    }
  }, 1000)
}

function stopTimer() {
  if (agTimer) { clearInterval(agTimer); agTimer = null }
}

function answerAmbiguity(studentSaysAmbiguous) {
  if (agRoundResult.value) return
  stopTimer()
  const round = ambiguityRounds[agRound.value]
  const correct = studentSaysAmbiguous === round.ambiguous
  if (correct) agScore.value += 10
  agHistory.value.push({ round: agRound.value, correct })
  agRoundResult.value = { correct, explanation: round.explanation }
}

function nextAmbiguityRound() {
  agRoundResult.value = null
  agRound.value++
  if (agRound.value < ambiguityRounds.length) {
    startTimer()
  } else {
    stopTimer()
  }
}

function resetAmbiguityGame() {
  stopTimer()
  agStarted.value = false
  agRound.value = 0
  agTimeLeft.value = 60
  agScore.value = 0
  agHistory.value = []
  agRoundResult.value = null
}

onUnmounted(() => stopTimer())

// ═══════════════════════════════════════════
// TAB 4: 用例生成 (Spec-to-Test-Case Mapper)
// ═══════════════════════════════════════════
const tcAnswers = ref('')
const tcResults = ref(null)

const tcSpec = {
  requirements: [
    { id: 'REQ-01', text: '用户可使用信用卡完成支付。系统支持 Visa、MasterCard 和银联卡。' },
    { id: 'REQ-02', text: '支付金额必须与订单总额完全一致，不允许差额扣款。' },
    { id: 'REQ-03', text: '支付失败时，系统应显示明确的错误信息，且不扣除用户余额。' },
    { id: 'REQ-04', text: '支付成功后，系统在5秒内跳转到成功页面并发送确认短信。' },
  ],
  testConcepts: [
    { reqId: 'REQ-01', keywords: ['有效', '信用卡', 'visa', 'mastercard', '银联', '卡号', '过期', '无效', 'cvv', '安全码', '3d', '不支持', '类型'], concept: '有效/无效/过期/不支持卡类型的支付场景' },
    { reqId: 'REQ-01', keywords: ['卡号', '格式', '16位', '19位', '校验', 'luhn', '长度'], concept: '卡号格式校验（长度、Luhn算法）' },
    { reqId: 'REQ-02', keywords: ['金额', '一致', '匹配', '等于', '相等', '总额', 'order total', 'amount'], concept: '支付金额与订单总额精确匹配' },
    { reqId: 'REQ-02', keywords: ['差额', '部分', '少付', '多付', '0.01', '不一致', '不匹配', '不等于'], concept: '金额不匹配时的拒绝处理' },
    { reqId: 'REQ-02', keywords: ['四舍五入', '精度', '分', '小数', 'rounding', '浮点'], concept: '金额计算精度（分位舍入）验证' },
    { reqId: 'REQ-03', keywords: ['失败', '错误', '余额', '不扣', '未扣', '扣款', '未变', '不变', '未扣除'], concept: '支付失败验证余额未被扣除' },
    { reqId: 'REQ-03', keywords: ['错误', '提示', '信息', '消息', '显示', '明确', 'error'], concept: '支付失败后错误信息的内容和展示' },
    { reqId: 'REQ-03', keywords: ['超时', 'timeout', '网络', '断连', '异常'], concept: '网络超时/断连等异常场景的支付处理' },
    { reqId: 'REQ-04', keywords: ['跳转', '成功', '页面', '5秒', 'redirect', '成功页'], concept: '支付成功5秒内跳转到成功页面' },
    { reqId: 'REQ-04', keywords: ['短信', '确认', '通知', 'sms', '发送', '收到'], concept: '支付成功后确认短信的发送和接收' },
    { reqId: 'REQ-04', keywords: ['并发', '重复', '幂等', '两次', '刷新', 'back'], concept: '防止重复支付（幂等性）验证' },
  ],
}

function submitTestCases() {
  const lines = tcAnswers.value.split('\n').filter(l => l.trim())
  const answersLower = lines.map(l => l.toLowerCase())
  let covered = 0
  let partial = 0
  const missed = []

  for (const concept of tcSpec.testConcepts) {
    let matched = false
    let partialMatch = false
    for (const ans of answersLower) {
      const kwHits = concept.keywords.filter(kw => ans.includes(kw.toLowerCase())).length
      if (kwHits >= 2) { matched = true; break }
      if (kwHits >= 1) partialMatch = true
    }
    if (matched) covered++
    else if (partialMatch) partial++
    else missed.push(concept)
  }

  const total = tcSpec.testConcepts.length
  const coverage = Math.round((covered * 100 + partial * 50) / total)

  tcResults.value = { coverage, covered, partial, total, missed }
}
</script>

<style scoped>
.lab-page { max-width: 860px; margin: 0 auto; }

/* Tab bar */
.tab-bar { display: flex; gap: 2px; margin-bottom: var(--space-md); border-bottom: 2px solid var(--border); }
.tab-btn {
  padding: 10px 20px; border: none; background: transparent; cursor: pointer;
  font-size: .84rem; font-weight: 500; color: var(--text-secondary);
  border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: all var(--fast); font-family: var(--font-sans);
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
.spec-desc { font-size: .78rem; color: var(--text-muted); margin-top: 8px; }
.card-title { font-size: .9rem; font-weight: 650; margin-bottom: 12px; }
.card-title .hint-text { font-weight: 400; }

/* Spec document */
.spec-doc { border: 1px solid var(--border); border-radius: var(--radius); padding: 4px; background: var(--bg); }
.spec-clause {
  display: flex; align-items: flex-start; gap: 8px; padding: 10px 12px;
  cursor: pointer; border-radius: 6px; transition: all var(--fast);
  border-left: 3px solid transparent; position: relative;
}
.spec-clause:hover { background: var(--surface-hover); }
.spec-clause.is-editing { background: var(--primary-light); border-left-color: var(--primary); }
.spec-clause.annotated { border-left-width: 3px; border-left-style: solid; }
.spec-clause.cat-ambiguity { border-left-color: #f59e0b; background: #fffbeb; }
.spec-clause.cat-missing-constraint { border-left-color: #3b82f6; background: #eff6ff; }
.spec-clause.cat-contradiction { border-left-color: #ef4444; background: #fef2f2; }
.spec-clause.cat-missing-edge-case { border-left-color: #8b5cf6; background: #f5f3ff; }
.spec-clause.cat-undefined-behavior { border-left-color: #6b7280; background: #f9fafb; }
.spec-clause.missed { border-left-color: #ef4444; background: #fef2f2; }
.spec-clause.false-positive { border-left-color: #f59e0b; background: #fffbeb; }
.spec-clause.wrong-cat { border-left-color: #f97316; background: #fff7ed; }
.clause-num { font-size: .74rem; color: var(--text-muted); min-width: 24px; font-family: var(--font-mono); }
.clause-text { font-size: .84rem; line-height: 1.6; flex: 1; }
.anno-badge {
  font-size: .68rem; padding: 2px 8px; border-radius: 10px; font-weight: 600;
  white-space: nowrap; flex-shrink: 0;
}
.badge-ambiguity { background: #fef3c7; color: #92400e; }
.badge-missing-constraint { background: #dbeafe; color: #1e40af; }
.badge-contradiction { background: #fecaca; color: #991b1b; }
.badge-missing-edge-case { background: #ede9fe; color: #5b21b6; }
.badge-undefined-behavior { background: #e5e7eb; color: #374151; }

/* Annotation popup */
.anno-popup {
  margin-top: 12px; padding: 16px; border: 2px solid var(--primary);
  border-radius: var(--radius); background: var(--surface);
}
.anno-popup-title { font-size: .82rem; font-weight: 650; margin-bottom: 10px; }
.anno-cats { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.anno-cat-btn {
  padding: 6px 12px; border: 1px solid var(--border); border-radius: 20px;
  background: var(--surface); cursor: pointer; font-size: .76rem;
  transition: all var(--fast); font-family: var(--font-sans);
}
.anno-cat-btn:hover { border-color: var(--primary); }
.anno-cat-btn.selected { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }
.anno-note { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: .8rem; outline: none; font-family: var(--font-sans); margin-bottom: 10px; }
.anno-note:focus { border-color: var(--primary); }
.anno-actions { display: flex; gap: 8px; align-items: center; }
.btn-sm { font-size: .76rem; padding: 6px 14px; }
.btn-lg { font-size: .92rem; padding: 12px 32px; }

.toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; }
.hint-text { font-size: .74rem; color: var(--text-muted); }

/* Results */
.result-card { margin-top: var(--space-md); }
.result-pass { border-left: 4px solid var(--success); }
.result-fail { border-left: 4px solid var(--warning); }
.score-big { font-size: 2.8rem; font-weight: 800; text-align: center; margin: 8px 0; }
.score-unit { font-size: 1rem; color: var(--text-muted); font-weight: 400; }
.result-detail { margin: 8px 0; }
.rd-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: .82rem; border-bottom: 1px solid var(--border-light); }
.missed-title { font-size: .8rem; font-weight: 650; margin-bottom: 6px; color: var(--danger); }
.missed-list { margin-top: 4px; }
.missed-item { display: flex; gap: 8px; align-items: baseline; padding: 6px 10px; font-size: .8rem; background: var(--bg); border-radius: 4px; margin-bottom: 4px; }
.missed-cat {
  font-size: .68rem; padding: 2px 8px; border-radius: 10px; font-weight: 600;
  background: var(--danger-light); color: var(--danger); white-space: nowrap; flex-shrink: 0;
}

/* Edge case */
.requirement-box {
  display: flex; align-items: flex-start; gap: 10px; padding: 14px;
  background: var(--primary-light); border-radius: var(--radius); margin-top: 12px;
  font-size: .88rem; font-weight: 550; line-height: 1.6;
}
.req-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 1px; }
.ec-category { margin-bottom: 14px; }
.ec-cat-label { display: block; font-size: .82rem; font-weight: 600; margin-bottom: 4px; }
.ec-textarea {
  width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .82rem; line-height: 1.5; outline: none; resize: vertical;
  font-family: var(--font-sans); background: var(--surface);
}
.ec-textarea:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.ec-answer-item { display: flex; gap: 10px; padding: 10px; border-radius: 6px; margin-bottom: 6px; font-size: .8rem; }
.ec-answer-item.hit { background: #f0fdf4; }
.ec-answer-item.partial { background: #fffbeb; }
.ec-answer-item.missed { background: #fef2f2; }
.ec-answer-status { font-size: 1rem; flex-shrink: 0; }
.ec-answer-text { color: var(--text-secondary); margin-top: 2px; }
.ec-your-answer { color: var(--text-muted); font-style: italic; margin-top: 2px; font-size: .76rem; }

/* Ambiguity game */
.ag-timer-bar { height: 6px; background: var(--border-light); border-radius: 3px; margin-bottom: 12px; overflow: hidden; }
.ag-timer-fill { height: 100%; background: var(--primary); border-radius: 3px; transition: width 1s linear; }
.ag-timer-fill.timer-low { background: var(--danger); }
.ag-info { display: flex; justify-content: space-between; font-size: .8rem; color: var(--text-secondary); margin-bottom: 16px; }
.ag-question-card {
  padding: 28px 20px; background: var(--bg); border-radius: var(--radius);
  border: 1px solid var(--border); margin-bottom: 18px;
}
.ag-question-text { font-size: 1.05rem; font-weight: 600; line-height: 1.6; }
.ag-buttons { display: flex; gap: 12px; justify-content: center; }
.btn-ambiguous, .btn-clear {
  padding: 12px 28px; border-radius: var(--radius); font-size: .9rem; font-weight: 600;
  cursor: pointer; border: 2px solid; transition: all var(--fast); font-family: var(--font-sans);
}
.btn-ambiguous { background: #fef3c7; border-color: #f59e0b; color: #92400e; }
.btn-ambiguous:hover { background: #fde68a; }
.btn-clear { background: #d1fae5; border-color: #10b981; color: #065f46; }
.btn-clear:hover { background: #a7f3d0; }
.ag-feedback { padding: 16px; border-radius: var(--radius); margin-top: 16px; font-size: .84rem; line-height: 1.6; }
.ag-feedback.fb-correct { background: #f0fdf4; border: 1px solid #bbf7d0; }
.ag-feedback.fb-wrong { background: #fef2f2; border: 1px solid #fecaca; }

/* Test case mapper */
.req-list { display: flex; flex-direction: column; gap: 10px; }
.req-item { display: flex; gap: 10px; align-items: baseline; font-size: .84rem; line-height: 1.5; padding: 10px; background: var(--bg); border-radius: 6px; }
.req-tag {
  font-size: .7rem; padding: 3px 8px; border-radius: 4px; font-weight: 650;
  background: var(--primary-light); color: var(--primary); font-family: var(--font-mono);
  white-space: nowrap; flex-shrink: 0;
}
.sql-input {
  width: 100%; padding: 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .82rem; line-height: 1.7;
  background: #1a1a2e; color: #e5e7eb; outline: none; resize: vertical;
}
.sql-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
</style>
