<template>
  <div class="lab-page">
    <div class="proto-tabs">
      <button v-for="t in tabs" :key="t.id" class="proto-tab" :class="{ active: activeTab === t.id }"
        @click="activeTab = t.id">{{ t.icon }} {{ t.label }}</button>
    </div>

    <!-- ====== TCP ====== -->
    <div v-if="activeTab === 'tcp'" class="proto-content">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>🔗 TCP 三次握手</h3>
        <div class="handshake-viz">
          <div class="hs-party client"><span>客户端</span><span class="hs-label">CLOSED</span></div>
          <div class="hs-arrows">
            <div class="hs-step" :class="{ active: tcpStep >= 1 }" @click="tcpStep = tcpStep >= 1 ? tcpStep : 1">
              <span class="hs-arrow">→ SYN →</span><span class="hs-desc">seq=x, SYN=1</span>
            </div>
            <div class="hs-step" :class="{ active: tcpStep >= 2 }" @click="tcpStep = tcpStep >= 2 ? tcpStep : 2">
              <span class="hs-arrow">← SYN-ACK ←</span><span class="hs-desc">seq=y, ack=x+1, SYN=1, ACK=1</span>
            </div>
            <div class="hs-step" :class="{ active: tcpStep >= 3 }" @click="tcpStep = tcpStep >= 3 ? tcpStep : 3">
              <span class="hs-arrow">→ ACK →</span><span class="hs-desc">seq=x+1, ack=y+1, ACK=1</span>
            </div>
          </div>
          <div class="hs-party server"><span>服务器</span><span class="hs-label">{{ tcpStep >= 1 ? (tcpStep >= 2 ? 'ESTABLISHED' : 'SYN-RCVD') : 'LISTEN' }}</span></div>
        </div>
        <p class="hs-status">客户端状态：<strong>{{ ['CLOSED','SYN-SENT','SYN-SENT','ESTABLISHED'][tcpStep] }}</strong> &nbsp;|&nbsp; 点击箭头逐步演示</p>
        <button class="btn-outline" style="margin-top:8px;" @click="tcpStep = 0">🔄 重置</button>
      </div>

      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>📝 随堂测验</h3>
        <p class="quiz-q">TCP 三次握手中，第二步服务器发送的报文包含哪些标志位？</p>
        <button v-for="(o,i) in tcpQuiz.options" :key="i" class="quiz-opt" :class="{ selected: tcpQuiz.chosen===i, correct: tcpQuiz.submitted && i===tcpQuiz.answer, wrong: tcpQuiz.submitted && tcpQuiz.chosen===i && i!==tcpQuiz.answer }" :disabled="tcpQuiz.submitted" @click="tcpQuiz.chosen=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span><span>{{ o }}</span>
        </button>
        <div v-if="!tcpQuiz.submitted" style="margin-top:10px;">
          <button class="btn-primary" :disabled="tcpQuiz.chosen===-1" @click="checkTcpQuiz">✅ 提交</button>
        </div>
        <div v-if="tcpQuiz.submitted" class="explain">{{ tcpQuiz.chosen===tcpQuiz.answer ? '✅ 正确！' : '❌ 错误。' }} {{ tcpQuiz.explain }}</div>
      </div>
    </div>

    <!-- ====== HTTP ====== -->
    <div v-if="activeTab === 'http'" class="proto-content">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>🌐 HTTP 版本对比</h3>
        <div class="http-compare">
          <div v-for="v in httpVersions" :key="v.ver" class="http-card" :class="{ highlight: httpSelected === v.ver }" @click="httpSelected = v.ver">
            <h4>{{ v.ver }}</h4>
            <ul>
              <li v-for="f in v.features" :key="f">• {{ f }}</li>
            </ul>
          </div>
        </div>
        <div v-if="httpSelected" class="http-detail">📌 {{ httpVersions.find(v=>v.ver===httpSelected)?.detail }}</div>
      </div>

      <div class="card">
        <h3>📝 HTTP 状态码速查</h3>
        <div class="status-grid">
          <div v-for="s in httpStatuses" :key="s.code" class="status-item">
            <span class="status-code" :class="s.level">{{ s.code }}</span>
            <span class="status-text">{{ s.text }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ====== TLS ====== -->
    <div v-if="activeTab === 'tls'" class="proto-content">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>🔐 TLS 1.3 握手过程</h3>
        <div class="tls-flow">
          <div v-for="(step, i) in tlsSteps" :key="i" class="tls-step" :class="{ done: tlsProgress > i }" @click="tlsProgress = Math.max(tlsProgress, i+1)">
            <span class="tls-num">{{ i+1 }}</span>
            <div>
              <strong>{{ step.title }}</strong>
              <p>{{ step.desc }}</p>
            </div>
          </div>
        </div>
        <button class="btn-outline" @click="tlsProgress = 0">🔄 重置</button>
        <button class="btn-primary" style="margin-left:8px;" @click="tlsProgress = tlsSteps.length">▶ 全部展开</button>
      </div>

      <div class="card">
        <h3>📝 证书链验证要点</h3>
        <ul class="checklist">
          <li>🔍 证书是否在有效期内（notBefore / notAfter）</li>
          <li>🔍 证书 CN/SAN 是否匹配访问域名</li>
          <li>🔍 颁发者 CA 是否在操作系统/浏览器信任库中</li>
          <li>🔍 证书链是否完整（叶证书 → 中间CA → 根CA）</li>
          <li>🔍 吊销状态检查（CRL / OCSP）</li>
          <li>🔍 签名算法是否安全（禁止 MD5/SHA-1）</li>
        </ul>
      </div>
    </div>

    <!-- ====== DNS ====== -->
    <div v-if="activeTab === 'dns'" class="proto-content">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>🌍 DNS 解析流程</h3>
        <div class="dns-flow">
          <div class="dns-party">💻 客户端</div>
          <div class="dns-arrow">→ www.example.com →</div>
          <div class="dns-resolver">
            <div class="dns-step-card">
              <span>1️⃣ 浏览器缓存</span><span class="dns-time">~0ms</span>
            </div>
            <div class="dns-step-card">
              <span>2️⃣ OS hosts 文件</span><span class="dns-time">~0ms</span>
            </div>
            <div class="dns-step-card">
              <span>3️⃣ 本地 DNS 解析器</span><span class="dns-time">~5ms</span>
            </div>
            <div class="dns-step-card">
              <span>4️⃣ 根域名服务器</span><span class="dns-time">~30ms</span>
            </div>
            <div class="dns-step-card">
              <span>5️⃣ .com TLD 服务器</span><span class="dns-time">~50ms</span>
            </div>
            <div class="dns-step-card">
              <span>6️⃣ example.com 权威DNS</span><span class="dns-time">~80ms</span>
            </div>
          </div>
          <div class="dns-arrow">← 93.184.216.34 ←</div>
          <div class="dns-party">💻 客户端（缓存结果）</div>
        </div>
      </div>

      <div class="card">
        <h3>📝 DNS 记录类型</h3>
        <div class="dns-records">
          <div v-for="r in dnsRecords" :key="r.type" class="dns-record">
            <code>{{ r.type }}</code>
            <span>{{ r.desc }}</span>
            <span class="dns-example">{{ r.example }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ====== WebSocket ====== -->
    <div v-if="activeTab === 'ws'" class="proto-content">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>🔌 WebSocket vs HTTP</h3>
        <div class="ws-compare">
          <div class="ws-col">
            <h4>HTTP</h4>
            <ul>
              <li>客户端发起请求</li>
              <li>服务器只能响应</li>
              <li>每次请求独立</li>
              <li>头部开销大</li>
              <li>适合：REST API、网页</li>
            </ul>
          </div>
          <div class="ws-col highlight-col">
            <h4>WebSocket</h4>
            <ul>
              <li>双向全双工通信</li>
              <li>服务器可主动推送</li>
              <li>一次连接持续通信</li>
              <li>帧头部仅 2-10 字节</li>
              <li>适合：聊天、实时数据、推送通知</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="card">
        <h3>📝 测试要点</h3>
        <div class="quiz-q">WebSocket 测试中最容易遗漏的检查点是？</div>
        <button v-for="(o,i) in wsQuiz.options" :key="i" class="quiz-opt" :class="{ selected: wsQuiz.chosen===i, correct: wsQuiz.submitted && i===wsQuiz.answer, wrong: wsQuiz.submitted && wsQuiz.chosen===i && i!==wsQuiz.answer }" :disabled="wsQuiz.submitted" @click="wsQuiz.chosen=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span><span>{{ o }}</span>
        </button>
        <div v-if="!wsQuiz.submitted" style="margin-top:10px;">
          <button class="btn-primary" :disabled="wsQuiz.chosen===-1" @click="checkWsQuiz">✅ 提交</button>
        </div>
        <div v-if="wsQuiz.submitted" class="explain">{{ wsQuiz.chosen===wsQuiz.answer ? '✅ 正确！' : '❌ 错误。' }} {{ wsQuiz.explain }}</div>
      </div>
    </div>

    <!-- ====== 抓包分析 ====== -->
    <div v-if="activeTab === 'capture'" class="proto-content">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>📦 HTTP 请求/响应原始报文分析</h3>
        <p class="task-desc">🎯 <strong>目标：</strong>{{ captureScenarios[currentCapture].task }}</p>
        <div class="capture-bar">
          <button v-for="(s,i) in captureScenarios" :key="i" class="scenario-btn" :class="{ active: currentCapture === i }" @click="currentCapture = i; captureAnswer=''; captureResult=null">{{ s.label }}</button>
        </div>

        <div class="raw-http">
          <div class="raw-section">
            <div class="raw-label">📤 Request</div>
            <pre class="raw-text">{{ captureScenarios[currentCapture].request }}</pre>
          </div>
          <div class="raw-section">
            <div class="raw-label">📥 Response</div>
            <pre class="raw-text">{{ captureScenarios[currentCapture].response }}</pre>
          </div>
        </div>

        <div class="capture-question">{{ captureScenarios[currentCapture].question }}</div>
        <div class="capture-answers">
          <button v-for="(o,i) in captureScenarios[currentCapture].options" :key="i"
            class="quiz-opt" :class="{ selected: captureChosen===i, correct: captureResult && i===captureScenarios[currentCapture].answer, wrong: captureResult && captureChosen===i && i!==captureScenarios[currentCapture].answer }"
            :disabled="captureResult !== null"
            @click="captureChosen=i">{{ 'ABCD'[i] }}. {{ o }}</button>
        </div>
        <button v-if="captureResult===null" class="btn-primary" style="margin-top:10px;" :disabled="captureChosen===-1" @click="checkCapture">✅ 提交</button>
        <div v-if="captureResult!==null" class="explain">{{ captureResult ? '✅ 正确！' : '❌ 错误。' }} {{ captureScenarios[currentCapture].explain }}</div>
      </div>
    </div>

    <!-- ====== 弱网测试 ====== -->
    <div v-if="activeTab === 'weaknet'" class="proto-content">
      <div class="card" style="margin-bottom:var(--space-md);">
        <h3>📶 弱网条件与测试策略</h3>
        <div class="weaknet-grid">
          <div v-for="n in weakNetworks" :key="n.name" class="weaknet-card" @click="weakSelected = n.name">
            <h4>{{ n.icon }} {{ n.name }}</h4>
            <div class="wn-specs">
              <span>↓ {{ n.down }}</span><span>↑ {{ n.up }}</span><span>{{ n.latency }}</span>
            </div>
            <p>{{ n.desc }}</p>
            <div class="wn-test">{{ n.testStrategy }}</div>
          </div>
        </div>
        <div v-if="weakSelected" class="http-detail">💡 <strong>{{ weakSelected }}测试要点：</strong>{{ weakNetworks.find(n=>n.name===weakSelected)?.detail }}</div>
      </div>

      <div class="card">
        <h3>📝 弱网场景判断题</h3>
        <div class="quiz-q">APP 在 2G 网络下打开首页，30 秒后白屏。以下哪个是 QA 最应该优先验证的？</div>
        <button v-for="(o,i) in weakQuiz.options" :key="i" class="quiz-opt" :class="{ selected: weakQuiz.chosen===i, correct: weakQuiz.submitted && i===weakQuiz.answer, wrong: weakQuiz.submitted && weakQuiz.chosen===i && i!==weakQuiz.answer }" :disabled="weakQuiz.submitted" @click="weakQuiz.chosen=i">
          <span class="opt-letter">{{ 'ABCD'[i] }}</span><span>{{ o }}</span>
        </button>
        <div v-if="!weakQuiz.submitted" style="margin-top:10px;">
          <button class="btn-primary" :disabled="weakQuiz.chosen===-1" @click="checkWeakQuiz">✅ 提交</button>
        </div>
        <div v-if="weakQuiz.submitted" class="explain">{{ weakQuiz.chosen===weakQuiz.answer ? '✅ 正确！' : '❌ 错误。' }} {{ weakQuiz.explain }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const activeTab = ref('tcp')
const tabs = [
  { id: 'tcp', label: 'TCP 握手', icon: '🔗' },
  { id: 'http', label: 'HTTP 协议', icon: '🌐' },
  { id: 'tls', label: 'TLS 加密', icon: '🔐' },
  { id: 'dns', label: 'DNS 解析', icon: '🌍' },
  { id: 'ws', label: 'WebSocket', icon: '🔌' },
  { id: 'capture', label: '抓包分析', icon: '📦' },
  { id: 'weaknet', label: '弱网测试', icon: '📶' },
]

// TCP
const tcpStep = ref(0)
const tcpQuiz = reactive({ options: ['A. SYN', 'B. ACK', 'C. SYN + ACK', 'D. FIN'], answer: 2, chosen: -1, submitted: false, explain: '服务器在收到客户端SYN后，回复SYN-ACK报文，同时确认客户端的SYN（ACK=1）并发送自己的SYN（SYN=1），两个标志位同时置位。' })
function checkTcpQuiz() { tcpQuiz.submitted = true }

// HTTP
const httpSelected = ref('')
const httpVersions = [
  { ver: 'HTTP/1.1', features: ['文本协议，人类可读', '持久连接 (Keep-Alive)', '队头阻塞 (HOL Blocking)', '管道化 (Pipelining)', '6 个并发连接限制'], detail: 'HTTP/1.1 仍是使用最广泛的版本。队头阻塞意味着前一个请求的响应必须完整到达后才能发送下一个响应。' },
  { ver: 'HTTP/2', features: ['二进制分帧', '多路复用 (无HOL)', '头部压缩 (HPACK)', '服务器推送 (Server Push)', '单个连接'], detail: 'HTTP/2 通过多路复用在一个TCP连接上并行传输多个流。但TCP层的丢包仍会导致所有流阻塞（TCP HOL）。' },
  { ver: 'HTTP/3', features: ['基于 QUIC (UDP)', '0-RTT 快速握手', '无 TCP HOL 阻塞', '连接迁移', '内置 TLS 1.3'], detail: 'HTTP/3 用 QUIC 替代 TCP，彻底解决队头阻塞。连接迁移支持从WiFi切到4G不断连。目前已被 Google/Facebook/CDN 广泛部署。' },
]
const httpStatuses = [
  { code: '200', text: 'OK — 请求成功', level: 'ok' },
  { code: '201', text: 'Created — 资源创建成功', level: 'ok' },
  { code: '301', text: '永久重定向', level: 'redirect' },
  { code: '302', text: '临时重定向', level: 'redirect' },
  { code: '400', text: 'Bad Request — 请求格式错误', level: 'client' },
  { code: '401', text: 'Unauthorized — 未认证', level: 'client' },
  { code: '403', text: 'Forbidden — 无权限', level: 'client' },
  { code: '404', text: 'Not Found — 资源不存在', level: 'client' },
  { code: '429', text: 'Too Many Requests — 限流', level: 'client' },
  { code: '500', text: '服务器内部错误', level: 'server' },
  { code: '502', text: 'Bad Gateway — 网关错误', level: 'server' },
  { code: '503', text: 'Service Unavailable — 服务不可用', level: 'server' },
  { code: '504', text: 'Gateway Timeout — 网关超时', level: 'server' },
]

// TLS
const tlsProgress = ref(0)
const tlsSteps = [
  { title: 'Client Hello', desc: '客户端发送支持的加密套件列表、TLS版本、随机数。' },
  { title: 'Server Hello', desc: '服务器选择加密套件、发送证书链、随机数。' },
  { title: '证书验证', desc: '客户端验证证书有效性（链、域名、有效期、吊销状态）。' },
  { title: '密钥交换', desc: '通过 ECDHE 或 RSA 交换预主密钥，双方计算出会话密钥。' },
  { title: 'Finished', desc: '双方发送 Finished 消息，用会话密钥加密，握手完成。' },
]

// DNS
const dnsRecords = [
  { type: 'A', desc: '域名 → IPv4 地址', example: 'example.com → 93.184.216.34' },
  { type: 'AAAA', desc: '域名 → IPv6 地址', example: 'example.com → 2606:2800:...' },
  { type: 'CNAME', desc: '域名别名（指向另一个域名）', example: 'www → example.com' },
  { type: 'MX', desc: '邮件服务器记录', example: 'mail.example.com 优先级 10' },
  { type: 'TXT', desc: '文本记录（SPF/DKIM 等）', example: 'v=spf1 include:_spf.google.com ~all' },
  { type: 'NS', desc: '权威 DNS 服务器', example: 'ns1.example.com' },
  { type: 'PTR', desc: '反向解析（IP → 域名）', example: '34.216.184.93 → example.com' },
]

// WebSocket
const wsQuiz = reactive({ options: ['A. 连接建立后的负载测试', 'B. 断线重连和心跳保活机制', 'C. 消息格式和内容', 'D. 并发用户数'], answer: 1, chosen: -1, submitted: false, explain: '断线重连和心跳保活是WebSocket测试中最容易遗漏的。网络不稳定时连接断开，客户端能否正确重连？心跳超时是否正确处理？这些边界情况比正常通信更重要。' })
function checkWsQuiz() { wsQuiz.submitted = true }

// ====== 抓包分析 ======
const currentCapture = ref(0)
const captureChosen = ref(-1)
const captureResult = ref(null)
const captureScenarios = [
  {
    label: '🔑 Token 泄露',
    task: '检查以下 HTTP 请求，找出安全隐患',
    request: 'GET /api/user/profile HTTP/1.1\nHost: app.example.com\nAuthorization: Bearer eyJhbGciOiJIUzI1NiIs...\nCookie: session=abc123; token=eyJhbGciOiJIUzI1NiIs...\nUser-Agent: Mozilla/5.0\n\n',
    response: 'HTTP/1.1 200 OK\nContent-Type: application/json\nSet-Cookie: session=def456; HttpOnly\nX-Debug-Token: admin-secret-123\n\n{"id":1,"username":"admin","role":"admin","api_key":"sk-abc123456"}',
    question: '这段抓包数据中，有几处安全隐患？',
    options: ['A. 1处：Cookie中的token重复', 'B. 2处：Cookie未设HttpOnly + 响应暴露api_key', 'C. 3处：Cookie未设HttpOnly + X-Debug-Token泄露 + 响应暴露api_key', 'D. 0处，都是正常的'],
    answer: 2,
    explain: '3处隐患：①Cookie中的token没有HttpOnly/Secure标记可被XSS窃取；②X-Debug-Token响应头泄露了调试密钥；③响应body直接返回了api_key明文。另外Authorization头中的token在URL参数或Referer中间接泄露也是常见问题。',
  },
  {
    label: '📋 参数篡改',
    task: '分析请求，找出可以被攻击者利用的参数',
    request: 'POST /api/orders/create HTTP/1.1\nHost: shop.example.com\nContent-Type: application/json\nCookie: session=user123\n\n{"product_id":42,"quantity":1,"price":99.00,"total":99.00,"discount_code":"","user_role":"user"}',
    response: 'HTTP/1.1 200 OK\n\n{"order_id":1001,"status":"created","total_paid":0.01}',
    question: '攻击者可以如何利用这个接口？',
    options: ['A. 修改product_id购买其他商品', 'B. 修改price参数为0.01实现低价购买', 'C. 修改user_role为admin提权', 'D. B和C都可以'],
    answer: 3,
    explain: '关键问题：①price和total由客户端传入——攻击者改price=0.01就能以1分钱购买；②user_role由客户端控制——改为admin可能获取管理员权限。正确做法：price/total由服务端根据product_id查数据库计算，user_role从服务端session中读取而非客户端传入。',
  },
  {
    label: '💉 XSS Payload',
    task: '检查响应中是否存在XSS风险',
    request: 'GET /search?q=\x3Cscript\x3Ealert(1)\x3C/script\x3E HTTP/1.1\nHost: blog.example.com\n\n',
    response: 'HTTP/1.1 200 OK\nContent-Type: text/html\nX-XSS-Protection: 0\n\n<html><body>\n<h1>搜索结果：&lt;script&gt;alert(1)&lt;/script&gt;</h1>\n<div class="result">未找到与 \x3Cscript\x3Ealert(1)\x3C/script\x3E 相关的结果</div>\n</body></html>',
    question: '这个响应存在什么问题？',
    options: ['A. 没有问题，已经做了HTML转义', 'B. X-XSS-Protection: 0 关闭了浏览器XSS过滤器', 'C. 第一个h1做了转义，但第二个div没有——存在反射型XSS', 'D. B和C都是问题'],
    answer: 3,
    explain: '两个问题：①X-XSS-Protection: 0主动关闭了浏览器XSS Auditor；②h1中的搜索词做了HTML实体编码（正确），但div中的搜索词直接插入HTML（错误）——形成了反射型XSS。修复：对所有输出上下文做正确的编码（HTML编码/JS编码/URL编码）。',
  },
]

function checkCapture() {
  captureResult.value = captureChosen.value === captureScenarios[currentCapture.value].answer
}

// ====== 弱网测试 ======
const weakSelected = ref('')
const weakNetworks = [
  { name: '2G (GPRS)', icon: '🐢', down: '~40Kbps', up: '~20Kbps', latency: '~800ms', desc: '极慢，图片逐行加载', testStrategy: '测：超时设置≥30s, 降级策略(低清图/纯文字), loading状态, 大文件下载断线', detail: '2G下用户期望极低，核心验证：①能否在30s内展示首屏内容 ②超时是否给友好提示而非白屏 ③大图片是否有占位+渐进加载' },
  { name: '3G', icon: '🐌', down: '~1Mbps', up: '~500Kbps', latency: '~200ms', desc: '勉强可用，加载明显感知', testStrategy: '测：视频自动降清晰度, 分页加载, 接口超时5-10s, 请求合并减少往返', detail: '3G是很多地区的主流网络。压缩资源(Brotli/Gzip)、减少请求数(sprites/bundle)、关键路径优先加载。' },
  { name: '4G', icon: '🏃', down: '~10Mbps', up: '~5Mbps', latency: '~50ms', desc: '流畅，正常用户体验基线', testStrategy: '测：视频自动播放, 实时通信, WebSocket连接, 大文件上传下载, 并发请求数', detail: '4G是QA的基线网络。验证点：首屏<3s, 视频<2s起播, API响应<1s。弱网测试在4G基础上限速验证降级行为。' },
  { name: '高延迟', icon: '⏳', down: '正常', up: '正常', latency: '>1000ms', desc: '卫星/跨境链路，RTT极高', testStrategy: '测：超时重试机制, API合并, 预加载策略, 连接复用(HTTP/2多路复用)', detail: '高延迟≠低带宽。验证：TCP握手开销(高延迟下TLS握手代价很大)、API批量请求替代逐个请求、CDN边缘节点就近接入。' },
  { name: '高丢包', icon: '📉', down: '正常', up: '正常', latency: '正常', desc: '5%-30%丢包率，数据损坏', testStrategy: '测：重传机制, 断线重连, 幂等性, 数据一致性, 文件校验', detail: '丢包环境下TCP自动重传但会降速。验证：上传文件MD5校验、下单等关键操作的幂等性(重复提交不应创建重复订单)、WebSocket消息丢失后的补偿。' },
  { name: '网络切换', icon: '🔄', down: '变化', up: '变化', latency: '变化', desc: 'WiFi↔4G，IP地址变化', testStrategy: '测：连接迁移(HTTP/3), 会话保持, 下载续传, WebSocket重连, 登录态保持', detail: '从WiFi切到4G：IP地址变化→TCP连接断开→需重建。验证：下载是否续传(断点续传)、视频播放位置是否保持、登录态是否丢失、支付中途切网是否安全。' },
]

const weakQuiz = reactive({ options: ['A. 检查服务端是否有超时处理', 'B. 检查前端是否有超时提示+重试按钮+降级UI', 'C. 升级服务器配置', 'D. 让用户换个网络'], answer: 1, chosen: -1, submitted: false, explain: '3G/弱网环境不能假设用户网络好。QA应优先验证：①前端是否有合理的超时时间(非无限等待) ②超时后是否有友好提示和重试按钮 ③是否有降级UI(骨架屏/文字替代大图)。服务端超时是开发的事,C是运维的事,D不是解决方案。' })
function checkWeakQuiz() { weakQuiz.submitted = true }
</script>

<style scoped>
.lab-page { max-width: 860px; margin: 0 auto; }

.proto-tabs { display: flex; gap: 4px; margin-bottom: var(--space-lg); background: var(--surface); border-radius: var(--radius); padding: 4px; border: 1px solid var(--border); }
.proto-tab { flex: 1; padding: 10px 8px; border: none; background: none; border-radius: 8px; cursor: pointer; font-size: .82rem; color: var(--text-secondary); font-weight: 500; transition: all var(--fast); font-family: var(--font-sans); }
.proto-tab.active { background: var(--primary); color: #fff; font-weight: 600; }
.proto-content h3 { font-size: 1rem; margin-bottom: 14px; }

/* TCP Handshake */
.handshake-viz { display: flex; flex-direction: column; gap: 8px; align-items: center; margin: 16px 0; }
.hs-party { padding: 8px 20px; border-radius: var(--radius); font-weight: 600; font-size: .84rem; display: flex; gap: 10px; align-items: center; }
.hs-party.client { background: var(--primary-light); color: var(--primary); }
.hs-party.server { background: var(--success-light); color: var(--success); }
.hs-label { font-size: .7rem; font-family: var(--font-mono); opacity: .7; }
.hs-arrows { display: flex; flex-direction: column; gap: 4px; padding: 8px 0; }
.hs-step { padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: all var(--fast); text-align: center; opacity: .35; }
.hs-step:hover { background: var(--surface-hover); opacity: .7; }
.hs-step.active { opacity: 1; background: var(--primary-light); }
.hs-arrow { font-family: var(--font-mono); font-weight: 700; display: block; }
.hs-desc { font-size: .72rem; color: var(--text-secondary); font-family: var(--font-mono); }
.hs-status { text-align: center; font-size: .8rem; color: var(--text-secondary); margin-top: 8px; }

/* HTTP */
.http-compare { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }
.http-card { border: 2px solid var(--border); border-radius: var(--radius); padding: 16px; cursor: pointer; transition: all var(--fast); }
.http-card:hover { border-color: var(--primary); }
.http-card.highlight { border-color: var(--primary); background: var(--primary-light); }
.http-card h4 { font-size: .92rem; margin-bottom: 8px; }
.http-card ul { list-style: none; font-size: .78rem; color: var(--text-secondary); line-height: 1.7; }
.http-detail { margin-top: 12px; padding: 12px; background: var(--primary-light); border-radius: var(--radius); font-size: .82rem; line-height: 1.6; }

.status-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 6px; }
.status-item { display: flex; gap: 10px; align-items: baseline; padding: 4px 0; font-size: .8rem; }
.status-code { font-family: var(--font-mono); font-weight: 700; font-size: .82rem; min-width: 36px; }
.status-code.ok { color: var(--success); } .status-code.redirect { color: var(--primary); } .status-code.client { color: var(--warning); } .status-code.server { color: var(--danger); }

/* TLS */
.tls-flow { display: flex; flex-direction: column; gap: 0; }
.tls-step { display: flex; gap: 14px; padding: 12px 16px; cursor: pointer; transition: all var(--fast); border-left: 3px solid var(--border); opacity: .45; align-items: flex-start; }
.tls-step:hover { background: var(--surface-hover); opacity: .8; }
.tls-step.done { border-left-color: var(--success); opacity: 1; }
.tls-num { width: 26px; height: 26px; border-radius: 50%; background: var(--border-light); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .78rem; flex-shrink: 0; }
.tls-step.done .tls-num { background: var(--success); color: #fff; }
.tls-step strong { font-size: .84rem; display: block; }
.tls-step p { font-size: .78rem; color: var(--text-secondary); margin: 2px 0 0; }

/* DNS */
.dns-flow { display: flex; flex-direction: column; gap: 4px; align-items: center; }
.dns-party { font-size: .84rem; font-weight: 600; }
.dns-arrow { font-family: var(--font-mono); font-size: .78rem; color: var(--primary); }
.dns-resolver { display: flex; flex-direction: column; gap: 4px; width: 100%; }
.dns-step-card { display: flex; justify-content: space-between; padding: 6px 12px; background: var(--bg); border-radius: 6px; font-size: .78rem; }
.dns-time { font-family: var(--font-mono); color: var(--text-muted); font-size: .72rem; }
.dns-records { display: flex; flex-direction: column; gap: 6px; }
.dns-record { display: flex; gap: 12px; align-items: baseline; font-size: .8rem; padding: 6px 0; border-bottom: 1px solid var(--border-light); }
.dns-record code { background: var(--primary-light); color: var(--primary); padding: 2px 8px; border-radius: 4px; font-size: .74rem; min-width: 52px; text-align: center; }
.dns-example { font-family: var(--font-mono); font-size: .72rem; color: var(--text-muted); margin-left: auto; }

/* WebSocket */
.ws-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.ws-col { border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; }
.ws-col.highlight-col { border-color: var(--primary); background: var(--primary-light); }
.ws-col h4 { font-size: .88rem; margin-bottom: 8px; }
.ws-col ul { list-style: none; font-size: .78rem; color: var(--text-secondary); line-height: 1.8; }

/* Quiz shared */
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

.checklist { list-style: none; font-size: .84rem; line-height: 2; }

/* Capture */
.task-desc { font-size: .82rem; color: var(--text-secondary); margin-bottom: 12px; }
.capture-bar { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.scenario-btn { padding: 6px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border); background: var(--surface); cursor: pointer; font-size: .78rem; font-weight: 500; transition: all var(--fast); font-family: var(--font-sans); }
.scenario-btn:hover { border-color: var(--primary); }
.scenario-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }
.raw-http { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
@media (max-width: 600px) { .raw-http { grid-template-columns: 1fr; } }
.raw-section { background: #1a1a2e; border-radius: var(--radius); overflow: hidden; }
.raw-label { padding: 6px 14px; background: #16162a; font-size: .72rem; color: #a0a0b8; font-weight: 600; font-family: var(--font-mono); }
.raw-text { padding: 12px 16px; margin: 0; font-family: var(--font-mono); font-size: .72rem; line-height: 1.6; color: #e5e7eb; white-space: pre-wrap; word-break: break-all; overflow-x: auto; max-height: 280px; overflow-y: auto; }
.capture-question { font-size: .9rem; font-weight: 600; margin-bottom: 10px; line-height: 1.5; }
.capture-answers { margin-bottom: 6px; }

/* Weak network */
.weaknet-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; margin-bottom: 12px; }
.weaknet-card { border: 2px solid var(--border); border-radius: var(--radius); padding: 14px; cursor: pointer; transition: all var(--fast); }
.weaknet-card:hover { border-color: var(--primary); transform: translateY(-1px); }
.weaknet-card h4 { font-size: .84rem; margin-bottom: 6px; }
.wn-specs { display: flex; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }
.wn-specs span { font-size: .68rem; font-family: var(--font-mono); background: var(--border-light); padding: 2px 8px; border-radius: 4px; }
.weaknet-card p { font-size: .75rem; color: var(--text-secondary); line-height: 1.5; }
.wn-test { margin-top: 6px; font-size: .7rem; color: var(--primary); font-weight: 500; background: var(--primary-light); padding: 4px 8px; border-radius: 4px; }
</style>
