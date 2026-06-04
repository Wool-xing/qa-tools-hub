<template>
  <div class="lab-page">
    <div class="tab-bar">
      <button v-for="(t, i) in tabs" :key="i" class="tab-btn" :class="{ active: activeTab === i }" @click="activeTab = i">{{ t }}</button>
    </div>

    <!-- ═══════════════════ TAB 1: Faker Playground ═══════════════════ -->
    <div v-if="activeTab === 0" class="tab-content">
      <div class="card">
        <h3 class="card-title">🎲 Faker 数据工厂</h3>
        <p class="hint-text">配置字段模板，一键生成逼真测试数据。不需要写 Faker 代码。</p>

        <div class="form-row">
          <div class="form-group" style="flex:1;">
            <label class="field-label">模板预设</label>
            <select v-model="fakerPreset" class="field-select" @change="applyFakerPreset">
              <option value="user">👤 生成用户数据</option>
              <option value="order">🛒 生成订单数据</option>
              <option value="address">📍 生成地址数据</option>
              <option value="custom">✏️ 自由组合</option>
            </select>
          </div>
          <div class="form-group" style="flex:0 0 140px;">
            <label class="field-label">记录数</label>
            <input v-model.number="fakerCount" type="number" min="1" max="100" class="form-input">
          </div>
        </div>

        <div style="margin-top:12px;">
          <label class="field-label">字段配置 (勾选需要的字段)</label>
          <div class="checkbox-grid">
            <label v-for="f in fakerFields" :key="f.key" class="checkbox-item" :class="{ checked: f.enabled }">
              <input type="checkbox" v-model="f.enabled" :disabled="f.locked">
              <span>{{ f.icon }} {{ f.label }}</span>
            </label>
          </div>
        </div>

        <div class="toolbar">
          <span class="hint-text">{{ enabledFakerCount }} 个字段 · {{ fakerCount }} 条记录</span>
          <button class="btn-primary" :disabled="enabledFakerCount === 0" @click="generateFaker">🎲 生成数据</button>
        </div>
      </div>

      <div v-if="fakerOutput.length" class="card" style="overflow:hidden;padding:0;">
        <div style="padding:12px 20px;font-size:.78rem;color:var(--text-secondary);border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">
          <span>生成 <strong>{{ fakerOutput.length }}</strong> 条记录 · {{ getFakerColumns.length }} 列</span>
          <div style="display:flex;gap:8px;">
            <button class="btn-ghost btn-xs" @click="fakerViewMode = fakerViewMode === 'table' ? 'json' : 'table'">
              {{ fakerViewMode === 'table' ? '📋 JSON' : '📊 表格' }}
            </button>
            <button class="btn-ghost btn-xs" @click="copyFakerOutput">📋 复制</button>
          </div>
        </div>
        <div v-if="fakerViewMode === 'table'" style="overflow-x:auto;">
          <table class="result-table">
            <thead><tr><th v-for="c in getFakerColumns" :key="c">{{ c }}</th></tr></thead>
            <tbody><tr v-for="(r, i) in fakerOutput" :key="i"><td v-for="c in getFakerColumns" :key="c">{{ r[c] }}</td></tr></tbody>
          </table>
        </div>
        <pre v-else class="json-output">{{ JSON.stringify(fakerOutput, null, 2) }}</pre>
      </div>

      <div class="education-box">
        <strong>📚 你知道吗？</strong> 真实项目中，测试数据通常需要满足: ① 数据多样性 (不同字符集/长度/格式) ② 边界覆盖 (空值/极值) ③ 关联一致性 (订单金额=商品单价×数量)。Faker 库只解决第①点，第②③点需要你自己设计。
      </div>
    </div>

    <!-- ═══════════════════ TAB 2: Pairwise Generator ═══════════════════ -->
    <div v-if="activeTab === 1" class="tab-content">
      <div class="card">
        <h3 class="card-title">🔀 Pairwise (All-Pairs) 组合生成器</h3>
        <p class="hint-text">全组合爆炸时用 Pairwise——绝大多数 bug 由单个参数或参数对触发，极少由 3 个参数同时触发。</p>

        <div class="pair-params">
          <div v-for="(p, i) in pairwiseParams" :key="i" class="pair-param-row">
            <input v-model="p.name" placeholder="参数名" class="param-name-input">
            <input v-model="p.valuesStr" placeholder="值1, 值2, 值3" class="param-values-input">
            <span class="param-count">{{ p.valuesStr ? p.valuesStr.split(',').filter(v => v.trim()).length : 0 }} 个值</span>
            <button class="btn-ghost btn-xs" @click="pairwiseParams.splice(i, 1)" :disabled="pairwiseParams.length <= 2">✕</button>
          </div>
        </div>
        <button class="btn-outline btn-sm" style="margin-top:8px;" @click="pairwiseParams.push({ name: '', valuesStr: '' })">+ 添加参数</button>
        <button class="btn-ghost btn-sm" style="margin-left:8px;" @click="loadPairwisePreset">📋 加载示例 (浏览器/OS/分辨率/语言)</button>

        <div class="toolbar" style="margin-top:12px;">
          <span class="hint-text">{{ pairwiseParams.filter(p => p.name && p.valuesStr).length }} 个参数定义完成</span>
          <button class="btn-primary" :disabled="pairwiseParams.filter(p => p.name && p.valuesStr).length < 2" @click="generatePairwise">🔀 生成组合</button>
        </div>
      </div>

      <div v-if="pairwiseResult" class="card">
        <div class="pairwise-stats">
          <div class="stat-card">
            <div class="stat-number">{{ pairwiseFullCount }}</div>
            <div class="stat-label">全组合</div>
            <div class="stat-formula">{{ pairwiseFormula }}</div>
          </div>
          <div class="stat-arrow">→</div>
          <div class="stat-card stat-card-green">
            <div class="stat-number">{{ pairwiseResult.length }}</div>
            <div class="stat-label">Pairwise 组合</div>
            <div class="stat-formula">减少 {{ pairwiseReduction }}%</div>
          </div>
        </div>

        <h4 style="font-size:.84rem;margin-bottom:8px;">生成的测试用例 ({{ pairwiseResult.length }} 条)</h4>
        <div style="overflow-x:auto;">
          <table class="result-table">
            <thead><tr><th v-for="c in pairwiseHeaders" :key="c">{{ c }}</th></tr></thead>
            <tbody><tr v-for="(r, i) in pairwiseResult" :key="i"><td v-for="h in pairwiseHeaders" :key="h">{{ r[h] }}</td></tr></tbody>
          </table>
        </div>
      </div>

      <div class="education-box">
        <strong>📚 Pairwise 原理:</strong> 假设有 4 个参数各 3 个值，全组合 = 3^4 = 81。Pairwise 只需 9 个测试用例就能覆盖所有「参数对」组合。研究表明 70%+ 的缺陷由单参数或参数对触发 (Kuhn & Reilly, 2002)。工具: PICT (Microsoft), AllPairs (Python)。
      </div>
    </div>

    <!-- ═══════════════════ TAB 3: Data Masking ═══════════════════ -->
    <div v-if="activeTab === 2" class="tab-content">
      <div class="card">
        <h3 class="card-title">🎭 数据脱敏 (Data Masking)</h3>
        <p class="hint-text">生产数据不能直接用于测试——粘贴 CSV/JSON 数据，选择脱敏规则，一键处理。</p>

        <div class="form-group">
          <label class="field-label">输入数据 (CSV 或 JSON 格式)</label>
          <textarea v-model="maskInput" rows="6" class="sql-input" placeholder="name,email,phone,id_card&#10;张三,zhangsan@abc.com,13812345678,310101199001011234&#10;李四,lisi@def.com,13987654321,110102198502022345"></textarea>
        </div>
        <button class="btn-ghost btn-sm" style="margin-bottom:10px;" @click="loadMaskSample">📋 加载示例数据 (5行含PII)</button>

        <label class="field-label">脱敏规则</label>
        <div class="checkbox-grid">
          <label v-for="r in maskRules" :key="r.key" class="checkbox-item" :class="{ checked: r.enabled }">
            <input type="checkbox" v-model="r.enabled">
            <span>{{ r.icon }} {{ r.label }} <code class="rule-code">{{ r.pattern }}</code></span>
          </label>
        </div>

        <div class="toolbar" style="margin-top:10px;">
          <span class="hint-text">{{ enabledMaskCount }} 条规则启用</span>
          <button class="btn-primary" :disabled="!maskInput.trim() || enabledMaskCount === 0" @click="executeMask">🎭 执行脱敏</button>
        </div>
      </div>

      <div v-if="maskResult.length" class="card" style="overflow:hidden;padding:0;">
        <div style="padding:12px 20px;font-size:.78rem;color:var(--text-secondary);border-bottom:1px solid var(--border);">
          脱敏完成 · {{ maskResult.length }} 行
        </div>
        <div style="overflow-x:auto;">
          <table class="result-table">
            <thead><tr><th>#</th><th v-for="c in maskColumns" :key="c">{{ c }} (原始)</th><th v-for="c in maskColumns" :key="'m'+c">{{ c }} (脱敏后)</th></tr></thead>
            <tbody>
              <tr v-for="(r, i) in maskResult" :key="i">
                <td>{{ i + 1 }}</td>
                <td v-for="c in maskColumns" :key="'o'+c" style="color:var(--danger);">{{ r.original[c] }}</td>
                <td v-for="c in maskColumns" :key="'m'+c" style="color:var(--success);">{{ r.masked[c] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="education-box">
        <strong>📚 脱敏 vs 合成数据:</strong> 脱敏保留数据结构/分布特征，适合性能测试和回归测试。合成数据 (Faker) 更适合新功能测试和边界探索——可以构造生产中没有的极端场景。生产数据脱敏后仍需审计：警惕间接标识符组合重识别 (如生日+邮编+性别可唯一标识 87% 美国人口)。
      </div>
    </div>

    <!-- ═══════════════════ TAB 4: Edge-Case Generator ═══════════════════ -->
    <div v-if="activeTab === 3" class="tab-content">
      <div class="card">
        <h3 class="card-title">⚡ 边界值 & 边缘用例生成器</h3>
        <p class="hint-text">选择数据类型，查看预计算的边界用例清单。勾选你认为需要测试的项，与答案比对。</p>

        <div class="form-row">
          <div class="form-group" style="flex:1;">
            <label class="field-label">数据类型</label>
            <select v-model="edgeDataType" class="field-select" @change="resetEdgeCheck">
              <option v-for="et in edgeTypes" :key="et.key" :value="et.key">{{ et.icon }} {{ et.label }}</option>
            </select>
          </div>
        </div>

        <div v-if="currentEdgeType" class="edge-checklist">
          <div class="edge-info-row">
            <span class="hint-text">📋 共 {{ currentEdgeType.cases.length }} 条边界用例 — 勾选你认为应该测试的</span>
            <button class="btn-primary btn-sm" @click="checkEdgeAnswers">✅ 提交比对</button>
          </div>
          <div v-for="(ec, i) in currentEdgeType.cases" :key="i" class="edge-item" :class="edgeReveal ? (ec.shouldTest ? 'edge-should' : 'edge-skip') : ''">
            <label class="edge-check-label">
              <input type="checkbox" v-model="edgeChecks[i]" :disabled="edgeReveal">
              <span class="edge-desc">{{ ec.description }}</span>
              <code class="edge-example">{{ ec.example }}</code>
            </label>
            <span v-if="edgeReveal" class="edge-answer-tag" :class="ec.shouldTest ? 'tag-should' : 'tag-skip'">
              {{ ec.shouldTest ? '✅ 应测' : '⏭ 可跳过' }}
            </span>
            <span v-if="edgeReveal && ec.note" class="edge-note">{{ ec.note }}</span>
          </div>
        </div>

        <div v-if="edgeReveal" class="card result-card" :class="edgeScore >= 60 ? 'result-pass' : 'result-fail'">
          <h3>📊 边界判断结果</h3>
          <div class="score-big">{{ edgeScore }}<span class="score-unit">分</span></div>
          <div class="result-detail">
            <div class="rd-row"><span>✅ 正确勾选 (应测且你勾了)</span><span>{{ edgeCorrectHits }}</span></div>
            <div class="rd-row"><span>⚠️ 遗漏 (应测但你没勾)</span><span>{{ edgeMissed }}</span></div>
            <div class="rd-row"><span>❌ 过度测试 (不应测但你勾了)</span><span>{{ edgeOverTest }}</span></div>
            <div class="rd-row"><span>⏭ 正确跳过 (不应测且你没勾)</span><span>{{ edgeCorrectSkip }}</span></div>
          </div>
          <button class="btn-ghost btn-sm" style="margin-top:10px;" @click="resetEdgeCheck">🔄 重新挑战</button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════ TAB 5: SQL Data Factory ═══════════════════ -->
    <div v-if="activeTab === 4" class="tab-content">
      <div class="card">
        <h3 class="card-title">🗄️ SQL INSERT 语句工厂</h3>
        <p class="hint-text">选择表模板，配置列值生成策略，一键生成批量 INSERT 语句。</p>

        <div class="form-row">
          <div class="form-group" style="flex:1;">
            <label class="field-label">表模板</label>
            <select v-model="sqlTable" class="field-select" @change="applySqlTable">
              <option value="users">👤 users — 用户表</option>
              <option value="orders">🛒 orders — 订单表</option>
              <option value="products">📦 products — 产品表</option>
            </select>
          </div>
          <div class="form-group" style="flex:0 0 120px;">
            <label class="field-label">生成行数</label>
            <input v-model.number="sqlRowCount" type="number" min="1" max="50" class="form-input">
          </div>
        </div>

        <div style="margin-top:12px;">
          <label class="field-label">列值配置</label>
          <div class="sql-cols">
            <div v-for="(col, i) in sqlColumns" :key="i" class="sql-col-row">
              <span class="sql-col-name">{{ col.name }}</span>
              <span class="sql-col-type">{{ col.type }}</span>
              <select v-model="col.strategy" class="field-select" style="flex:1;padding:4px 8px;font-size:.76rem;">
                <option v-for="s in col.strategies" :key="s" :value="s">{{ s }}</option>
              </select>
              <input v-if="col.strategy === '静态值'" v-model="col.staticVal" placeholder="值" class="param-name-input" style="width:100px;">
              <input v-if="col.strategy === '数字范围'" v-model.number="col.rangeMin" placeholder="最小" class="param-name-input" style="width:60px;" type="number">
              <input v-if="col.strategy === '数字范围'" v-model.number="col.rangeMax" placeholder="最大" class="param-name-input" style="width:60px;" type="number">
            </div>
          </div>
        </div>

        <div class="toolbar" style="margin-top:10px;">
          <span class="hint-text">{{ sqlColumns.length }} 列 · {{ sqlRowCount }} 行</span>
          <button class="btn-primary" @click="generateSQL">🗄️ 生成 SQL</button>
        </div>
      </div>

      <div v-if="sqlOutput" class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <h3 style="font-size:.84rem;">📋 生成的 INSERT 语句</h3>
          <button class="btn-ghost btn-xs" @click="copySqlOutput">📋 复制</button>
        </div>
        <pre class="sql-output">{{ sqlOutput }}</pre>
      </div>

      <div class="education-box">
        <strong>📚 测试数据工厂最佳实践:</strong> ① 每次测试前重置数据库到已知状态 (seed) ② 使用事务回滚隔离测试 ③ 数据工厂函数应支持覆盖默认值 (trait/overrides) ④ 工厂数据应包含「反例」——故意构造不符合业务规则的数据来测校验逻辑。
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const tabs = ['🎲 Faker工厂', '🔀 Pairwise', '🎭 数据脱敏', '⚡ 边界值', '🗄️ SQL工厂']
const activeTab = ref(0)

// ═══════════════════════════════════════════
// TAB 1: Faker Playground
// ═══════════════════════════════════════════
const fakerPreset = ref('user')
const fakerCount = ref(10)
const fakerViewMode = ref('table')
const fakerOutput = ref([])

const fakerFieldDefs = {
  user: [
    { key: 'name', icon: '👤', label: '姓名', enabled: true, locked: false },
    { key: 'email', icon: '📧', label: '邮箱', enabled: true, locked: false },
    { key: 'phone', icon: '📱', label: '手机号', enabled: true, locked: false },
    { key: 'id_card', icon: '🪪', label: '身份证号', enabled: false, locked: false },
    { key: 'age', icon: '🎂', label: '年龄', enabled: true, locked: false },
    { key: 'gender', icon: '⚧', label: '性别', enabled: false, locked: false },
    { key: 'birthday', icon: '📅', label: '生日', enabled: false, locked: false },
    { key: 'address', icon: '📍', label: '地址', enabled: false, locked: false },
    { key: 'company', icon: '🏢', label: '公司', enabled: false, locked: false },
    { key: 'username', icon: '🔑', label: '用户名', enabled: true, locked: false },
  ],
  order: [
    { key: 'order_id', icon: '🔢', label: '订单号', enabled: true, locked: true },
    { key: 'user_id', icon: '👤', label: '用户ID', enabled: true, locked: true },
    { key: 'product_name', icon: '📦', label: '商品名', enabled: true, locked: false },
    { key: 'quantity', icon: '🔢', label: '数量', enabled: true, locked: false },
    { key: 'unit_price', icon: '💰', label: '单价', enabled: true, locked: false },
    { key: 'total', icon: '💵', label: '总价', enabled: true, locked: true },
    { key: 'status', icon: '📊', label: '状态', enabled: true, locked: false },
    { key: 'created_at', icon: '📅', label: '创建时间', enabled: false, locked: false },
    { key: 'payment_method', icon: '💳', label: '支付方式', enabled: false, locked: false },
    { key: 'shipping_address', icon: '📍', label: '收货地址', enabled: false, locked: false },
  ],
  address: [
    { key: 'province', icon: '🗺️', label: '省', enabled: true, locked: true },
    { key: 'city', icon: '🏙️', label: '市', enabled: true, locked: true },
    { key: 'district', icon: '🏘️', label: '区', enabled: true, locked: false },
    { key: 'street', icon: '🛣️', label: '街道', enabled: true, locked: false },
    { key: 'postal_code', icon: '📮', label: '邮编', enabled: false, locked: false },
    { key: 'recipient', icon: '👤', label: '收件人', enabled: true, locked: false },
    { key: 'phone', icon: '📱', label: '电话', enabled: true, locked: false },
    { key: 'is_default', icon: '⭐', label: '默认地址', enabled: false, locked: false },
  ],
  custom: [
    { key: 'field1', icon: '📌', label: '字段1', enabled: true, locked: false },
    { key: 'field2', icon: '📌', label: '字段2', enabled: false, locked: false },
    { key: 'field3', icon: '📌', label: '字段3', enabled: false, locked: false },
    { key: 'field4', icon: '📌', label: '字段4', enabled: false, locked: false },
  ],
}

const fakerFields = ref(JSON.parse(JSON.stringify(fakerFieldDefs.user)))
const enabledFakerCount = computed(() => fakerFields.value.filter(f => f.enabled).length)

function applyFakerPreset() {
  fakerFields.value = JSON.parse(JSON.stringify(fakerFieldDefs[fakerPreset.value] || fakerFieldDefs.custom))
  fakerOutput.value = []
}

const surnames = ['张', '李', '王', '赵', '陈', '刘', '黄', '周', '吴', '郑', '孙', '朱', '马', '胡', '林', '何', '高', '罗', '郭', '杨']
const givenNames = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '涛', '明', '秀英', '华', '慧', '鑫', '桂英']
const companies = ['阿里巴巴', '腾讯科技', '百度在线', '字节跳动', '华为技术', '小米科技', '京东集团', '美团点评', '滴滴出行', '网易网络']
const products = ['iPhone 15 Pro', 'MacBook Air M3', 'AirPods Pro', 'iPad Mini', 'Apple Watch', 'Sony WH-1000XM5', 'Dell XPS 15', 'Logitech MX Master 3S', 'Samsung Galaxy S24', 'Google Pixel 8']
const statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled', 'refunded']
const payMethods = ['credit_card', 'debit_card', 'wechat_pay', 'alipay', 'bank_transfer']
const provinces = ['北京市', '上海市', '广东省', '浙江省', '江苏省', '四川省', '湖北省', '湖南省', '福建省', '山东省']
const cities = { '北京市': ['朝阳区', '海淀区', '西城区'], '上海市': ['浦东新区', '徐汇区', '静安区'], '广东省': ['广州市', '深圳市', '东莞市'], '浙江省': ['杭州市', '宁波市', '温州市'], '江苏省': ['南京市', '苏州市', '无锡市'], '四川省': ['成都市', '绵阳市', '德阳市'] }

function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min }
function pick(arr) { return arr[Math.floor(Math.random() * arr.length)] }
function genPhone() { const prefixes = ['138', '139', '150', '151', '158', '159', '186', '187', '188']; return pick(prefixes) + String(rand(10000000, 99999999)) }
function genIdCard() { return String(rand(110101, 530102)) + String(rand(1980, 2005)) + String(rand(1, 12)).padStart(2, '0') + String(rand(1, 28)).padStart(2, '0') + String(rand(1000, 9999)) }
function genDate(daysBack) { const d = new Date(); d.setDate(d.getDate() - rand(0, daysBack)); return d.toISOString().split('T')[0] }
function genOrderId() { return 'ORD-' + Date.now().toString(36).toUpperCase() + '-' + String(rand(1000, 9999)) }

