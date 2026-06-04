<template>
  <div class="lab-page">
    <!-- Tabs -->
    <div class="tabs">
      <button :class="{ active: tab==='xss' }" @click="tab='xss'">💉 XSS 跨站脚本</button>
      <button :class="{ active: tab==='sqli' }" @click="tab='sqli'">🗄️ SQL 注入</button>
    </div>

    <!-- ==================== XSS ==================== -->
    <div v-if="tab==='xss'">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>🎯 反射型 XSS 攻击模拟</h3>
        <p class="desc">下面的搜索框存在反射型XSS漏洞——输入会被直接插入HTML而不做转义。尝试注入脚本。</p>

        <div class="xss-bar">
          <input v-model="xssPayload" @keyup.enter="submitXSS" placeholder='<script>alert("XSS")</script>' class="xss-input">
          <button class="btn-primary" @click="submitXSS">💉 注入</button>
        </div>

        <div v-if="xssResult" class="xss-result">
          <div class="result-panel unsafe">
            <div class="panel-label">❌ 不安全渲染（原始输入直接插入HTML）</div>
            <div class="panel-html" v-html="xssResult.unsafe_html"></div>
            <div class="panel-code"><code>{{ xssResult.unsafe_html }}</code></div>
          </div>
          <div class="result-panel safe">
            <div class="panel-label">✅ 安全渲染（HTML实体编码后）</div>
            <div class="panel-html" v-html="xssResult.safe_html"></div>
            <div class="panel-code"><code>{{ xssResult.safe_html }}</code></div>
          </div>
          <div class="xss-verdict" :class="{ exploited: xssResult.script_executed }">
            {{ xssResult.script_executed ? '⚠️ 脚本执行成功！XSS 攻击有效。' : '🔒 输入已被转义，攻击无效。' }}
          </div>
        </div>
      </div>

      <div class="card">
        <h3>📝 试试这些 Payload</h3>
        <div class="payload-chips">
          <button v-for="p in xssPayloads" :key="p.label" class="payload-chip" @click="xssPayload=p.value; submitXSS()">
            <strong>{{ p.label }}</strong><span>{{ p.value }}</span>
          </button>
        </div>
      </div>

      <div class="card" style="margin-top:var(--space-md);">
        <h3>🛡️ 防御方案</h3>
        <ul class="defense-list">
          <li><strong>输出编码</strong> — 将 &lt; &gt; " ' &amp; 转义为 HTML 实体</li>
          <li><strong>CSP 头</strong> — Content-Security-Policy 限制脚本来源</li>
          <li><strong>HttpOnly Cookie</strong> — 防止 JS 读取会话 Cookie</li>
          <li><strong>输入校验</strong> — 白名单验证，拒绝不必要的 HTML 标签</li>
          <li><strong>X-XSS-Protection</strong> — 启用浏览器内置 XSS 过滤器</li>
        </ul>
      </div>
    </div>

    <!-- ==================== SQL Injection ==================== -->
    <div v-if="tab==='sqli'">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>🎯 SQL 注入攻击模拟</h3>
        <p class="desc">这个登录表单使用字符串拼接构造SQL查询。尝试用 SQL 注入绕过身份验证。</p>

        <div class="login-mock">
          <div class="field"><label>用户名</label><input v-model="sqliUser" placeholder="admin" class="form-input" @keyup.enter="submitSQLI"></div>
          <div class="field"><label>密码</label><input v-model="sqliPass" type="text" placeholder="password" class="form-input" @keyup.enter="submitSQLI"></div>
          <button class="btn-primary" style="width:100%;justify-content:center;padding:10px;margin-top:8px;" @click="submitSQLI">🔓 登录</button>
        </div>

        <div v-if="sqliResult" class="sqli-result">
          <div class="query-box">
            <div class="query-label">实际执行的 SQL 查询：</div>
            <pre class="query-sql">{{ sqliResult.vulnerable_query }}</pre>
          </div>

          <div class="query-box secure" style="margin-top:8px;">
            <div class="query-label">安全的参数化查询：</div>
            <pre class="query-sql">{{ sqliResult.secure_query }}</pre>
          </div>

          <div v-if="sqliResult.injection_detected" class="injection-detected">
            <h4>🔍 检测到注入攻击：</h4>
            <div v-for="(inj, i) in sqliResult.injection_types" :key="i" class="inj-item">
              <code>{{ inj.pattern }}</code><span>{{ inj.description }}</span>
            </div>
          </div>

          <div class="sqli-verdict" :class="{ bypassed: sqliResult.auth_bypassed, blocked: !sqliResult.auth_bypassed && sqliResult.injection_detected, normal: !sqliResult.injection_detected }">
            <template v-if="sqliResult.auth_bypassed">⚠️ 认证绕过成功！攻击者以任意身份登录。</template>
            <template v-else-if="sqliResult.injection_detected">🔍 检测到注入尝试但未绕过认证。</template>
            <template v-else>{{ sqliResult.matched_user ? '✅ 正常登录成功' : '❌ 用户名或密码错误' }}</template>
          </div>

          <div class="lesson-box">💡 <strong>教训：</strong>{{ sqliResult.lesson }}</div>
        </div>
      </div>

      <div class="card">
        <h3>📝 经典注入 Payload</h3>
        <div class="sqli-cheats">
          <div v-for="p in sqliPayloads" :key="p.label" class="sqli-cheat" @click="sqliUser=p.user; sqliPass=p.pass; submitSQLI()">
            <strong>{{ p.label }}</strong>
            <span>用户名: <code>{{ p.user }}</code> 密码: <code>{{ p.pass }}</code></span>
            <span class="cheat-desc">{{ p.desc }}</span>
          </div>
        </div>
      </div>

      <div class="card" style="margin-top:var(--space-md);">
        <h3>🛡️ 防御方案</h3>
        <ul class="defense-list">
          <li><strong>参数化查询</strong> — 使用 ? 占位符，数据库驱动自动转义</li>
          <li><strong>ORM 框架</strong> — SQLAlchemy/Django ORM 自动处理转义</li>
          <li><strong>存储过程</strong> — 预编译 SQL，参数与查询结构分离</li>
          <li><strong>最小权限</strong> — 应用账户只给必要权限（SELECT/INSERT，不给 DROP）</li>
          <li><strong>输入校验</strong> — 白名单验证，拒绝特殊字符</li>
          <li><strong>WAF</strong> — Web Application Firewall 拦截常见攻击模式</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const tab = ref('xss')

