<template>
  <div class="lab-page">
    <div class="lab-layout">
      <!-- LEFT: Viewport -->
      <div class="vp-panel">
        <div class="scenario-bar">
          <select v-model="currentScenario" class="scenario-select">
            <option value="login">🔐 登录表单</option>
            <option value="cart">🛒 购物车</option>
            <option value="table">数据表格</option>
            <option value="modal">💬 模态对话框</option>
          </select>
          <button class="btn-rec" :class="{ active: isRecording }" @click="toggleRecording">
            {{ isRecording ? '⏹ 停止' : '⏺ 录制' }}
          </button>
          <span class="scenario-url">{{ scenarioUrl }}</span>
        </div>
        <div class="browser-chrome">
          <div class="bc-header">
            <span class="bc-dot red"></span><span class="bc-dot yellow"></span><span class="bc-dot green"></span>
            <span class="bc-url">{{ scenarioUrl }}</span>
          </div>
          <div class="bc-viewport" ref="viewportRef" @click="onViewportClick">
            <!-- Login Form -->
            <div v-if="currentScenario==='login'" class="mock-page">
              <h2>用户登录</h2>
              <form @submit.prevent="handleLogin">
                <div class="form-group"><label for="login-user">用户名</label><input id="login-user" type="text" v-model="loginState.username" placeholder="请输入用户名"></div>
                <div class="form-group"><label for="login-pass">密码</label><input id="login-pass" type="password" v-model="loginState.password" placeholder="请输入密码"></div>
                <button type="submit" class="btn-login">登录</button>
                <div class="error-msg" :style="{ display: loginState.showError ? 'block' : 'none' }">❌ 用户名或密码错误</div>
                <div class="success-msg" :style="{ display: loginState.showSuccess ? 'block' : 'none' }">登录成功！欢迎回来</div>
              </form>
            </div>
            <!-- Shopping Cart -->
            <div v-if="currentScenario==='cart'" class="mock-page">
              <h2>🛒 购物车</h2>
              <div v-for="(p,i) in cartProducts" :key="p.id" class="product-item" :data-product-id="p.id">
                <span class="product-name">{{ p.name }}</span>
                <span class="product-price">{{ fmtPrice(p.price) }}</span>
                <input type="number" class="quantity-input" v-model.number="p.qty" min="0" :data-product-id="p.id">
                <button class="btn-remove" @click="removeCartItem(i)">移除</button>
              </div>
              <div class="cart-total">总计: {{ fmtPrice(cartTotal) }}</div>
              <button id="checkout" @click="handleCheckout">去结算</button>
            </div>
            <!-- Data Table -->
            <div v-if="currentScenario==='table'" class="mock-page">
              <h2>数据管理</h2>
              <input id="search" v-model="tableState.search" placeholder="搜索 ID 或名称..." type="text">
              <table class="data-table">
                <thead><tr><th>ID</th><th>名称</th><th>状态</th><th>操作</th></tr></thead>
                <tbody>
                  <tr v-for="row in paginatedTableRows" :key="row.id" :data-id="row.id">
                    <td>{{ row.id }}</td><td>{{ row.name }}</td>
                    <td><span :class="['status-badge', row.status==='active'?'active':'inactive']">{{ row.status==='active'?'活跃':'停用' }}</span></td>
                    <td><button class="btn-edit" @click="editTableRow(row.id)">编辑</button></td>
                  </tr>
                </tbody>
              </table>
              <div class="pagination">
                <button @click="tableState.page--" :disabled="tableState.page<=1">上一页</button>
                <span>第 {{ tableState.page }} / {{ tableTotalPages }} 页</span>
                <button @click="tableState.page++" :disabled="tableState.page >= tableTotalPages">下一页</button>
              </div>
            </div>
            <!-- Modal Dialog -->
            <div v-if="currentScenario==='modal'" class="mock-page">
              <h2>💬 操作确认</h2>
              <button id="open-modal" @click="modalState.open=true">打开模态框</button>
              <div class="modal-overlay" v-if="modalState.open" @click.self="modalState.open=false">
                <div class="modal-content">
                  <h3>确认操作</h3><p>你确定要执行此操作吗？此操作不可撤销。</p>
                  <button class="btn-confirm" @click="confirmModal">确认</button>
                  <button class="btn-cancel" @click="modalState.open=false">取消</button>
                </div>
              </div>
              <div class="toast" v-if="modalState.toast">{{ modalState.toast }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Editor + Controls -->
      <div class="ed-panel">
        <div class="mode-tabs">
          <button :class="{ active: syntaxMode==='playwright' }" @click="syntaxMode='playwright'">Playwright</button>
          <button :class="{ active: syntaxMode==='cypress' }" @click="syntaxMode='cypress'">Cypress</button>
          <button :class="{ active: syntaxMode==='selenium' }" @click="syntaxMode='selenium'">Selenium</button>
        </div>

        <div class="challenge-bar">
          <select v-model="currentChallenge" @change="loadChallenge" class="challenge-select">
            <option value="beginner">初级</option>
            <option value="intermediate">⭐⭐ 中级</option>
            <option value="advanced">⭐⭐⭐ 高级</option>
          </select>
          <button class="btn-sm" @click="showChallengeHint">💡 提示</button>
          <button class="btn-sm" @click="loadSolution">📝 答案</button>
          <span v-if="currentHintText" class="hint-text">{{ currentHintText }}</span>
        </div>

        <div class="code-editor">
          <div class="ce-header">
            <span class="ce-dot red"></span><span class="ce-dot yellow"></span><span class="ce-dot green"></span>
            <span class="ce-fname">test.{{ syntaxMode==='playwright'?'spec.ts':syntaxMode==='cypress'?'cy.js':'java' }}</span>
          </div>
          <div class="ce-body"><textarea v-model="script" class="ce-textarea" :placeholder="placeholderScript" spellcheck="false" @input="onScriptInput"></textarea></div>
        </div>

        <div class="exec-controls">
          <button class="btn-step" :disabled="currentStepIndex>=totalSteps" @click="stepExecute">⏭ 单步</button>
          <button class="btn-run" @click="runAll">▶ 全部运行</button>
          <button class="btn-reset" @click="resetExecution">↺ 重置</button>
          <span class="step-info">{{ currentStepIndex }}/{{ totalSteps }} 步</span>
        </div>

        <div class="selector-panel" v-if="currentSelectors.length">
          <h4>选择器验证</h4>
          <div v-for="s in currentSelectors" :key="s.selector" class="sel-row" :class="s.status">
            <span class="sel-icon">{{ s.icon }}</span>
            <code>{{ s.selector }}</code>
            <span class="sel-info">{{ s.message }}</span>
            <span v-if="s.hint" class="sel-hint">{{ s.hint }}</span>
          </div>
        </div>

        <div class="log-panel" ref="logRef">
          <h4>执行日志</h4>
          <div v-if="!stepResults.length" class="log-empty">点击"单步"或"全部运行"开始</div>
          <div v-for="(r,i) in stepResults" :key="i" class="log-row" :class="r.pass?'pass':'fail'">
            <span class="log-icon">{{ r.pass?'✓':'✗' }}</span><span>{{ r.message }}</span>
          </div>
        </div>

        <div class="assertion-panel" v-if="assertionResults.length">
          <h4>断言结果</h4>
          <div v-for="(a,i) in assertionResults" :key="i" class="assert-row" :class="a.pass?'pass':'fail'">
            <span>{{ a.pass?'✓':'✗' }}</span><code>{{ a.assertion }}</code>
            <span v-if="!a.pass" class="assert-detail"> — {{ a.detail }}</span>
          </div>
        </div>

        <button class="btn-cheatsheet" @click="showCheatsheet=!showCheatsheet">📖 速查表 {{ showCheatsheet?'▲':'▼' }}</button>
        <div v-if="showCheatsheet" class="cheatsheet-panel">
          <table class="cheat-table">
            <thead><tr><th>操作</th><th>Playwright</th><th>Cypress</th><th>Selenium</th></tr></thead>
            <tbody>
              <tr v-for="c in cheatsheet" :key="c.action">
                <td>{{ c.action }}</td><td><code>{{ c.playwright }}</code></td><td><code>{{ c.cypress }}</code></td><td><code>{{ c.selenium }}</code></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onBeforeUnmount } from 'vue'