const fakerGenerators = {
  name: () => pick(surnames) + pick(givenNames),
  email: () => 'user' + rand(100, 9999) + '@' + pick(['qq.com', '163.com', 'gmail.com', 'outlook.com', 'example.cn']),
  phone: genPhone,
  id_card: genIdCard,
  age: () => rand(18, 65),
  gender: () => pick(['男', '女']),
  birthday: () => genDate(365 * 40),
  address: () => pick(provinces) + pick(cities[pick(provinces)] || ['—']) + pick(['中山路', '人民路', '解放路', '建设路']) + rand(1, 500) + '号',
  company: () => pick(companies),
  username: () => 'user_' + pick(['alpha', 'beta', 'gamma', 'delta', 'echo', 'fox', 'ghost', 'hawk']) + rand(10, 99),
  product_name: () => pick(products),
  quantity: () => rand(1, 10),
  unit_price: () => parseFloat((Math.random() * 9900 + 99).toFixed(2)),
  total: () => 0,
  status: () => pick(statuses),
  created_at: () => genDate(90),
  payment_method: () => pick(payMethods),
  shipping_address: () => pick(provinces) + pick(cities[pick(provinces)] || ['—']) + pick(['中山路', '人民路']) + rand(1, 300) + '号',
  province: () => pick(provinces),
  city: () => pick(cities[pick(provinces)] || ['—']),
  district: () => pick(['东城区', '西城区', '南山区', '福田区', '天河区', '浦东新区', '朝阳区', '海淀区']),
  street: () => pick(['中山路', '人民路', '解放路', '建设路', '南京路']) + rand(1, 500) + '号',
  postal_code: () => String(rand(100000, 999999)),
  recipient: () => pick(surnames) + pick(givenNames),
  is_default: () => Math.random() > 0.7,
  user_id: () => rand(1, 9999),
  order_id: genOrderId,
  field1: () => 'value_' + rand(1, 999),
  field2: () => rand(1, 100),
  field3: () => pick(['A', 'B', 'C']),
  field4: () => genDate(30),
}

