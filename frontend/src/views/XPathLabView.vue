<template>
  <div class="lab-page">
    <div class="card" style="margin-bottom:var(--space-md);">
      <div class="mode-bar">
        <button :class="{ active: mode==='css' }" @click="mode='css'">CSS 选择器</button>
        <button :class="{ active: mode==='xpath' }" @click="mode='xpath'">XPath</button>
        <select v-model="currentScenario" class="scenario-pick">
          <option v-for="(s,i) in scenarios" :key="i" :value="i">{{ s.name }}</option>
        </select>
      </div>

      <div class="task-desc"><strong>目标：</strong>{{ scenarios[currentScenario].task }}</div>

      <div class="selector-bar">
        <span class="sel-prefix">{{ mode === 'css' ? '' : '//' }}</span>
        <input v-model="selector" :placeholder="selPlaceholder" class="sel-input" spellcheck="false" @input="evaluate">
        <span class="match-count" :class="{ hit: matchCount > 0 }">{{ matchCount }} 个匹配</span>
      </div>

      <div class="html-preview">
        <div class="html-header">
          <span class="html-dot red"></span><span class="html-dot yellow"></span><span class="html-dot green"></span>
          <span class="html-title">page.html</span>
        </div>
        <pre class="html-code" v-html="highlightedHtml"></pre>
      </div>

      <div v-if="matchCount > 0" class="card match-info" style="margin-top:12px;">
        <h4>匹配的元素</h4>
        <div v-for="(m, i) in matches" :key="i" class="match-row">
          <span class="match-tag">&lt;{{ m.tag }}&gt;</span>
          <span class="match-text">{{ m.text?.trim().slice(0, 60) || '(空元素)' }}</span>
          <span v-if="m.attrs" class="match-attrs">{{ m.attrs }}</span>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>📖 速查表</h3>
      <div class="cheat-grid">
        <div v-for="c in cheatsheet" :key="c.css" class="cheat-row">
          <code class="cheat-css">{{ c.css }}</code>
          <code class="cheat-xpath">{{ c.xpath }}</code>
          <span>{{ c.desc }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const mode = ref('css')
const selector = ref('')
const matchCount = ref(0)
const matches = ref([])
const highlightedHtml = ref('')

const scenarios = [
  {
    name: '📋 登录表单',
    task: '定位「登录」按钮',
    html: `<form class="login-form" id="login">
  <div class="field">
    <label for="email">邮箱</label>
    <input type="email" id="email" name="email" placeholder="you@example.com">
  </div>
  <div class="field">
    <label for="password">密码</label>
    <input type="password" id="password" name="password">
  </div>
  <button type="submit" class="btn primary" id="login-btn">登录</button>
  <a href="/forgot" class="link">忘记密码？</a>
</form>`
  },
  {
    name: '📊 数据表格',
    task: '定位表格中所有状态为「已完成」的行',
    html: `<table id="data-table" class="table striped">
  <thead><tr><th>ID</th><th>名称</th><th>状态</th><th>操作</th></tr></thead>
  <tbody>
    <tr class="row"><td>1</td><td>需求分析</td><td><span class="badge done">已完成</span></td><td><button>编辑</button></td></tr>
    <tr class="row"><td>2</td><td>用例设计</td><td><span class="badge done">已完成</span></td><td><button>编辑</button></td></tr>
    <tr class="row"><td>3</td><td>测试执行</td><td><span class="badge pending">进行中</span></td><td><button>编辑</button></td></tr>
    <tr class="row"><td>4</td><td>缺陷验证</td><td><span class="badge done">已完成</span></td><td><button>编辑</button></td></tr>
  </tbody>
</table>`
  },
  {
    name: '🧭 导航菜单',
    task: '定位当前激活的导航项',
    html: `<nav class="sidebar">
  <ul class="menu">
    <li class="menu-item"><a href="/dashboard">仪表板</a></li>
    <li class="menu-item active"><a href="/test-cases">测试用例</a></li>
    <li class="menu-item"><a href="/bugs">缺陷管理</a></li>
    <li class="menu-item has-submenu">
      <a href="/reports">报告</a>
      <ul class="submenu">
        <li><a href="/reports/weekly">周报</a></li>
        <li><a href="/reports/coverage">覆盖率</a></li>
      </ul>
    </li>
  </ul>
</nav>`
  },
  {
    name: '🔔 通知列表',
    task: '定位所有未读通知',
    html: `<div class="notifications">
  <div class="notification unread" data-id="101">
    <span class="dot"></span>
    <strong>新缺陷 #456</strong>
    <p>登录页崩溃 - P0</p>
    <time>10分钟前</time>
  </div>
  <div class="notification unread" data-id="102">
    <span class="dot"></span>
    <strong>构建完成</strong>
    <p>#234 通过了所有测试</p>
    <time>30分钟前</time>
  </div>
  <div class="notification read" data-id="99">
    <strong>用例评审</strong>
    <p>周五 14:00 会议室 A</p>
    <time>2小时前</time>
  </div>
</div>`
  },
]

const currentScenario = ref(0)
const currentHtml = computed(() => scenarios[currentScenario.value].html)
const selPlaceholder = computed(() => mode.value === 'css' ? 'button.primary' : 'button[@class="primary"]')

function escapeHtml(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

function evaluate() {
  highlightedHtml.value = escapeHtml(currentHtml.value)
  if (!selector.value.trim()) { matchCount.value = 0; matches.value = []; return }
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString('<div>' + currentHtml.value + '</div>', 'text/html')
    const root = doc.body.firstChild
    let elems = []
    if (mode.value === 'css') {
      elems = [...root.querySelectorAll(selector.value)]
    } else {
      const result = doc.evaluate('.//' + selector.value, root, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
      for (let i = 0; i < result.snapshotLength; i++) elems.push(result.snapshotItem(i))
    }
    matchCount.value = elems.length
    matches.value = elems.map(el => ({
      tag: el.tagName?.toLowerCase() || '#text',
      text: el.textContent || '',
      attrs: el.attributes ? [...el.attributes].map(a => `${a.name}="${a.value}"`).join(' ') : '',
    }))
  } catch (e) {
    matchCount.value = 0; matches.value = []
  }
}

watch(currentScenario, () => { selector.value = ''; evaluate() })

const cheatsheet = [
  { css: '.class', xpath: '//*[@class="class"]', desc: '按 class 匹配' },
  { css: '#id', xpath: '//*[@id="id"]', desc: '按 id 匹配' },
  { css: 'div', xpath: '//div', desc: '按标签名匹配' },
  { css: 'div > p', xpath: '//div/p', desc: '直接子元素' },
  { css: 'div p', xpath: '//div//p', desc: '任意后代' },
  { css: '[data-id]', xpath: '//*[@data-id]', desc: '按属性存在' },
  { css: '[data-id="101"]', xpath: '//*[@data-id="101"]', desc: '按属性值' },
  { css: 'button.primary', xpath: '//button[@class="primary"]', desc: '标签 + class' },
  { css: ':first-child', xpath: '//*[1]', desc: '第一个子元素' },
  { css: ':nth-child(2)', xpath: '//*[2]', desc: '第 N 个子元素' },
  { css: ':contains("文本")', xpath: '//*[contains(text(),"文本")]', desc: '按文本内容（仅XPath）' },
  { css: 'li.active', xpath: '//li[contains(@class,"active")]', desc: '包含 class' },
]
</script>

<style scoped>
.lab-page { max-width: 860px; margin: 0 auto; }

.mode-bar { display: flex; gap: 8px; margin-bottom: 12px; align-items: center; flex-wrap: wrap; }
.mode-bar button { padding: 6px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); cursor: pointer; font-size: .8rem; font-weight: 500; transition: all var(--fast); font-family: var(--font-sans); }
.mode-bar button.active { border-color: var(--primary); background: var(--primary); color: #fff; font-weight: 600; }
.scenario-pick { padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: .8rem; background: var(--surface); color: var(--text); cursor: pointer; outline: none; font-family: var(--font-sans); margin-left: auto; }

.task-desc { font-size: .82rem; color: var(--text-secondary); margin-bottom: 12px; }

.selector-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 0 14px; }
.selector-bar:focus-within { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.sel-prefix { font-family: var(--font-mono); color: var(--primary); font-weight: 700; font-size: .9rem; }
.sel-input { flex: 1; border: none; outline: none; padding: 10px 0; font-family: var(--font-mono); font-size: .86rem; background: transparent; color: var(--text); }
.match-count { font-size: .78rem; color: var(--text-muted); font-weight: 600; white-space: nowrap; }
.match-count.hit { color: var(--success); }

.html-preview { background: #1a1a2e; border-radius: var(--radius); overflow: hidden; }
.html-header { display: flex; align-items: center; gap: 6px; padding: 8px 14px; background: #16162a; }
.html-dot { width: 10px; height: 10px; border-radius: 50%; }
.html-dot.red { background: #ff5f57; } .html-dot.yellow { background: #febc2e; } .html-dot.green { background: #28c840; }
.html-title { color: #a0a0b8; font-size: .7rem; font-family: var(--font-mono); }
.html-code { padding: 16px 20px; margin: 0; font-family: var(--font-mono); font-size: .8rem; line-height: 1.7; color: #e5e7eb; white-space: pre; overflow-x: auto; }
.html-code :deep(.match) { background: rgba(99,102,241,.3); border-radius: 2px; }

.match-info { background: var(--success-light); border-color: var(--success); }
.match-info h4 { font-size: .84rem; margin-bottom: 8px; }
.match-row { display: flex; gap: 10px; align-items: baseline; padding: 4px 0; font-size: .78rem; border-bottom: 1px solid rgba(16,185,129,.15); }
.match-tag { font-family: var(--font-mono); color: var(--success); font-weight: 600; }
.match-text { color: var(--text-secondary); }
.match-attrs { font-family: var(--font-mono); font-size: .7rem; color: var(--text-muted); margin-left: auto; }

.cheat-grid { display: flex; flex-direction: column; gap: 4px; }
.cheat-row { display: flex; gap: 12px; align-items: baseline; padding: 5px 0; font-size: .78rem; border-bottom: 1px solid var(--border-light); }
.cheat-css { background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-family: var(--font-mono); font-size: .74rem; min-width: 80px; }
.cheat-xpath { background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-family: var(--font-mono); font-size: .72rem; min-width: 140px; white-space: nowrap; }
.cheat-row span { color: var(--text-secondary); }
</style>