const viewportRef = ref(null)
const logRef = ref(null)

/* ==================== Scenario State ==================== */
const currentScenario = ref('login')
const scenarioUrl = computed(() => {
  const m = { login: '/login', cart: '/cart', table: '/data-table', modal: '/modal' }
  return m[currentScenario.value] || '/login'
})

const loginState = reactive({ username: '', password: '', showError: false, showSuccess: false })
function handleLogin() {
  loginState.showError = false; loginState.showSuccess = false
  if (loginState.username === 'admin' && loginState.password === 'pass123') loginState.showSuccess = true
  else loginState.showError = true
}

const cartProducts = ref([
  { id: 'widget-a', name: 'Widget A', price: 19.99, qty: 0 },
  { id: 'widget-b', name: 'Widget B', price: 29.99, qty: 0 },
  { id: 'gadget-x', name: 'Gadget X', price: 9.99, qty: 0 },
  { id: 'tool-y', name: 'Tool Y', price: 49.99, qty: 0 },
])
const cartTotal = computed(() => cartProducts.value.reduce((s,p) => s + p.price * p.qty, 0))
function removeCartItem(i) { cartProducts.value[i].qty = 0 }
function handleCheckout() { if (cartTotal.value > 0) alert('结算成功！') }
function fmtPrice(n) { return '$' + n.toFixed(2) }

const tableRows = [
  { id: 1, name: '项目 Alpha', status: 'active' },{ id: 2, name: '测试 Beta', status: 'inactive' },
  { id: 3, name: '产品 Gamma', status: 'active' },{ id: 4, name: '服务 Delta', status: 'active' },
  { id: 5, name: '模块 Epsilon', status: 'inactive' },{ id: 6, name: '系统 Zeta', status: 'active' },
  { id: 7, name: '工具 Eta', status: 'inactive' },{ id: 8, name: '库 Theta', status: 'active' },
  { id: 9, name: '框架 Iota', status: 'active' },{ id: 10, name: '平台 Kappa', status: 'inactive' },
]
const tableState = reactive({ search: '', page: 1, pageSize: 10 })
const filteredTableRows = computed(() => {
  let rows = tableRows
  if (tableState.search) { const q = tableState.search.toLowerCase(); rows = rows.filter(r => r.name.toLowerCase().includes(q) || String(r.id).includes(q)) }
  return rows
})
const paginatedTableRows = computed(() => {
  const start = (tableState.page - 1) * tableState.pageSize
  return filteredTableRows.value.slice(start, start + tableState.pageSize)
})
const tableTotalPages = computed(() => Math.max(1, Math.ceil(filteredTableRows.value.length / tableState.pageSize)))
function editTableRow(id) { /* placeholder */ if (tableState.page > tableTotalPages.value) tableState.page = tableTotalPages.value }