function generateFaker() {
  const enabled = fakerFields.value.filter(f => f.enabled)
  const result = []
  for (let i = 0; i < fakerCount.value; i++) {
    const row = {}
    for (const f of enabled) {
      const gen = fakerGenerators[f.key]
      if (gen) row[f.key] = gen()
      else row[f.key] = ''
    }
    // Post-process: total = quantity * unit_price
    if (row.quantity && row.unit_price) row.total = parseFloat((row.quantity * row.unit_price).toFixed(2))
    result.push(row)
  }
  fakerOutput.value = result
}

const getFakerColumns = computed(() => {
  if (!fakerOutput.value.length) return []
  return Object.keys(fakerOutput.value[0])
})

function copyFakerOutput() {
  const text = fakerViewMode.value === 'json' ? JSON.stringify(fakerOutput.value, null, 2) : [getFakerColumns.value.join(',')].concat(fakerOutput.value.map(r => getFakerColumns.value.map(c => r[c]).join(','))).join('\n')
  navigator.clipboard.writeText(text).catch(() => {})
}

// ═══════════════════════════════════════════
// TAB 2: Pairwise Generator
// ═══════════════════════════════════════════
const pairwiseParams = ref([
  { name: '浏览器', valuesStr: 'Chrome, Firefox, Safari' },
  { name: '操作系统', valuesStr: 'Windows, macOS, Linux' },
])
const pairwiseResult = ref(null)

