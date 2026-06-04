<template>
  <div class="lab-page">
    <div class="tabs-bar">
      <button class="tab-btn" :class="{ active: tab === 'free' }" @click="tab = 'free'">🔍 自由检测</button>
      <button class="tab-btn" :class="{ active: tab === 'challenge' }" @click="tab = 'challenge'">🏆 场景挑战</button>
    </div>

    <div v-if="tab === 'free'" class="card" style="margin-bottom:var(--space-md);">
      <textarea v-model="freeHtml" placeholder="在此粘贴 HTML 代码..." rows="10" class="html-input"></textarea>
      <div class="toolbar">
        <span class="hint-text">粘贴任意 HTML 片段，点击运行检测 WCAG 违规项</span>
        <button class="btn-primary" :disabled="!freeHtml.trim()" @click="runCheck(freeHtml)">▶ 运行检测</button>
      </div>
    </div>

    <div v-if="tab === 'challenge'">
      <div v-for="(ch, ci) in challenges" :key="ci" class="card challenge-card" :class="{ expanded: expandedChallenge === ci }">
        <div class="challenge-header" @click="expandedChallenge = expandedChallenge === ci ? -1 : ci">
          <div class="challenge-title">
            <span class="ch-diff">{{ ch.diff }}</span>
            <span>{{ ch.title }}</span>
          </div>
          <span class="ch-toggle">{{ expandedChallenge === ci ? '▼' : '▶' }}</span>
        </div>
        <div v-if="expandedChallenge === ci" class="challenge-body">
          <p class="ch-desc">{{ ch.desc }}</p>
          <pre class="ch-html">{{ ch.html }}</pre>
          <div class="ch-actions">
            <button class="btn-primary" @click="runChallenge(ci)">▶ 检测此场景</button>
            <span v-if="chSolved[ci]" class="ch-solved">🎉 已完成</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="results && results.length > 0" class="card" style="margin-bottom:var(--space-md);">
      <div class="results-header">
        <h3>📋 检测结果</h3>
        <span class="results-summary">
          <span class="sev-count sev-a">🔴 {{ counts.A }} A级</span>
          <span class="sev-count sev-aa">🟡 {{ counts.AA }} AA级</span>
          <span class="sev-count sev-aaa">🔵 {{ counts.AAA }} AAA级</span>
        </span>
      </div>
      <div class="violation-list">
        <div v-for="(v, i) in results" :key="i" class="violation-item">
          <div class="violation-head">
            <span class="sev-badge" :class="'sev-' + v.severity.toLowerCase()">{{ sevIcon(v.severity) }} {{ v.severity }}</span>
            <span class="rule-id">{{ v.rule }}</span>
            <span class="rule-name">{{ v.name }}</span>
          </div>
          <p class="violation-desc" v-html="v.description"></p>
          <p class="violation-fix">💡 <strong>修复建议：</strong>{{ v.fix }}</p>
        </div>
      </div>
    </div>

    <div v-if="results && results.length === 0" class="card" style="text-align:center;padding:32px;color:var(--success);">
      ✅ 未检测到 WCAG 违规项！
    </div>

    <div v-if="errorMsg" class="card" style="background:var(--danger-light);color:var(--danger);">
      ❌ {{ errorMsg }}
    </div>

    <details class="hints-card">
      <summary>📖 WCAG 规则参考</summary>
      <div class="rules-ref">
        <div v-for="r in ruleRefs" :key="r.id" class="rule-ref-item">
          <span class="sev-badge" :class="'sev-' + r.level">{{ sevIcon(r.level) }} {{ r.level }}</span>
          <strong>{{ r.id }}</strong> — {{ r.name }}
          <p>{{ r.desc }}</p>
        </div>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

const tab = ref('free')
const freeHtml = ref('')
const results = ref(null)
const errorMsg = ref('')
const expandedChallenge = ref(-1)
const chSolved = reactive([false, false, false])