// XSS
const xssPayload = ref('')
const xssResult = ref(null)

const xssPayloads = [
  { label: '基本 Script', value: '<scr' + 'ipt>alert("XSS")</scr' + 'ipt>' },
  { label: 'Img Onerror', value: '<img src=x onerror=alert(1)>' },
  { label: 'SVG Onerror', value: '<svg onload=alert(1)>' },
  { label: 'Body Onerror', value: '<body onload=alert(1)>' },
  { label: 'Iframe Src', value: '<iframe src="javascript:alert(1)">' },
]

async function submitXSS() {
  try {
    const r = await fetch('/api/labs/security/xss', {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('qa-pro-token')}` },
      body: JSON.stringify({ payload: xssPayload.value }),
    })
    xssResult.value = await r.json()
  } catch (e) {
    xssResult.value = { unsafe_html: '', safe_html: '', error: '请求失败: ' + e.message }
  }
}

// SQL Injection
const sqliUser = ref('admin'), sqliPass = ref('')
const sqliResult = ref(null)

const sqliPayloads = [
  { label: 'OR 1=1', user: "admin' OR 1=1 --", pass: 'anything', desc: '经典永真绕过 —— 注释掉密码检查' },
  { label: 'OR ""=""', user: "admin' OR ''='' --", pass: 'anything', desc: 'OR 空串等于空串 —— 永远为真' },
  { label: 'Admin Bypass', user: "admin'--", pass: '', desc: '直接注释掉密码部分 —— 只要用户名对就登录' },
  { label: 'Union Injection', user: "x' UNION SELECT 1,'admin','hacked','admin' --", pass: '', desc: 'UNION注入 —— 返回攻击者构造的假用户' },
]

async function submitSQLI() {
  try {
    const r = await fetch('/api/labs/security/sqli', {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('qa-pro-token')}` },
      body: JSON.stringify({ username: sqliUser.value, password: sqliPass.value }),
    })
    sqliResult.value = await r.json()
  } catch (e) {
    sqliResult.value = { query: '', result: '', error: '请求失败: ' + e.message }
  }
}
</script>

<style scoped>
.lab-page { max-width: 860px; margin: 0 auto; }