const pairwiseFullCount = computed(() => {
  const valid = pairwiseParams.value.filter(p => p.name && p.valuesStr)
  return valid.reduce((acc, p) => acc * p.valuesStr.split(',').filter(v => v.trim()).length, 1)
})
const pairwiseFormula = computed(() => {
  const valid = pairwiseParams.value.filter(p => p.name && p.valuesStr)
  return valid.map(p => p.valuesStr.split(',').filter(v => v.trim()).length).join('×')
})
const pairwiseHeaders = computed(() => {
  return pairwiseParams.value.filter(p => p.name && p.valuesStr).map(p => p.name)
})
const pairwiseReduction = computed(() => {
  if (!pairwiseResult.value || pairwiseFullCount.value === 0) return 0
  return Math.round((1 - pairwiseResult.value.length / pairwiseFullCount.value) * 100)
})

function loadPairwisePreset() {
  pairwiseParams.value = [
    { name: '浏览器', valuesStr: 'Chrome, Firefox, Safari' },
    { name: '操作系统', valuesStr: 'Windows, macOS, Linux' },
    { name: '屏幕分辨率', valuesStr: '1920×1080, 2560×1440, 3840×2160' },
    { name: '语言', valuesStr: '中文, English, 日本語' },
  ]
  pairwiseResult.value = null
}

function allPairs(params) {
  // IPOG-like strategy: start with first 2 params all-pairs, then extend
  if (params.length < 2) return params.length === 1 ? params[0].values.map(v => ({ [params[0].name]: v })) : []
  const parseValues = p => p.valuesStr.split(',').map(v => v.trim()).filter(v => v)
  const parsed = params.map(p => ({ name: p.name, values: parseValues(p) }))

  // Start with full combination of first 2 parameters
  let result = []
  for (const v0 of parsed[0].values) {
    for (const v1 of parsed[1].values) {
      result.push({ [parsed[0].name]: v0, [parsed[1].name]: v1 })
    }
  }

  // Extend for each additional parameter
  for (let pi = 2; pi < parsed.length; pi++) {
    const p = parsed[pi]
    const newResult = []
    // Each existing row gets paired with each value of the new parameter, but we minimize
    // Simple greedy: assign each value at least once, then fill remaining rows
    const vals = [...p.values]
    const used = new Set()
    for (let ri = 0; ri < result.length; ri++) {
      const row = result[ri]
      // Find an uncovered pair for each existing param with the new param
      let bestVal = vals[ri % vals.length]
      for (const v of vals) {
        let allCovered = true
        for (const prevKey of Object.keys(row)) {
          const pairKey = prevKey + '|' + row[prevKey] + '|' + p.name + '|' + v
          if (!used.has(pairKey)) { allCovered = false; break }
        }
        if (!allCovered) { bestVal = v; break }
      }
      // Mark pairs as covered
      for (const prevKey of Object.keys(row)) {
        used.add(prevKey + '|' + row[prevKey] + '|' + p.name + '|' + bestVal)
      }
      newResult.push({ ...row, [p.name]: bestVal })
    }
    result = newResult
  }
  return result
}

function generatePairwise() {
  const valid = pairwiseParams.value.filter(p => p.name && p.valuesStr && p.valuesStr.split(',').filter(v => v.trim()).length >= 1)
  if (valid.length < 2) { pairwiseResult.value = []; return }
  pairwiseResult.value = allPairs(valid)
}