let _modalToastTimer = null
const modalState = reactive({ open: false, toast: '' })
function confirmModal() {
  modalState.open = false
  modalState.toast = '操作已确认'
  clearTimeout(_modalToastTimer)
  _modalToastTimer = setTimeout(() => { modalState.toast = '' }, 3000)
}

function urlToScenario(url) {
  const u = url.replace(/^\/+/,'').replace(/\/+$/,'')
  if (u === 'login' || u === '/login') return 'login'
  if (u === 'cart' || u === '/cart') return 'cart'
  if (u === 'data-table' || u === '/data-table') return 'table'
  if (u === 'modal' || u === '/modal') return 'modal'
  return null
}

/* ==================== Script & Syntax ==================== */
const syntaxMode = ref('playwright')
const script = ref('')
const placeholderScript = computed(() => {
  if (syntaxMode.value === 'playwright') return "await page.goto('/login');\nawait page.fill('#username', 'admin');\nawait page.click('.btn-login');\nawait expect(page.locator('.success-msg')).toBeVisible();"
  if (syntaxMode.value === 'cypress') return "cy.visit('/login');\ncy.get('#username').type('admin');\ncy.get('.btn-login').click();\ncy.get('.success-msg').should('be.visible');"
  return "driver.get('/login');\ndriver.findElement(By.id('username')).sendKeys('admin');\ndriver.findElement(By.css('.btn-login')).click();\nassert driver.findElement(By.css('.success-msg')).isDisplayed();"
})

/* ==================== Recording ==================== */
const isRecording = ref(false)
function toggleRecording() { isRecording.value = !isRecording.value }
function onViewportClick(e) {
  if (!isRecording.value) return
  e.preventDefault(); e.stopPropagation()
  const el = e.target.closest('[id], [class], button, input, span, td, div')
  if (!el) return
  let sel = ''
  if (el.id) sel = '#' + el.id
  else if (el.className && typeof el.className === 'string') {
    const cls = el.className.split(' ').filter(c => c && c !== 'mock-page' && !c.startsWith('status-') && c !== 'active' && c !== 'inactive')
    if (cls.length) sel = '.' + cls[0]
  }
  if (!sel) sel = el.tagName.toLowerCase()
  let line = `await page.click('${sel}');`
  if (el.tagName === 'INPUT' && el.type === 'text') line = `await page.fill('${sel}', 'value');`
  script.value = script.value ? script.value + '\n' + line : line
  onScriptInput()
}

/* ==================== Challenge System ==================== */
const currentChallenge = ref('beginner')
const challengeHints = reactive({ beginner: 0, intermediate: 0, advanced: 0 })
const currentHintText = ref('')

const challengeScripts = {
  beginner: `// ⭐ 初级挑战：填写登录表单，验证成功消息
await page.goto('/login');
await page.fill('#username', 'admin');
await page.fill('#password', 'pass123');
await page.click('.btn-login');
await expect(page.locator('.success-msg')).toBeVisible();`,
  intermediate: `// ⭐⭐ 中级挑战：添加商品到购物车，验证总价
await page.goto('/cart');
// 添加 2 个 Widget A
await page.fill('.quantity-input[data-product-id="widget-a"]', '2');
// 添加 1 个 Widget B
await page.fill('.quantity-input[data-product-id="widget-b"]', '1');
// 验证总价是否正确
await expect(page.locator('.cart-total')).toHaveText('$69.97');`,
  advanced: `// ⭐⭐⭐ 高级挑战：模态框确认 + 数据表格搜索
await page.goto('/modal');
// 打开模态框并确认
await page.click('#open-modal');
await page.click('.btn-confirm');
// 验证 toast 出现且模态框关闭
await expect(page.locator('.toast')).toBeVisible();
await expect(page.locator('.modal-overlay')).toBeHidden();
// 导航到数据表格并搜索
await page.goto('/data-table');
await page.fill('#search', 'test');
await expect(page.locator('.data-table tbody tr')).toBeVisible();`,
}

const challengeHintList = {
  beginner: ['使用 #username 定位用户名输入框','使用 #password 定位密码输入框','点击 .btn-login 提交登录','使用 .success-msg 验证成功消息'],
  intermediate: ['使用 .quantity-input[data-product-id="widget-a"] 定位 Widget A 数量输入','使用 .cart-total 验证总价','每个 .product-item 对应一个商品','使用 .btn-remove 移除商品'],
  advanced: ['使用 #open-modal 打开模态框','确认按钮是 .btn-confirm','Toast 使用 .toast 选择器','使用 expect(...).toBeHidden() 验证模态框关闭','搜索框是 #search'],
}

function loadChallenge() {
  resetExecution()
  const level = currentChallenge.value
  script.value = challengeScripts[level] || ''
  challengeHints[level] = 0
  currentHintText.value = ''
  // Reset scenario based on challenge
  if (level === 'beginner') currentScenario.value = 'login'
  else if (level === 'intermediate') currentScenario.value = 'cart'
  else currentScenario.value = 'modal'
  resetVirtualState()
  nextTick(() => onScriptInput())
}

function showChallengeHint() {
  const level = currentChallenge.value
  const hints = challengeHintList[level] || []
  const idx = challengeHints[level]
  if (idx < hints.length) {
    currentHintText.value = hints[idx]
    challengeHints[level]++
  } else {
    currentHintText.value = '所有提示已显示'
  }
}