.tabs { display: flex; gap: 4px; margin-bottom: var(--space-lg); background: var(--surface); border-radius: var(--radius); padding: 4px; border: 1px solid var(--border); }
.tabs button { flex: 1; padding: 12px; border: none; background: none; border-radius: 8px; cursor: pointer; font-size: .86rem; color: var(--text-secondary); font-weight: 500; transition: all var(--fast); font-family: var(--font-sans); }
.tabs button.active { background: var(--danger); color: #fff; font-weight: 600; }

.desc { font-size: .84rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 14px; }

/* XSS */
.xss-bar { display: flex; gap: 8px; }
.xss-input { flex: 1; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-family: var(--font-mono); font-size: .84rem; background: var(--surface); color: var(--text); outline: none; }
.xss-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.xss-result { margin-top: 16px; }
.result-panel { border-radius: var(--radius); overflow: hidden; margin-bottom: 10px; border: 1px solid var(--border); }
.result-panel.unsafe { border-color: var(--danger); }
.result-panel.safe { border-color: var(--success); }
.panel-label { padding: 8px 14px; font-size: .76rem; font-weight: 600; }
.result-panel.unsafe .panel-label { background: var(--danger-light); color: var(--danger); }
.result-panel.safe .panel-label { background: var(--success-light); color: var(--success); }
.panel-html { padding: 12px 16px; background: var(--bg); font-size: .84rem; border-bottom: 1px solid var(--border-light); }
.panel-code { padding: 10px 16px; background: #1a1a2e; }
.panel-code code { font-family: var(--font-mono); font-size: .72rem; color: #e5e7eb; }
.xss-verdict { padding: 12px 16px; border-radius: var(--radius-sm); font-weight: 600; font-size: .84rem; text-align: center; }
.xss-verdict.exploited { background: var(--danger-light); color: var(--danger); }
.xss-verdict:not(.exploited) { background: var(--success-light); color: var(--success); }

.payload-chips { display: flex; flex-direction: column; gap: 6px; }
.payload-chip { display: flex; flex-direction: column; gap: 2px; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); cursor: pointer; text-align: left; transition: all var(--fast); font-family: var(--font-sans); }
.payload-chip:hover { border-color: var(--primary); background: var(--primary-light); }
.payload-chip strong { font-size: .82rem; }
.payload-chip span { font-family: var(--font-mono); font-size: .74rem; color: var(--text-secondary); }

/* SQLi */
.login-mock { max-width: 400px; margin: 0 auto 16px; padding: 20px; background: var(--bg); border-radius: var(--radius); }
.field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; }
.field label { font-size: .78rem; font-weight: 600; color: var(--text-secondary); }
.form-input { padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: .86rem; font-family: var(--font-mono); background: var(--surface); color: var(--text); outline: none; width: 100%; transition: border-color var(--fast); }
.form-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.query-box { background: #1a1a2e; border-radius: var(--radius); overflow: hidden; }
.query-box.secure { border: 1px solid var(--success); }
.query-label { padding: 8px 14px; font-size: .72rem; color: #a0a0b8; background: #16162a; }
.query-sql { padding: 12px 16px; margin: 0; font-family: var(--font-mono); font-size: .78rem; line-height: 1.7; color: #e5e7eb; white-space: pre-wrap; }

.injection-detected { margin-top: 12px; padding: 14px; background: var(--warning-light); border-radius: var(--radius); border: 1px solid var(--warning); }
.injection-detected h4 { font-size: .82rem; margin-bottom: 8px; }
.inj-item { display: flex; gap: 8px; align-items: baseline; padding: 4px 0; font-size: .78rem; }
.inj-item code { background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-size: .72rem; font-family: var(--font-mono); }
.inj-item span { color: var(--text-secondary); }

.sqli-verdict { padding: 12px 16px; border-radius: var(--radius-sm); font-weight: 600; font-size: .84rem; text-align: center; margin-top: 8px; }
.sqli-verdict.bypassed { background: var(--danger-light); color: var(--danger); }
.sqli-verdict.blocked { background: var(--warning-light); color: #92400e; }
.sqli-verdict.normal { background: var(--bg); color: var(--text-secondary); }

.lesson-box { margin-top: 10px; padding: 12px; background: var(--primary-light); border-radius: var(--radius); font-size: .84rem; line-height: 1.6; }

.sqli-cheats { display: flex; flex-direction: column; gap: 6px; }
.sqli-cheat { display: flex; flex-direction: column; gap: 2px; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); cursor: pointer; text-align: left; transition: all var(--fast); font-family: var(--font-sans); }
.sqli-cheat:hover { border-color: var(--primary); background: var(--primary-light); }
.sqli-cheat strong { font-size: .82rem; }
.sqli-cheat span { font-size: .76rem; color: var(--text-secondary); font-family: var(--font-mono); }
.cheat-desc { font-size: .74rem; color: var(--text-muted); }

.defense-list { list-style: none; font-size: .84rem; line-height: 2.2; padding: 0; }
.defense-list li { padding: 2px 0; }
.defense-list strong { color: var(--primary); }
</style>