// ═══════════════════════════════════════════
// TAB 3: Data Masking
// ═══════════════════════════════════════════
const maskInput = ref('')
const maskResult = ref([])
const maskColumns = ref([])
const enabledMaskCount = computed(() => maskRules.value.filter(r => r.enabled).length)

const maskRules = ref([
  { key: 'email', icon: '📧', label: '邮箱 →', pattern: 'u***@domain.com', enabled: true },
  { key: 'phone', icon: '📱', label: '手机号 →', pattern: '138****1234', enabled: true },
  { key: 'name', icon: '👤', label: '姓名 →', pattern: '张**', enabled: true },
  { key: 'id_card', icon: '🪪', label: '身份证 →', pattern: '310***********1234', enabled: true },
  { key: 'ip', icon: '🌐', label: 'IP 地址 →', pattern: '192.168.*.*', enabled: false },
  { key: 'bank_card', icon: '💳', label: '银行卡 →', pattern: '6222****1234', enabled: false },
])

const maskSampleCSV = `name,email,phone,id_card,ip_address
张三,zhangsan@abc-company.com,13812345678,310101199001011234,202.96.209.5
李四,lisi@def-tech.cn,13987654321,110102198502022345,58.247.22.136
王五,wangwu@gmail.com,15012349876,440106199512153456,183.195.12.88
赵六,zhaoliu@outlook.com,18698761234,510107198807203456,120.204.17.45
陈七,chenqi@example.org,15855556666,320506200010123456,61.170.81.200`

function loadMaskSample() {
  maskInput.value = maskSampleCSV
  maskResult.value = []
}

function maskValue(val, ruleKey) {
  if (!val) return val
  switch (ruleKey) {
    case 'email': {
      const at = val.indexOf('@')
      if (at === -1) return val
      return val[0] + '***@' + val.slice(at + 1)
    }
    case 'phone': {
      const digits = val.replace(/\D/g, '')
      if (digits.length < 7) return val
      return digits.slice(0, 3) + '****' + digits.slice(-4)
    }
    case 'name': {
      if (val.length <= 1) return val
      return val[0] + '*'.repeat(val.length - 1)
    }
    case 'id_card': {
      const cleaned = val.replace(/\s/g, '')
      if (cleaned.length < 8) return val
      return cleaned.slice(0, 3) + '*'.repeat(cleaned.length - 7) + cleaned.slice(-4)
    }
    case 'ip': {
      const parts = val.split('.')
      if (parts.length !== 4) return val
      return parts[0] + '.' + parts[1] + '.*.*'
    }
    case 'bank_card': {
      const digits = val.replace(/\D/g, '')
      if (digits.length < 8) return val
      return digits.slice(0, 4) + '****' + digits.slice(-4)
    }
    default: return val
  }
}

function executeMask() {
  const text = maskInput.value.trim()
  if (!text) return

  // Try CSV first
  const lines = text.split('\n').filter(l => l.trim())
  if (lines.length === 0) return

  // Check if it looks like CSV (has commas) or JSON
  if (text.startsWith('[') || text.startsWith('{')) {
    // JSON
    try {
      let data = JSON.parse(text)
      if (!Array.isArray(data)) data = [data]
      const cols = Object.keys(data[0] || {})
      maskColumns.value = cols
      const enabledRules = maskRules.value.filter(r => r.enabled)
      maskResult.value = data.map(row => {
        const masked = { ...row }
        for (const col of cols) {
          const val = String(row[col] || '')
          for (const rule of enabledRules) {
            if (col.toLowerCase().includes(rule.key) || val.match(getRuleRegex(rule.key))) {
              masked[col] = maskValue(val, rule.key)
              break
            }
          }
        }
        return { original: row, masked }
      })
    } catch { maskByCSV(lines) }
  } else {
    maskByCSV(lines)
  }
}

function getRuleRegex(key) {
  const map = { email: /@/, phone: /^1[3-9]\d{9}$/, id_card: /^\d{17}[\dXx]$/, ip: /^\d+\.\d+\.\d+\.\d+$/, bank_card: /^\d{16,19}$/ }
  return map[key] || /^$/
}

function maskByCSV(lines) {
  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
  maskColumns.value = headers
  const enabledRules = maskRules.value.filter(r => r.enabled)
  const rows = []
  for (let li = 1; li < lines.length; li++) {
    const vals = lines[li].split(',').map(v => v.trim().replace(/^"(.*)"$/, '$1'))
    const orig = {}, masked = {}
    for (let hi = 0; hi < headers.length; hi++) {
      orig[headers[hi]] = vals[hi] || ''
      let mv = vals[hi] || ''
      for (const rule of enabledRules) {
        const lowerH = headers[hi].toLowerCase()
        if (lowerH.includes(rule.key) || lowerH.includes(rule.key.replace('_', ''))) {
          mv = maskValue(mv, rule.key)
          break
        }
      }
      // Also apply rules based on value pattern
      for (const rule of enabledRules) {
        const regex = getRuleRegex(rule.key)
        if (regex.test(mv)) { mv = maskValue(mv, rule.key); break }
      }
      masked[headers[hi]] = mv
    }
    rows.push({ original: orig, masked })
  }
  maskResult.value = rows
}

// ═══════════════════════════════════════════
// TAB 4: Edge-Case Generator
// ═══════════════════════════════════════════
const edgeDataType = ref('email')
const edgeChecks = ref([])
const edgeReveal = ref(false)

const edgeTypes = [
  { key: 'email', icon: '📧', label: 'Email 地址' },
  { key: 'phone', icon: '📱', label: '手机号' },
  { key: 'date', icon: '📅', label: '日期' },
  { key: 'currency', icon: '💰', label: '货币/价格' },
  { key: 'url', icon: '🌐', label: 'URL' },
  { key: 'ip', icon: '🌍', label: 'IP 地址' },
]