const challenges = [
  {
    diff: '⭐', title: '图片缺少 alt',
    desc: '以下 HTML 包含一张图片但缺少 alt 属性。运行检测看看有什么问题。',
    html: '<div class="product">\n  <img src="/images/banner.png">\n  <h3>新品上市</h3>\n  <p>立即购买，享受限时优惠</p>\n</div>',
    expectedRules: ['1.1.1'],
  },
  {
    diff: '⭐⭐', title: '表单无障碍问题',
    desc: '表单中有多个无障碍问题：缺少标签关联、缺少提交按钮的 role、标题层级跳跃。',
    html: '<html>\n<head><title>注册</title></head>\n<body>\n  <h1>用户注册</h1>\n  <h3>填写以下信息</h3>\n  <form>\n    <input id="email" type="email" placeholder="邮箱">\n    <input id="password" type="password" placeholder="密码">\n    <div onclick="submitForm()">提交注册</div>\n  </form>\n</body>\n</html>',
    expectedRules: ['1.3.1', '4.1.2', '1.3.1'],
  },
  {
    diff: '⭐⭐⭐', title: '综合无障碍问题',
    desc: '完整页面片段，包含多个 WCAG 违规：缺少 lang、低对比度、缺少标签、缺少标题。',
    html: '<html>\n<head></head>\n<body>\n  <h1>仪表板</h1>\n  <h3>统计概览</h3>\n  <p style="color:#ccc;">当日活跃用户: 1,234</p>\n  <p style="color:#ccc;">新增订单: 56</p>\n  <input id="search" type="text" placeholder="搜索...">\n  <img src="/logo.png">\n  <div onclick="alert(\'clicked\')">点我</div>\n</body>\n</html>',
    expectedRules: ['3.1.1', '1.4.3', '1.4.3', '1.3.1', '1.1.1', '2.4.2', '4.1.2'],
  },
]

const ruleRefs = [
  { id: '1.1.1', name: '非文本内容', level: 'A', desc: '所有非文本内容（如图片、图标）都需要有替代文本，使屏幕阅读器能够传达信息。' },
  { id: '1.3.1', name: '信息和关系', level: 'A', desc: '通过标记（label、heading层级）传达的信息结构必须可被程序化确定。表单控件必须有关联标签，标题层级不可跳跃。' },
  { id: '1.4.3', name: '对比度（最低）', level: 'AA', desc: '文本和文本图像的对比度至少为 4.5:1，大文本至少 3:1。#ccc 在白色背景上对比度约 1.6:1，不达标。' },
  { id: '2.4.2', name: '页面标题', level: 'A', desc: '每个网页都需要有描述主题的 &lt;title&gt; 标签，帮助用户快速定位和导航。' },
  { id: '3.1.1', name: '页面语言', level: 'A', desc: 'html 标签需要 lang 属性指定页面默认语言，帮助屏幕阅读器选择正确的语音引擎。' },
  { id: '4.1.2', name: '名称、角色、值', level: 'A', desc: '所有 UI 组件必须有可被辅助技术访问的名称和角色。如 div 做按钮需 role="button" 和 tabindex。' },
]

const counts = computed(() => {
  if (!results.value) return { A: 0, AA: 0, AAA: 0 }
  const c = { A: 0, AA: 0, AAA: 0 }
  results.value.forEach(v => { if (c[v.severity] !== undefined) c[v.severity]++ })
  return c
})

function sevIcon(severity) {
  return severity === 'A' ? '🔴' : severity === 'AA' ? '🟡' : '🔵'
}