function loadSolution() {
  const level = currentChallenge.value
  const solutions = {
    beginner: `await page.goto('/login');
await page.fill('#username', 'admin');
await page.fill('#password', 'pass123');
await page.click('.btn-login');
await expect(page.locator('.success-msg')).toBeVisible();`,
    intermediate: `await page.goto('/cart');
await page.fill('.quantity-input[data-product-id="widget-a"]', '2');
await page.fill('.quantity-input[data-product-id="widget-b"]', '1');
await expect(page.locator('.cart-total')).toHaveText('$69.97');
await page.click('.product-item:first-child .btn-remove');
await expect(page.locator('.cart-total')).toHaveText('$29.99');`,
    advanced: `await page.goto('/modal');
await page.click('#open-modal');
await page.click('.btn-confirm');
await expect(page.locator('.toast')).toBeVisible();
await expect(page.locator('.modal-overlay')).toBeHidden();
await page.goto('/data-table');
await page.fill('#search', 'test');
await expect(page.locator('.data-table tbody tr')).toBeVisible();`,
  }
  script.value = solutions[level] || ''
  onScriptInput()
}

function resetVirtualState() {
  loginState.username = ''; loginState.password = ''; loginState.showError = false; loginState.showSuccess = false
  cartProducts.value.forEach(p => p.qty = 0)
  tableState.search = ''; tableState.page = 1
  modalState.open = false; modalState.toast = ''
}

/* ==================== Execution Engine ==================== */
const stepResults = ref([])
const assertionResults = ref([])
const currentStepIndex = ref(0)

const scriptLines = computed(() => {
  return script.value.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('//') && !l.startsWith('#'))
})

const totalSteps = computed(() => scriptLines.value.length)

function parseLine(line) {
  const t = line.trim()
  if (syntaxMode.value === 'playwright') return parsePlaywright(t)
  if (syntaxMode.value === 'cypress') return parseCypress(t)
  return parseSelenium(t)
}