const edgeData = {
  email: { cases: [
    { description: '空字符串', example: '""', shouldTest: true, note: '必填字段必须验证' },
    { description: '缺少 @ 符号', example: '"userdomain.com"', shouldTest: true, note: '' },
    { description: '双 @@ 符号', example: '"user@@domain.com"', shouldTest: true, note: '' },
    { description: 'Unicode 字符', example: '"用户@测试.cn"', shouldTest: true, note: '国际化支持' },
    { description: '超长 (255+ 字符)', example: '"aaa...255chars...@domain.com"', shouldTest: true, note: '防止缓冲区溢出' },
    { description: '本地部分含特殊字符', example: '"user+tag@domain.com"', shouldTest: true, note: 'Gmail 风格别名' },
    { description: '域名部分缺 .', example: '"user@domain"', shouldTest: true, note: '' },
    { description: '本地部分为空', example: '"@domain.com"', shouldTest: true, note: '' },
    { description: '域名部分为空', example: '"user@"', shouldTest: true, note: '' },
    { description: '含空格', example: '"user name@domain.com"', shouldTest: true, note: '' },
    { description: '有效标准邮箱', example: '"test@example.com"', shouldTest: false, note: '正常路径，单独用例覆盖' },
    { description: '含引号本地部分', example: '"\\"user\\"@domain.com"', shouldTest: true, note: 'RFC 允许但罕见' },
    { description: '纯数字邮箱', example: '"12345@domain.com"', shouldTest: false, note: '合法，无特殊处理逻辑' },
  ]},
  phone: { cases: [
    { description: '空值', example: '""', shouldTest: true, note: '' },
    { description: '含字母', example: '"138abcd5678"', shouldTest: true, note: '' },
    { description: '太短 (少位数)', example: '"138123"', shouldTest: true, note: '' },
    { description: '太长 (多位数)', example: '"138123456789"', shouldTest: true, note: '' },
    { description: '国际格式 +86', example: '"+8613812345678"', shouldTest: true, note: '海外用户场景' },
    { description: '含分隔符', example: '"138-1234-5678"', shouldTest: true, note: '格式化输入' },
    { description: '含空格', example: '"138 1234 5678"', shouldTest: false, note: 'UI 可自动 strip' },
    { description: '全角数字', example: '"１３８１２３４５６７８"', shouldTest: true, note: '日文/中文输入法' },
    { description: '特殊字符开头', example: '"+*#13812345678"', shouldTest: true, note: '' },
    { description: '有效 11 位手机号', example: '"13812345678"', shouldTest: false, note: '正常路径' },
    { description: '台湾/香港格式', example: '"0912345678"', shouldTest: true, note: '不同地区长度不同' },
    { description: 'null 值', example: 'null', shouldTest: true, note: '后端可能传 null' },
  ]},
  date: { cases: [
    { description: '空值', example: '""', shouldTest: true, note: '' },
    { description: '非闰年 2月29日', example: '"2025-02-29"', shouldTest: true, note: '经典边界' },
    { description: '12月31日→1月1日', example: '跨年边界', shouldTest: true, note: '年终结算' },
    { description: 'Unix 纪元 0', example: '"1970-01-01"', shouldTest: true, note: '系统默认值冲突' },
    { description: '2038年问题', example: '"2038-01-19"', shouldTest: true, note: '32位系统溢出' },
    { description: '时区跨越', example: 'UTC+14 → UTC-12', shouldTest: true, note: '国际日期变更线' },
    { description: '闰年 2月29日', example: '"2024-02-29"', shouldTest: true, note: '闰年逻辑' },
    { description: '无效格式', example: '"2025/13/01"', shouldTest: true, note: '13 月不存在' },
    { description: '极端未来日期', example: '"9999-12-31"', shouldTest: true, note: '远期合同场景' },
    { description: '负年份', example: '"-0001-01-01"', shouldTest: true, note: '历史数据' },
    { description: '普通日期', example: '"2025-06-15"', shouldTest: false, note: '正常路径' },
    { description: '单月 31 天全测试', example: '月份天数校验', shouldTest: false, note: '边界枚举太多，等价类划分' },
  ]},
  currency: { cases: [
    { description: '零值', example: '0.00', shouldTest: true, note: '免费商品' },
    { description: '负数', example: '-100.00', shouldTest: true, note: '退款/冲正' },
    { description: '最大值 (JS)', example: '9007199254740991', shouldTest: true, note: 'Number.MAX_SAFE_INTEGER' },
    { description: '超过 2 位小数', example: '99.999', shouldTest: true, note: '金额精度' },
    { description: '不同币种符号', example: '"¥100.00"', shouldTest: true, note: '多币种支持' },
    { description: '科学计数法', example: '"1e2"', shouldTest: true, note: '' },
    { description: '逗号分隔', example: '"1,000.00"', shouldTest: true, note: '格式化显示' },
    { description: '空格/空白字符', example: '" 100.00 "', shouldTest: false, note: 'trim 处理' },
    { description: '极小正数', example: '0.01', shouldTest: true, note: '最小金额边界' },
    { description: '字符串混合', example: '"100元"', shouldTest: true, note: '中文货币输入' },
    { description: '正常金额', example: '199.99', shouldTest: false, note: '正常路径' },
    { description: 'null', example: 'null', shouldTest: true, note: '' },
  ]},
  url: { cases: [
    { description: '空字符串', example: '""', shouldTest: true, note: '' },
    { description: '缺少协议', example: '"www.example.com"', shouldTest: true, note: '' },
    { description: '缺少域名', example: '"https:///path"', shouldTest: true, note: '' },
    { description: 'IP 地址 URL', example: '"https://192.168.1.1"', shouldTest: true, note: '内网地址' },
    { description: '超长 URL (2048+ 字符)', example: '"https://example.com/?q=aaa..."', shouldTest: true, note: '浏览器限制' },
    { description: '含认证信息', example: '"https://user:pass@example.com"', shouldTest: true, note: '安全：禁止记录密码' },
    { description: 'javascript: 协议', example: '"javascript:alert(1)"', shouldTest: true, note: 'XSS 向量' },
    { description: 'Unicode 域名', example: '"https://测试.cn"', shouldTest: true, note: 'Punycode' },
    { description: '端口号极端值', example: '"https://example.com:99999"', shouldTest: true, note: '' },
    { description: '含空格', example: '"https://example .com"', shouldTest: true, note: '' },
    { description: '正常 URL', example: '"https://www.example.com/path"', shouldTest: false, note: '正常路径' },
    { description: 'localhost', example: '"http://localhost:3000"', shouldTest: false, note: '开发环境正常' },
  ]},
  ip: { cases: [
    { description: '空字符串', example: '""', shouldTest: true, note: '' },
    { description: '超过 255 的段', example: '"192.168.256.1"', shouldTest: true, note: '' },
    { description: '少于 4 段', example: '"192.168.1"', shouldTest: true, note: '' },
    { description: '多于 4 段', example: '"192.168.1.2.3"', shouldTest: true, note: '' },
    { description: '前导零', example: '"192.168.001.001"', shouldTest: true, note: '八进制混淆风险' },
    { description: 'IPv6 地址', example: '"2001:db8::1"', shouldTest: true, note: 'IPv6 支持' },
    { description: '0.0.0.0', example: '"0.0.0.0"', shouldTest: true, note: '非路由地址' },
    { description: '255.255.255.255', example: '"255.255.255.255"', shouldTest: true, note: '广播地址' },
    { description: '私有地址 (10.0.0.0/8)', example: '"10.0.0.1"', shouldTest: false, note: '合法内网地址' },
    { description: '回环地址 127.0.0.1', example: '"127.0.0.1"', shouldTest: false, note: '合法' },
    { description: '含字母', example: '"192.168.abc.1"', shouldTest: true, note: '' },
    { description: '正常公网 IP', example: '"8.8.8.8"', shouldTest: false, note: '正常路径' },
  ]},
}

const currentEdgeType = computed(() => edgeData[edgeDataType.value] || null)

function resetEdgeCheck() {
  edgeReveal.value = false
  edgeChecks.value = (currentEdgeType.value?.cases || []).map(() => false)
}