function checkA11y(html) {
  const violations = []

  // 1. img missing alt
  const imgRegex = /<img\b(?![^>]*\balt\s*=)[^>]*>/gi
  let match
  while ((match = imgRegex.exec(html)) !== null) {
    violations.push({
      severity: 'A', rule: 'WCAG 1.1.1', name: '非文本内容',
      description: `<img> 标签缺少 alt 属性：<code>${escapeHtml(match[0])}</code>。屏幕阅读器无法描述图片内容。`,
      fix: '为 img 标签添加 alt 属性，如 alt="描述性文字"。纯装饰性图片使用 alt=""。',
    })
  }

  // 2. input with id but no matching label[for]
  const inputIds = []
  const idRegex = /\b(id\s*=\s*["']([^"']+)["'])/gi
  let idMatch
  while ((idMatch = idRegex.exec(html)) !== null) {
    inputIds.push(idMatch[2])
  }
  inputIds.forEach(id => {
    const labelForRegex = new RegExp(`<label\\b[^>]*\\bfor\\s*=\\s*["']${escapeRegex(id)}["']`, 'i')
    if (!labelForRegex.test(html)) {
      violations.push({
        severity: 'A', rule: 'WCAG 1.3.1', name: '信息和关系',
        description: `id="${id}" 的输入控件没有关联的 &lt;label for="${id}"&gt; 标签。辅助技术无法识别此输入框的用途。`,
        fix: `添加 &lt;label for="${id}"&gt;标签文字&lt;/label&gt; 或将 input 包裹在 label 内。`,
      })
    }
  })

  // 3. Heading hierarchy skip
  const headingRegex = /<h([1-6])\b[^>]*>/gi
  const headings = []
  let hMatch
  while ((hMatch = headingRegex.exec(html)) !== null) {
    headings.push({ level: parseInt(hMatch[1]), index: hMatch.index })
  }
  for (let i = 1; i < headings.length; i++) {
    if (headings[i].level - headings[i - 1].level > 1) {
      violations.push({
        severity: 'A', rule: 'WCAG 1.3.1', name: '信息和关系',
        description: `标题层级跳跃：h${headings[i - 1].level} 后直接跳到 h${headings[i].level}，缺少 h${headings[i - 1].level + 1}。破坏文档大纲结构。`,
        fix: `在 h${headings[i - 1].level} 和 h${headings[i].level} 之间插入 h${headings[i - 1].level + 1}，保持层级连续。`,
      })
    }
  }

  // 4. html tag missing lang
  if (/<html\b(?![^>]*\blang\s*=)[^>]*>/i.test(html)) {
    violations.push({
      severity: 'A', rule: 'WCAG 3.1.1', name: '页面语言',
      description: '&lt;html&gt; 标签缺少 lang 属性。屏幕阅读器无法确定页面语言，影响语音合成准确性。',
      fix: '为 html 标签添加 lang 属性，如 &lt;html lang="zh-CN"&gt; 或 &lt;html lang="en"&gt;。',
    })
  }

  // 5. Low contrast: style="color:#ccc" on white background
  const colorRegex = /style\s*=\s*["'][^"']*color\s*:\s*(#ccc|#cccccc|#C0C0C0|#ddd|#eeeeee|#f0f0f0|rgb\(\s*20[4-9]\b|rgb\(\s*2[1-5]\d\b)[^"']*["']/gi
  let colorMatch
  const lowContrastHtml = []
  while ((colorMatch = colorRegex.exec(html)) !== null) {
    const contextStart = Math.max(0, colorMatch.index - 30)
    const contextEnd = Math.min(html.length, colorMatch.index + colorMatch[0].length + 30)
    const snippet = html.substring(contextStart, contextEnd).replace(/\n/g, ' ')
    lowContrastHtml.push(snippet)
  }
  lowContrastHtml.forEach(snippet => {
    violations.push({
      severity: 'AA', rule: 'WCAG 1.4.3', name: '对比度（最低）',
      description: `检测到浅色文本 (color 近 #ccc) 在白色背景上：<code>${escapeHtml(snippet)}</code>。对比度约 1.6:1，远低于 4.5:1 的最低要求。`,
      fix: '将文本颜色加深至 #595959 或更深（如 #4a4a4a），保证与白色背景对比度 >= 4.5:1。',
    })
  })

  // 6. div with onclick but no role
  const onclickRegex = /<div\b(?![^>]*\brole\s*=)[^>]*\bonclick\s*=[^>]*>/gi
  let onclickMatch
  while ((onclickMatch = onclickRegex.exec(html)) !== null) {
    violations.push({
      severity: 'A', rule: 'WCAG 4.1.2', name: '名称、角色、值',
      description: `<div> 元素使用了 onclick 事件但缺少 role 属性：<code>${escapeHtml(onclickMatch[0])}</code>。键盘用户和屏幕阅读器无法操作此元素。`,
      fix: '添加 role="button" 和 tabindex="0" 使其可被键盘聚焦。或直接使用 &lt;button&gt; 元素。',
    })
  }

  // 7. Missing title in head
  if (!/<head\b[^>]*>[\s\S]*?<\/head>/i.test(html) || !/<title\b[^>]*>[\s\S]*?<\/title>/i.test(html)) {
    violations.push({
      severity: 'A', rule: 'WCAG 2.4.2', name: '页面标题',
      description: '&lt;head&gt; 中缺少 &lt;title&gt; 标签。页面标题帮助用户识别当前页面内容，是屏幕阅读器最先读取的元素。',
      fix: '在 &lt;head&gt; 中添加 &lt;title&gt;页面标题&lt;/title&gt;，确保标题描述页面主题。',
    })
  }

  return violations
}

function runCheck(html) {
  errorMsg.value = ''
  try {
    results.value = checkA11y(html)
  } catch (e) {
    errorMsg.value = 'HTML 解析出错：' + e.message
    results.value = null
  }
}

function runChallenge(ci) {
  tab.value = 'free'
  freeHtml.value = challenges[ci].html
  runCheck(challenges[ci].html)
  chSolved[ci] = true
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
</script>

<style scoped>
.lab-page { max-width: 860px; margin: 0 auto; }

.tabs-bar { display: flex; gap: 4px; margin-bottom: var(--space-lg); background: var(--surface); border-radius: var(--radius); padding: 4px; border: 1px solid var(--border); }
.tab-btn { flex: 1; padding: 10px 8px; border: none; background: none; border-radius: 8px; cursor: pointer; font-size: .82rem; color: var(--text-secondary); font-weight: 500; transition: all var(--fast); font-family: var(--font-sans); }
.tab-btn.active { background: var(--primary); color: #fff; font-weight: 600; }

.html-input {
  width: 100%; padding: 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .8rem; line-height: 1.7;
  background: #1a1a2e; color: #e5e7eb; outline: none; resize: vertical;
}
.html-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.hint-text { font-size: .74rem; color: var(--text-muted); }

.challenge-card { margin-bottom: 10px; cursor: pointer; }
.challenge-card.expanded { border-color: var(--primary); }
.challenge-header { display: flex; justify-content: space-between; align-items: center; }
.challenge-title { display: flex; align-items: center; gap: 10px; font-size: .88rem; font-weight: 600; }
.ch-diff { font-size: .78rem; }
.ch-toggle { font-size: .7rem; color: var(--text-muted); }
.challenge-body { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border-light); }
.ch-desc { font-size: .82rem; color: var(--text-secondary); margin-bottom: 10px; line-height: 1.6; }
.ch-html {
  padding: 12px; background: #1a1a2e; border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .74rem; line-height: 1.6;
  color: #e5e7eb; overflow-x: auto; white-space: pre-wrap; margin-bottom: 10px;
}
.ch-actions { display: flex; align-items: center; gap: 12px; }
.ch-solved { font-size: .82rem; color: var(--success); font-weight: 600; }

.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.results-header h3 { font-size: 1rem; }
.results-summary { display: flex; gap: 10px; font-size: .78rem; }
.sev-count { padding: 2px 10px; border-radius: var(--radius-full); font-weight: 600; }
.sev-count.sev-a { background: #fef2f2; color: #dc2626; }
.sev-count.sev-aa { background: #fffbeb; color: #d97706; }
.sev-count.sev-aaa { background: #eff6ff; color: #2563eb; }

.violation-list { display: flex; flex-direction: column; gap: 10px; }
.violation-item { padding: 14px; background: var(--bg-subtle); border-radius: var(--radius-sm); border-left: 4px solid var(--border); }
.violation-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.sev-badge { padding: 2px 8px; border-radius: 4px; font-size: .7rem; font-weight: 700; font-family: var(--font-mono); }
.sev-badge.sev-a { background: #fef2f2; color: #dc2626; }
.sev-badge.sev-aa { background: #fffbeb; color: #d97706; }
.sev-badge.sev-aaa { background: #eff6ff; color: #2563eb; }
.rule-id { font-family: var(--font-mono); font-size: .72rem; color: var(--text-muted); font-weight: 600; }
.rule-name { font-size: .84rem; font-weight: 600; }
.violation-desc { font-size: .8rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px; }
.violation-desc :deep(code) { background: var(--border-light); padding: 1px 5px; border-radius: 3px; font-size: .74rem; color: var(--danger); }
.violation-fix { font-size: .78rem; color: var(--success); line-height: 1.5; }

.hints-card { margin-top: var(--space-md); font-size: .82rem; cursor: pointer; }
.hints-card summary { color: var(--primary); font-weight: 500; margin-bottom: 8px; }
.rules-ref { display: flex; flex-direction: column; gap: 12px; margin-top: 10px; padding-left: 8px; }
.rule-ref-item { font-size: .8rem; line-height: 1.6; }
.rule-ref-item p { font-size: .76rem; color: var(--text-secondary); margin-top: 2px; }
.rule-ref-item .sev-badge { display: inline-flex; margin-right: 6px; }
</style>