function parsePlaywright(l) {
  let m
  m = l.match(/page\.goto\('([^']+)'\)/); if (m) return { action: 'goto', url: m[1] }
  m = l.match(/page\.fill\('([^']+)',\s*'([^']*)'\)/); if (m) return { action: 'fill', selector: m[1], value: m[2] }
  m = l.match(/page\.type\('([^']+)',\s*'([^']*)'\)/); if (m) return { action: 'type', selector: m[1], value: m[2] }
  m = l.match(/page\.click\('([^']+)'\)/); if (m) return { action: 'click', selector: m[1] }
  m = l.match(/expect\(page\.locator\('([^']+)'\)\)\.toBeVisible\(\)/); if (m) return { action: 'assertVisible', selector: m[1] }
  m = l.match(/expect\(page\.locator\('([^']+)'\)\)\.toHaveText\('([^']*)'\)/); if (m) return { action: 'assertText', selector: m[1], expected: m[2] }
  m = l.match(/expect\(page\.locator\('([^']+)'\)\)\.toBeHidden\(\)/); if (m) return { action: 'assertHidden', selector: m[1] }
  return null
}

function parseCypress(l) {
  let m
  m = l.match(/cy\.visit\('([^']+)'\)/); if (m) return { action: 'goto', url: m[1] }
  m = l.match(/cy\.get\('([^']+)'\)\.type\('([^']*)'\)/); if (m) return { action: 'type', selector: m[1], value: m[2] }
  m = l.match(/cy\.get\('([^']+)'\)\.click\(\)/); if (m) return { action: 'click', selector: m[1] }
  m = l.match(/cy\.get\('([^']+)'\)\.should\('be\.visible'\)/); if (m) return { action: 'assertVisible', selector: m[1] }
  m = l.match(/cy\.get\('([^']+)'\)\.should\('have\.text',\s*'([^']*)'\)/); if (m) return { action: 'assertText', selector: m[1], expected: m[2] }
  m = l.match(/cy\.get\('([^']+)'\)\.should\('not\.be\.visible'\)/); if (m) return { action: 'assertHidden', selector: m[1] }
  return null
}

function parseSelenium(l) {
  let m
  m = l.match(/driver\.get\('([^']+)'\)/); if (m) return { action: 'goto', url: m[1] }
  m = l.match(/driver\.findElement\(By\.(?:css|id)\('([^']+)'\)\)\.sendKeys\('([^']*)'\)/); if (m) return { action: 'type', selector: m[1], value: m[2] }
  m = l.match(/driver\.findElement\(By\.(?:css|id)\('([^']+)'\)\)\.click\(\)/); if (m) return { action: 'click', selector: m[1] }
  m = l.match(/assert\s+driver\.findElement\(By\.(?:css|id)\('([^']+)'\)\)\.isDisplayed\(\)/); if (m) return { action: 'assertVisible', selector: m[1] }
  m = l.match(/assert(?:Equals)?\s*\(?\s*driver\.findElement\(By\.(?:css|id)\('([^']+)'\)\)\.getText\(\),\s*'?([^')]+?)'?\s*\)?;?/); if (m) return { action: 'assertText', selector: m[1], expected: m[2].trim() }
  return null
}

async function stepExecute() {
  if (currentStepIndex.value >= totalSteps.value) return
  const line = scriptLines.value[currentStepIndex.value]
  const cmd = parseLine(line)
  if (!cmd) {
    stepResults.value.push({ pass: false, message: `无法解析: ${line.slice(0,60)}` })
    currentStepIndex.value++
    return
  }
  const result = await executeCommand(cmd)
  stepResults.value.push(result)
  if (cmd.action && cmd.action.startsWith('assert')) {
    assertionResults.value.push({
      pass: result.pass,
      assertion: line.replace(/^await\s+/,'').replace(/^assert\s+/,'').slice(0, 80),
      detail: result.pass ? 'PASSED' : result.message.replace(/^断言[^:]+:\s*/,''),
    })
  }
  currentStepIndex.value++
  await nextTick()
  if (logRef.value) logRef.value.scrollTop = logRef.value.scrollHeight
}

async function runAll() {
  resetExecution()
  resetVirtualState()
  for (let i = 0; i < totalSteps.value; i++) {
    await stepExecute()
  }
}

function resetExecution() {
  currentStepIndex.value = 0
  stepResults.value = []
  assertionResults.value = []
  currentSelectors.value = []
  resetVirtualState()
}

/* ==================== Command Execution ==================== */
async function executeCommand(cmd) {
  const vp = viewportRef.value
  if (!vp && cmd.action !== 'goto') return { pass: false, message: `Viewport 未就绪` }

  try {
    switch (cmd.action) {
      case 'goto': {
        const s = urlToScenario(cmd.url)
        if (s) {
          resetVirtualState()
          currentScenario.value = s
          await nextTick()
          return { pass: true, message: `✓ 导航到 ${scenarioUrl.value}` }
        }
        return { pass: false, message: `✗ 未知 URL: ${cmd.url}` }
      }
      case 'fill':
      case 'type': {
        const el = vp.querySelector(cmd.selector)
        if (!el) return { pass: false, message: `✗ 选择器 ${cmd.selector} 未找到` }
        if (el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA') return { pass: false, message: `✗ ${cmd.selector} 不是输入元素` }
        const setter = Object.getOwnPropertyDescriptor(el.tagName === 'INPUT' ? HTMLInputElement.prototype : HTMLTextAreaElement.prototype, 'value').set
        setter.call(el, cmd.value)
        el.dispatchEvent(new Event('input', { bubbles: true }))
        el.dispatchEvent(new Event('change', { bubbles: true }))
        await nextTick()
        highlight(el)
        return { pass: true, message: `✓ 填充 ${cmd.selector} 为 "${cmd.value}"` }
      }
      case 'click': {
        const el = vp.querySelector(cmd.selector)
        if (!el) return { pass: false, message: `✗ 选择器 ${cmd.selector} 未找到` }
        el.click()
        await nextTick()
        highlight(el)
        return { pass: true, message: `✓ 点击 ${cmd.selector}` }
      }
      case 'assertVisible': {
        const el = vp.querySelector(cmd.selector)
        if (!el) return { pass: false, message: `✗ 断言失败: ${cmd.selector} 未找到` }
        const style = window.getComputedStyle(el)
        const visible = el.offsetParent !== null && style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity) > 0
        if (visible) { highlight(el); return { pass: true, message: `✓ 断言通过: ${cmd.selector} 可见` } }
        return { pass: false, message: `✗ 断言失败: ${cmd.selector} 不可见` }
      }
      case 'assertHidden': {
        const el = vp.querySelector(cmd.selector)
        if (!el) return { pass: true, message: `✓ 断言通过: ${cmd.selector} 已隐藏（不在DOM中）` }
        const style = window.getComputedStyle(el)
        const hidden = el.offsetParent === null || style.display === 'none' || style.visibility === 'hidden'
        if (hidden) return { pass: true, message: `✓ 断言通过: ${cmd.selector} 已隐藏` }
        return { pass: false, message: `✗ 断言失败: ${cmd.selector} 仍然可见` }
      }
      case 'assertText': {
        const el = vp.querySelector(cmd.selector)
        if (!el) return { pass: false, message: `✗ 断言失败: ${cmd.selector} 未找到` }
        const text = el.textContent.replace(/\s+/g, ' ').trim()
        const expected = cmd.expected.trim()
        const match = text === expected || text.includes(expected)
        if (match) { highlight(el); return { pass: true, message: `✓ 断言通过: ${cmd.selector} 文本为 "${text}"` } }
        return { pass: false, message: `✗ 断言失败: 期望 "${expected}", 实际 "${text}"` }
      }
      default:
        return { pass: false, message: `✗ 未知命令: ${cmd.action}` }
    }
  } catch (e) {
    return { pass: false, message: `✗ 执行错误: ${e.message}` }
  }
}

function highlight(el) {
  if (!el) return
  el.classList.add('hl-pulse')
  setTimeout(() => el.classList.remove('hl-pulse'), 1200)
}

/* ==================== Selector Validation ==================== */
const currentSelectors = ref([])

function extractSelectorsFromLine(line) {
  const mode = syntaxMode.value
  const selList = []
  if (mode === 'playwright') {
    const m1 = line.match(/page\.(?:fill|click|type|locator)\('([^']+)'/)
    if (m1) selList.push(m1[1])
    const m2 = line.match(/expect\(page\.locator\('([^']+)'\)\)/)
    if (m2) selList.push(m2[1])
  } else if (mode === 'cypress') {
    const m = line.match(/cy\.get\('([^']+)'\)/)
    if (m) selList.push(m[1])
  } else if (mode === 'selenium') {
    const re = /By\.(?:css|id)\('([^']+)'\)/g; let m
    while ((m = re.exec(line)) !== null) selList.push(m[1])
  }
  return [...new Set(selList)]
}

function onScriptInput() {
  const vp = viewportRef.value
  if (!vp) { currentSelectors.value = []; return }

  // Validate selectors from ALL lines for the selector panel
  currentSelectors.value = []
  const allSelectors = new Map()
  for (const line of scriptLines.value) {
    const sels = extractSelectorsFromLine(line)
    for (const s of sels) {
      if (!allSelectors.has(s)) allSelectors.set(s, [])
    }
  }
  for (const [sel] of allSelectors) {
    try {
      const elems = vp.querySelectorAll(sel)
      const count = elems.length
      let status, icon, message, hint
      if (count === 1) { status = 'ok'; icon = '✓'; message = `匹配 1 个元素` }
      else if (count === 0) { status = 'err'; icon = '✗'; message = `匹配 0 个元素`; hint = '选择器可能不存在或拼写错误' }
      else { status = 'warn'; icon = '⚠'; message = `匹配 ${count} 个元素`; hint = '多个匹配，考虑使用更具体的定位'.replace(/ /g, ' ') }
      currentSelectors.value.push({ selector: sel, status, icon, message, hint })
    } catch {
      currentSelectors.value.push({ selector: sel, status: 'err', icon: '✗', message: '无效选择器', hint: '' })
    }
  }
}

watch(currentScenario, async () => { await nextTick(); onScriptInput() })
watch(syntaxMode, () => { onScriptInput() })

/* ==================== Cheatsheet ==================== */
const showCheatsheet = ref(false)
const cheatsheet = [
  { action:'导航', playwright:"page.goto(url)", cypress:"cy.visit(url)", selenium:"driver.get(url)" },
  { action:'点击', playwright:"page.click(sel)", cypress:"cy.get(sel).click()", selenium:"driver.findElement(By.css(sel)).click()" },
  { action:'输入', playwright:"page.fill(sel, text)", cypress:"cy.get(sel).type(text)", selenium:"driver.findElement(By.css(sel)).sendKeys(text)" },
  { action:'断言可见', playwright:"expect(page.locator(sel)).toBeVisible()", cypress:"cy.get(sel).should('be.visible')", selenium:"assert driver.findElement(By.css(sel)).isDisplayed()" },
  { action:'断言隐藏', playwright:"expect(page.locator(sel)).toBeHidden()", cypress:"cy.get(sel).should('not.be.visible')", selenium:"assert !driver.findElement(By.css(sel)).isDisplayed()" },
  { action:'断言文本', playwright:"expect(page.locator(sel)).toHaveText(t)", cypress:"cy.get(sel).should('have.text', t)", selenium:"assertEquals(driver.findElement(By.css(sel)).getText(), t)" },
  { action:'截图', playwright:"await page.screenshot({path:t})", cypress:"cy.screenshot(t)", selenium:"TakesScreenshot driver" },
]

/* Init */
loadChallenge()

onBeforeUnmount(() => {
  if (_modalToastTimer) clearTimeout(_modalToastTimer)
})
</script>

<style scoped>
.lab-page { max-width: 1200px; margin: 0 auto; }

.page-header { margin-bottom: var(--space-md); }
.page-header h1 { font-size: 1.5rem; font-weight: 750; letter-spacing: -.5px; margin-bottom: 4px; }
.page-header p { color: var(--text-secondary); font-size: .88rem; line-height: 1.6; }

.lab-layout { display: grid; grid-template-columns: 45fr 55fr; gap: var(--space-lg); }
@media (max-width: 900px) { .lab-layout { grid-template-columns: 1fr; } }

/* Viewport */
.vp-panel { display: flex; flex-direction: column; gap: 10px; }
.scenario-bar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.scenario-select { padding: 6px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: .8rem; background: var(--surface); color: var(--text); cursor: pointer; outline: none; font-family: var(--font-sans); }
.scenario-url { font-family: var(--font-mono); font-size: .73rem; color: var(--text-muted); margin-left: auto; }
.btn-rec { padding: 5px 12px; border: 1px solid var(--danger); border-radius: var(--radius-sm); background: transparent; color: var(--danger); cursor: pointer; font-size: .76rem; font-weight: 600; font-family: var(--font-sans); transition: all var(--fast); }
.btn-rec.active { background: var(--danger); color: #fff; animation: recPulse 1.2s infinite; }
@keyframes recPulse { 0%,100% { opacity: 1; } 50% { opacity: .5; } }

.browser-chrome { border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; background: var(--bg); }
.bc-header { display: flex; align-items: center; gap: 6px; padding: 8px 12px; background: var(--surface); border-bottom: 1px solid var(--border); }
.bc-dot { width: 10px; height: 10px; border-radius: 50%; }
.bc-dot.red { background: #ff5f57; } .bc-dot.yellow { background: #febc2e; } .bc-dot.green { background: #28c840; }
.bc-url { font-family: var(--font-mono); font-size: .68rem; color: var(--text-muted); flex: 1; text-align: center; }
.bc-viewport { padding: 24px 28px; min-height: 420px; background: var(--bg); }

/* Mock pages */
.mock-page h2 { font-size: 1.2rem; margin-bottom: 18px; font-weight: 650; }
.mock-page .form-group { margin-bottom: 12px; }
.mock-page .form-group label { display: block; font-size: .8rem; font-weight: 600; margin-bottom: 4px; color: var(--text-secondary); }
.mock-page .form-group input { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: .84rem; font-family: var(--font-sans); background: var(--surface); color: var(--text); outline: none; }
.mock-page .form-group input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.mock-page .btn-login, .mock-page #checkout, .mock-page #open-modal { padding: 9px 22px; border: none; border-radius: var(--radius-sm); background: var(--primary); color: #fff; font-weight: 600; font-size: .84rem; cursor: pointer; font-family: var(--font-sans); margin-top: 6px; transition: all var(--fast); }
.mock-page .btn-login:hover, .mock-page #checkout:hover, .mock-page #open-modal:hover { background: var(--primary-hover); }
.mock-page .error-msg { color: var(--danger); font-size: .8rem; margin-top: 10px; padding: 8px 12px; background: var(--danger-light); border-radius: var(--radius-sm); }
.mock-page .success-msg { color: var(--success); font-size: .8rem; margin-top: 10px; padding: 8px 12px; background: var(--success-light); border-radius: var(--radius-sm); }

.product-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-light); }
.product-name { flex: 1; font-weight: 600; font-size: .86rem; }
.product-price { font-family: var(--font-mono); font-size: .82rem; color: var(--text-secondary); min-width: 56px; }
.quantity-input { width: 60px; padding: 5px 8px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: .8rem; text-align: center; font-family: var(--font-mono); background: var(--surface); color: var(--text); }
.btn-remove { padding: 4px 12px; border: 1px solid var(--danger); border-radius: var(--radius-sm); background: transparent; color: var(--danger); cursor: pointer; font-size: .74rem; font-weight: 500; font-family: var(--font-sans); transition: all var(--fast); }
.btn-remove:hover { background: var(--danger); color: #fff; }
.cart-total { margin-top: 14px; font-weight: 700; font-size: 1rem; font-family: var(--font-mono); padding: 8px 0; border-top: 2px solid var(--border); }

#search { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: .82rem; margin-bottom: 14px; font-family: var(--font-sans); background: var(--surface); color: var(--text); outline: none; }
#search:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.data-table { width: 100%; border-collapse: collapse; font-size: .78rem; margin-bottom: 12px; }
.data-table th { text-align: left; padding: 8px 10px; border-bottom: 2px solid var(--border); font-weight: 650; color: var(--text-secondary); font-size: .74rem; text-transform: uppercase; }
.data-table td { padding: 8px 10px; border-bottom: 1px solid var(--border-light); }
.status-badge { padding: 2px 10px; border-radius: var(--radius-full); font-size: .7rem; font-weight: 600; }
.status-badge.active { background: var(--success-light); color: var(--success); }
.status-badge.inactive { background: var(--danger-light); color: var(--danger); }
.btn-edit { padding: 3px 10px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); color: var(--text-secondary); cursor: pointer; font-size: .7rem; font-family: var(--font-sans); }
.pagination { display: flex; align-items: center; gap: 10px; justify-content: center; font-size: .78rem; color: var(--text-secondary); }
.pagination button { padding: 4px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); color: var(--text); cursor: pointer; font-size: .74rem; font-family: var(--font-sans); }
.pagination button:disabled { opacity: .4; cursor: not-allowed; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); display: flex; align-items: center; justify-content: center; z-index: 50; }
.modal-content { background: var(--surface); padding: 28px; border-radius: var(--radius-lg); min-width: 300px; box-shadow: var(--shadow-lg); }
.modal-content h3 { margin-bottom: 12px; font-size: 1rem; }
.modal-content p { color: var(--text-secondary); font-size: .84rem; margin-bottom: 18px; }
.btn-confirm { padding: 7px 20px; border: none; border-radius: var(--radius-sm); background: var(--success); color: #fff; font-weight: 600; cursor: pointer; font-size: .8rem; font-family: var(--font-sans); margin-right: 8px; }
.btn-cancel { padding: 7px 20px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); color: var(--text-secondary); cursor: pointer; font-size: .8rem; font-family: var(--font-sans); }
.toast { position: fixed; bottom: 30px; right: 30px; padding: 12px 24px; background: var(--success); color: #fff; border-radius: var(--radius); font-size: .84rem; font-weight: 600; z-index: 60; box-shadow: var(--shadow); animation: toastIn .3s var(--ease); }
@keyframes toastIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

/* Highlight */
:deep(.hl-pulse) { animation: pulseBorder 1.2s ease-out; border-radius: 3px; position: relative; z-index: 5; }
@keyframes pulseBorder {
  0% { box-shadow: 0 0 0 0 rgba(99,102,241,.5); outline: 3px solid var(--primary); outline-offset: 2px; }
  40% { box-shadow: 0 0 0 6px rgba(245,158,11,.6); outline: 3px solid var(--warning); outline-offset: 2px; }
  100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); outline: 3px solid transparent; outline-offset: 2px; }
}

/* Editor Panel */
.ed-panel { display: flex; flex-direction: column; gap: 10px; }
.mode-tabs { display: flex; gap: 4px; background: var(--surface); border-radius: var(--radius); padding: 4px; border: 1px solid var(--border); }
.mode-tabs button { flex: 1; padding: 8px; border: none; background: none; border-radius: 8px; cursor: pointer; font-size: .78rem; color: var(--text-secondary); font-weight: 500; transition: all var(--fast); font-family: var(--font-sans); }
.mode-tabs button.active { background: var(--primary); color: #fff; font-weight: 600; box-shadow: var(--shadow-xs); }

.challenge-bar { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.challenge-select { padding: 5px 10px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: .78rem; background: var(--surface); color: var(--text); cursor: pointer; outline: none; font-family: var(--font-sans); }
.btn-sm { padding: 4px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); color: var(--text-secondary); cursor: pointer; font-size: .74rem; font-family: var(--font-sans); transition: all var(--fast); }
.btn-sm:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-light); }
.hint-text { font-size: .74rem; color: var(--primary); font-weight: 500; background: var(--primary-light); padding: 4px 10px; border-radius: var(--radius-sm); }

.code-editor { background: #1a1a2e; border-radius: var(--radius-lg); overflow: hidden; border: 1px solid #2d2d4a; }
.ce-header { display: flex; align-items: center; gap: 8px; padding: 8px 14px; background: #16162a; border-bottom: 1px solid #2d2d4a; }
.ce-dot { width: 10px; height: 10px; border-radius: 50%; }
.ce-dot.red { background: #ff5f57; } .ce-dot.yellow { background: #febc2e; } .ce-dot.green { background: #28c840; }
.ce-fname { color: #a0a0b8; font-size: .7rem; font-family: var(--font-mono); flex: 1; }
.ce-body { display: flex; }
.ce-textarea { width: 100%; min-height: 200px; padding: 14px 16px; border: none; font-family: var(--font-mono); font-size: .8rem; line-height: 1.7; background: transparent; color: #e5e7eb; resize: vertical; outline: none; tab-size: 2; }
.ce-textarea::placeholder { color: #6b7280; }

.exec-controls { display: flex; align-items: center; gap: 8px; }
.btn-step { padding: 7px 16px; border: 1px solid var(--primary); border-radius: var(--radius-sm); background: transparent; color: var(--primary); cursor: pointer; font-size: .78rem; font-weight: 600; font-family: var(--font-sans); transition: all var(--fast); }
.btn-step:hover:not(:disabled) { background: var(--primary); color: #fff; }
.btn-step:disabled { opacity: .4; cursor: not-allowed; }
.btn-run { padding: 7px 20px; border: none; border-radius: var(--radius-sm); background: var(--success); color: #fff; cursor: pointer; font-size: .78rem; font-weight: 600; font-family: var(--font-sans); transition: all var(--fast); }
.btn-run:hover { filter: brightness(1.1); }
.btn-reset { padding: 7px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); color: var(--text-secondary); cursor: pointer; font-size: .78rem; font-family: var(--font-sans); transition: all var(--fast); }
.btn-reset:hover { border-color: var(--text-muted); }
.step-info { font-family: var(--font-mono); font-size: .74rem; color: var(--text-muted); margin-left: auto; }

.selector-panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px 14px; }
.selector-panel h4 { font-size: .8rem; margin-bottom: 8px; color: var(--text-secondary); }
.sel-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: .76rem; border-bottom: 1px solid var(--border-light); }
.sel-row:last-child { border-bottom: none; }
.sel-row code { font-family: var(--font-mono); font-size: .74rem; padding: 2px 6px; border-radius: 3px; }
.sel-row.ok code { background: var(--success-light); color: var(--success); }
.sel-row.err code { background: var(--danger-light); color: var(--danger); }
.sel-row.warn code { background: var(--warning-light); color: var(--warning); }
.sel-icon { font-weight: 700; width: 16px; text-align: center; }
.sel-row.ok .sel-icon { color: var(--success); }
.sel-row.err .sel-icon { color: var(--danger); }
.sel-row.warn .sel-icon { color: var(--warning); }
.sel-info { color: var(--text-secondary); flex: 1; }
.sel-hint { color: var(--text-muted); font-size: .7rem; font-style: italic; }

.log-panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); max-height: 200px; overflow-y: auto; padding: 10px 14px; }
.log-panel h4 { font-size: .8rem; margin-bottom: 6px; color: var(--text-secondary); position: sticky; top: 0; background: var(--surface); padding-bottom: 6px; }
.log-empty { color: var(--text-muted); font-size: .78rem; padding: 8px 0; }
.log-row { display: flex; align-items: baseline; gap: 6px; padding: 3px 0; font-size: .76rem; font-family: var(--font-mono); }
.log-row.pass { color: var(--success); }
.log-row.fail { color: var(--danger); }
.log-icon { font-weight: 700; flex-shrink: 0; }

.assertion-panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px 14px; }
.assertion-panel h4 { font-size: .8rem; margin-bottom: 8px; color: var(--text-secondary); }
.assert-row { display: flex; align-items: baseline; gap: 6px; padding: 3px 0; font-size: .76rem; border-bottom: 1px solid var(--border-light); flex-wrap: wrap; }
.assert-row:last-child { border-bottom: none; }
.assert-row.pass { color: var(--success); }
.assert-row.fail { color: var(--danger); }
.assert-row code { font-family: var(--font-mono); font-size: .72rem; background: var(--code-bg); padding: 1px 6px; border-radius: 3px; color: var(--text); }
.assert-detail { color: var(--text-muted); font-size: .72rem; }

.btn-cheatsheet { width: 100%; padding: 8px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); color: var(--text-secondary); cursor: pointer; font-size: .78rem; font-family: var(--font-sans); font-weight: 500; transition: all var(--fast); text-align: left; }
.btn-cheatsheet:hover { background: var(--surface-hover); }
.cheatsheet-panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px; overflow-x: auto; }
.cheat-table { width: 100%; border-collapse: collapse; font-size: .72rem; }
.cheat-table th { text-align: left; padding: 6px 8px; border-bottom: 2px solid var(--border); font-weight: 650; color: var(--text-secondary); white-space: nowrap; }
.cheat-table td { padding: 5px 8px; border-bottom: 1px solid var(--border-light); }
.cheat-table code { font-family: var(--font-mono); font-size: .68rem; padding: 2px 5px; border-radius: 3px; background: var(--code-bg); color: var(--primary); white-space: nowrap; display: inline-block; max-width: 200px; overflow: hidden; text-overflow: ellipsis; }
</style>