const edgeScore = computed(() => {
  if (!edgeReveal.value || !currentEdgeType.value) return 0
  let total = currentEdgeType.value.cases.length
  let correct = 0
  for (let i = 0; i < total; i++) {
    const should = currentEdgeType.value.cases[i].shouldTest
    const checked = edgeChecks.value[i]
    if (should === checked) correct++
  }
  return Math.round(correct / total * 100)
})
const edgeCorrectHits = computed(() => {
  if (!edgeReveal.value || !currentEdgeType.value) return 0
  return currentEdgeType.value.cases.filter((c, i) => c.shouldTest && edgeChecks.value[i]).length
})
const edgeMissed = computed(() => {
  if (!edgeReveal.value || !currentEdgeType.value) return 0
  return currentEdgeType.value.cases.filter((c, i) => c.shouldTest && !edgeChecks.value[i]).length
})
const edgeOverTest = computed(() => {
  if (!edgeReveal.value || !currentEdgeType.value) return 0
  return currentEdgeType.value.cases.filter((c, i) => !c.shouldTest && edgeChecks.value[i]).length
})
const edgeCorrectSkip = computed(() => {
  if (!edgeReveal.value || !currentEdgeType.value) return 0
  return currentEdgeType.value.cases.filter((c, i) => !c.shouldTest && !edgeChecks.value[i]).length
})

function checkEdgeAnswers() {
  edgeReveal.value = true
}

// ═══════════════════════════════════════════
// TAB 5: SQL Data Factory
// ═══════════════════════════════════════════
const sqlTable = ref('users')
const sqlRowCount = ref(10)
const sqlOutput = ref('')
const sqlColumns = ref([])

const sqlTableDefs = {
  users: {
    columns: [
      { name: 'username', type: 'VARCHAR(50)', strategy: '随机用户名', strategies: ['随机用户名', '随机邮箱', '静态值'], staticVal: '' },
      { name: 'email', type: 'VARCHAR(100)', strategy: '随机邮箱', strategies: ['随机邮箱', '随机用户名', '静态值'], staticVal: '' },
      { name: 'password_hash', type: 'VARCHAR(255)', strategy: '静态值', strategies: ['静态值'], staticVal: 'hashed_password_123' },
      { name: 'phone', type: 'VARCHAR(20)', strategy: '随机手机号', strategies: ['随机手机号', '静态值', 'NULL'], staticVal: '' },
      { name: 'age', type: 'INT', strategy: '数字范围', strategies: ['数字范围', '静态值', 'NULL'], staticVal: '', rangeMin: 18, rangeMax: 65 },
      { name: 'created_at', type: 'DATETIME', strategy: '随机日期(90天)', strategies: ['随机日期(90天)', '随机日期(365天)', '静态值'], staticVal: '' },
      { name: 'status', type: 'VARCHAR(20)', strategy: '静态值', strategies: ['静态值', '随机枚举'], staticVal: 'active' },
    ],
  },
  orders: {
    columns: [
      { name: 'user_id', type: 'INT', strategy: '数字范围', strategies: ['数字范围', '静态值'], staticVal: '', rangeMin: 1, rangeMax: 1000 },
      { name: 'product_name', type: 'VARCHAR(100)', strategy: '随机商品名', strategies: ['随机商品名', '静态值'], staticVal: '' },
      { name: 'quantity', type: 'INT', strategy: '数字范围', strategies: ['数字范围', '静态值'], staticVal: '', rangeMin: 1, rangeMax: 10 },
      { name: 'unit_price', type: 'DECIMAL(10,2)', strategy: '随机价格', strategies: ['随机价格', '数字范围', '静态值'], staticVal: '', rangeMin: 9, rangeMax: 9999 },
      { name: 'status', type: 'VARCHAR(20)', strategy: '随机枚举', strategies: ['随机枚举', '静态值'], staticVal: 'pending,paid,shipped,delivered' },
      { name: 'created_at', type: 'DATETIME', strategy: '随机日期(90天)', strategies: ['随机日期(90天)', '随机日期(365天)', '静态值'], staticVal: '' },
    ],
  },
  products: {
    columns: [
      { name: 'name', type: 'VARCHAR(100)', strategy: '随机商品名', strategies: ['随机商品名', '静态值'], staticVal: '' },
      { name: 'category', type: 'VARCHAR(50)', strategy: '静态值', strategies: ['静态值', '随机枚举'], staticVal: 'electronics,clothing,food,books' },
      { name: 'price', type: 'DECIMAL(10,2)', strategy: '随机价格', strategies: ['随机价格', '数字范围', '静态值'], staticVal: '', rangeMin: 1, rangeMax: 9999 },
      { name: 'stock', type: 'INT', strategy: '数字范围', strategies: ['数字范围', '静态值', 'NULL'], staticVal: '', rangeMin: 0, rangeMax: 999 },
      { name: 'description', type: 'TEXT', strategy: '静态值', strategies: ['静态值', 'NULL'], staticVal: 'Sample product description.' },
      { name: 'is_active', type: 'BOOLEAN', strategy: '随机布尔', strategies: ['随机布尔', '静态值'], staticVal: '' },
    ],
  },
}

function applySqlTable() {
  const def = sqlTableDefs[sqlTable.value]
  if (def) sqlColumns.value = JSON.parse(JSON.stringify(def.columns))
  sqlOutput.value = ''
}

function sqlGenValue(col) {
  switch (col.strategy) {
    case '随机用户名': return "'" + pick(['alpha', 'beta', 'gamma', 'delta', 'echo', 'fox', 'ghost', 'hawk', 'iris', 'jade']) + '_' + rand(10, 999) + "'"
    case '随机邮箱': return "'user" + rand(100, 9999) + "@" + pick(['qq.com', '163.com', 'gmail.com', 'example.cn']) + "'"
    case '随机手机号': return "'" + genPhone() + "'"
    case '随机日期(90天)': return "'" + genDate(90) + "'"
    case '随机日期(365天)': return "'" + genDate(365) + "'"
    case '随机商品名': return "'" + pick(products).replace(/'/g, "''") + "'"
    case '随机价格': return parseFloat((Math.random() * 9990 + 9).toFixed(2)).toString()
    case '随机枚举': {
      const vals = (col.staticVal || 'A,B,C').split(',').map(v => v.trim()).filter(v => v)
      return "'" + pick(vals).replace(/'/g, "''") + "'"
    }
    case '随机布尔': return Math.random() > 0.5 ? 'TRUE' : 'FALSE'
    case '静态值': return isNaN(col.staticVal) && col.staticVal !== '' ? "'" + (col.staticVal || '').replace(/'/g, "''") + "'" : (col.staticVal || 'NULL')
    case '数字范围': return String(rand(col.rangeMin || 0, col.rangeMax || 100))
    case 'NULL': return 'NULL'
    default: return "'" + (col.staticVal || '').replace(/'/g, "''") + "'"
  }
}

function generateSQL() {
  const cols = sqlColumns.value
  if (!cols.length) { sqlOutput.value = ''; return }
  const colNames = cols.map(c => c.name).join(', ')
  const lines = []
  for (let i = 0; i < sqlRowCount.value; i++) {
    const values = cols.map(c => sqlGenValue(c)).join(', ')
    lines.push(`INSERT INTO ${sqlTable.value} (${colNames}) VALUES (${values});`)
  }
  sqlOutput.value = lines.join('\n')
}

function copySqlOutput() {
  navigator.clipboard.writeText(sqlOutput.value).catch(() => {})
}

// ── Init ──
resetEdgeCheck()
applySqlTable()
</script>

<style scoped>
.lab-page { max-width: 900px; margin: 0 auto; }

/* Tab bar — same pattern as RequirementLabView */
.tab-bar { display: flex; gap: 2px; margin-bottom: var(--space-md); border-bottom: 2px solid var(--border); flex-wrap: wrap; }
.tab-btn {
  padding: 10px 18px; border: none; background: transparent; cursor: pointer;
  font-size: .82rem; font-weight: 500; color: var(--text-secondary);
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
.form-input {
  width: 100%; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .86rem; background: var(--surface); color: var(--text); outline: none;
  font-family: var(--font-sans);
}
.form-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.form-row { display: flex; gap: 10px; flex-wrap: wrap; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.card-title { font-size: .9rem; font-weight: 650; margin-bottom: 10px; }
.card-title .hint-text { font-weight: 400; }
.hint-text { font-size: .74rem; color: var(--text-muted); }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; flex-wrap: wrap; gap: 8px; }

.sql-input {
  width: 100%; padding: 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .82rem; line-height: 1.7;
  background: #1a1a2e; color: #e5e7eb; outline: none; resize: vertical;
}
[data-theme="dark"] .sql-input { background: #0f1117; color: #e5e7eb; }
.sql-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

/* Checkbox grid */
.checkbox-grid { display: flex; flex-wrap: wrap; gap: 6px; }
.checkbox-item {
  display: flex; align-items: center; gap: 5px; padding: 6px 12px;
  border: 1px solid var(--border); border-radius: 20px; cursor: pointer;
  font-size: .78rem; transition: all var(--fast); user-select: none;
}
.checkbox-item:hover { border-color: var(--primary); }
.checkbox-item.checked { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }
.checkbox-item input[type="checkbox"] { accent-color: var(--primary); width: 14px; height: 14px; cursor: pointer; }

/* Result table — same as DBTestLabView */
.result-table { width: 100%; border-collapse: collapse; font-size: .82rem; }
.result-table th { background: var(--primary-light); color: var(--primary); padding: 10px 14px; text-align: left; font-weight: 600; font-size: .76rem; white-space: nowrap; }
.result-table td { padding: 8px 14px; border-top: 1px solid var(--border-light); }
.result-table tbody tr:hover { background: var(--surface-hover); }

.json-output {
  font-size: .74rem; font-family: var(--font-mono); line-height: 1.5;
  background: #1a1a2e; color: #e5e7eb; padding: 16px 20px;
  max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-break: break-all;
}
[data-theme="dark"] .json-output { background: #0f1117; }

/* Education box */
.education-box {
  margin-top: var(--space-md); padding: 14px 18px;
  background: var(--primary-light); color: var(--primary);
  border-radius: var(--radius); font-size: .78rem; line-height: 1.7;
}

/* ── Pairwise ── */
.pair-params { display: flex; flex-direction: column; gap: 8px; }
.pair-param-row { display: flex; align-items: center; gap: 8px; }
.param-name-input {
  width: 110px; padding: 7px 10px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .78rem; background: var(--surface); color: var(--text); outline: none;
  font-family: var(--font-sans);
}
.param-name-input:focus { border-color: var(--primary); }
.param-values-input {
  flex: 1; padding: 7px 10px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: .78rem; background: var(--surface); color: var(--text); outline: none;
  font-family: var(--font-sans);
}
.param-values-input:focus { border-color: var(--primary); }
.param-count { font-size: .7rem; color: var(--text-muted); min-width: 40px; }

.pairwise-stats { display: flex; align-items: center; gap: 16px; justify-content: center; margin-bottom: 16px; }
.stat-card { text-align: center; padding: 16px 24px; border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg); }
.stat-card-green { border-color: var(--success); background: var(--success-light); }
.stat-number { font-size: 2rem; font-weight: 700; color: var(--primary); }
.stat-card-green .stat-number { color: var(--success); }
.stat-label { font-size: .76rem; color: var(--text-secondary); margin-top: 4px; }
.stat-formula { font-size: .7rem; color: var(--text-muted); margin-top: 2px; }
.stat-arrow { font-size: 1.5rem; color: var(--text-muted); }

/* ── Edge cases ── */
.edge-checklist { margin-top: 14px; }
.edge-info-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.edge-item {
  display: flex; align-items: flex-start; gap: 10px; padding: 8px 10px;
  border-radius: 6px; border: 1px solid transparent; margin-bottom: 2px; flex-wrap: wrap;
}
.edge-item.edge-should { border-color: var(--success); background: var(--success-light); }
.edge-item.edge-skip { border-color: var(--border); background: var(--bg); }
.edge-check-label {
  display: flex; align-items: center; gap: 8px; flex: 1; cursor: pointer;
  font-size: .8rem; line-height: 1.5;
}
.edge-check-label input[type="checkbox"] { accent-color: var(--primary); width: 15px; height: 15px; flex-shrink: 0; }
.edge-desc { flex: 1; }
.edge-example { font-size: .7rem; font-family: var(--font-mono); color: var(--text-muted); background: var(--bg); padding: 1px 6px; border-radius: 3px; white-space: nowrap; }
.edge-answer-tag { font-size: .68rem; padding: 2px 8px; border-radius: 10px; font-weight: 600; white-space: nowrap; flex-shrink: 0; }
.tag-should { background: #d1fae5; color: #065f46; }
.tag-skip { background: #e5e7eb; color: #6b7280; }
.edge-note { width: 100%; font-size: .72rem; color: var(--text-muted); padding-left: 23px; }

/* Result card — same as RequirementLabView */
.result-card { padding: 20px 24px; }
.result-pass { border-left: 4px solid var(--success); }
.result-fail { border-left: 4px solid var(--danger); }
.score-big { font-size: 2.5rem; font-weight: 700; color: var(--primary); text-align: center; }
.score-unit { font-size: 1rem; color: var(--text-muted); font-weight: 400; }
.result-detail { margin-top: 14px; font-size: .8rem; }
.rd-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border-light); }

/* ── Mask ── */
.rule-code { font-size: .68rem; color: var(--text-muted); font-weight: 400; }

/* ── SQL Factory ── */
.sql-cols { display: flex; flex-direction: column; gap: 6px; }
.sql-col-row { display: flex; align-items: center; gap: 8px; }
.sql-col-name { font-size: .8rem; font-weight: 600; font-family: var(--font-mono); min-width: 110px; }
.sql-col-type { font-size: .7rem; color: var(--text-muted); min-width: 90px; font-family: var(--font-mono); }

.sql-output {
  font-size: .74rem; font-family: var(--font-mono); line-height: 1.7;
  background: #1a1a2e; color: #e5e7eb; padding: 16px; border-radius: var(--radius-sm);
  max-height: 420px; overflow-y: auto; white-space: pre-wrap; word-break: break-all;
}
[data-theme="dark"] .sql-output { background: #0f1117; }

/* ── Buttons ── */
.btn-xs { font-size: .7rem; padding: 3px 10px; }
.btn-sm { font-size: .74rem; padding: 6px 14px; }
</style>
