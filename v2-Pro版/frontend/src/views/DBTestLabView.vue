<template>
  <div class="lab-page">
    <!-- Challenge Tabs -->
    <div class="challenge-bar">
      <button v-for="(c, i) in challenges" :key="i" class="challenge-btn"
        :class="{ active: chIdx === i, solved: chSolved[i] }"
        @click="selectChallenge(i)">{{ c.diff }} {{ c.label }}</button>
    </div>

    <!-- Active Challenge -->
    <div v-if="challenges[chIdx]" class="card" style="margin-bottom:var(--space-md);">
      <div class="ch-header">
        <h3>{{ challenges[chIdx].diff }} {{ challenges[chIdx].label }}</h3>
        <span class="tag tag-warning">{{ challenges[chIdx].domain }}</span>
      </div>
      <p class="ch-task-text">{{ challenges[chIdx].task }}</p>

      <details class="schema-details">
        <summary>📋 表结构 & 数据预览</summary>
        <pre class="schema-pre">{{ challenges[chIdx].schema }}</pre>
      </details>

      <!-- SQL Input -->
      <div style="margin-top:12px;">
        <textarea v-model="sql" :placeholder="challenges[chIdx].placeholder" rows="6" class="sql-input"></textarea>
        <div class="toolbar">
          <span class="hint-text">提示: SELECT · FROM · JOIN · WHERE · GROUP BY · HAVING · ORDER BY · LIMIT</span>
          <div style="display:flex;gap:8px;">
            <button class="btn-ghost" style="font-size:.72rem;" @click="showHint = !showHint">{{ showHint ? '隐藏' : '💡' }} 提示</button>
            <button class="btn-ghost" style="font-size:.72rem;" @click="showSolution = !showSolution">{{ showSolution ? '隐藏' : '🔑' }} 答案</button>
            <button class="btn-primary" :disabled="!sql.trim() || loading" @click="execute">▶ 执行</button>
          </div>
        </div>
      </div>

      <!-- Hint -->
      <div v-if="showHint" class="info-box">
        <strong>💡 提示:</strong> {{ challenges[chIdx].hint }}
      </div>

      <!-- Solution -->
      <div v-if="showSolution" class="solution-box">
        <strong>🔑 参考解答:</strong>
        <pre class="solution-code">{{ challenges[chIdx].solution }}</pre>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="card" style="text-align:center;padding:32px;color:var(--text-secondary);">⏳ 执行中...</div>

    <!-- Results -->
    <div v-if="result" class="card" style="overflow:hidden;padding:0;">
      <div v-if="result.ok">
        <div style="padding:12px 20px;font-size:.78rem;color:var(--text-secondary);border-bottom:1px solid var(--border);">
          返回 <strong>{{ result.row_count }}</strong> 行 · {{ result.columns.length }} 列
          <span v-if="challenges[chIdx].expected" style="margin-left:12px;color:var(--text-muted);">
            {{ challenges[chIdx].expected }}
          </span>
        </div>
        <div style="overflow-x:auto;">
          <table v-if="result.rows.length" class="result-table">
            <thead><tr><th v-for="c in result.columns" :key="c">{{ c }}</th></tr></thead>
            <tbody><tr v-for="(row, i) in result.rows" :key="i"><td v-for="c in result.columns" :key="c">{{ row[c] !== null ? row[c] : 'NULL' }}</td></tr></tbody>
          </table>
        </div>
        <p v-if="!result.rows.length" style="padding:32px;text-align:center;color:var(--text-muted);">查询执行成功，无返回数据</p>
      </div>
      <div v-else style="padding:16px 20px;color:var(--danger);background:var(--danger-light);font-size:.84rem;">❌ {{ result.error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { labs } from '../api'

const sql = ref('')
const result = ref(null)
const loading = ref(false)
const showHint = ref(false)
const showSolution = ref(false)
const chIdx = ref(0)
const chSolved = ref([false, false, false])

const challenges = [
  {
    diff: '⭐⭐', label: 'JOINs 数据校验', domain: '数据完整性',
    task: '找出所有订单中 payment 金额与 order total 不一致的记录。这是一个数据完整性检查——确保每笔支付金额与订单金额匹配。',
    placeholder: '-- 连接 orders 和 payments 表，比较 total 和 amount\nSELECT ...',
    schema: `-- orders 表
order_id | user_id | total  | status
1        | 1       | 99.99  | paid
2        | 2       | 149.50 | paid
3        | 1       | 200.00 | pending
4        | 3       | 75.00  | paid
5        | 2       | 59.99  | paid

-- payments 表
payment_id | order_id | amount | method
1          | 1        | 99.99  | credit
2          | 2        | 149.50 | debit
3          | 3        | 150.00 | credit
4          | 4        | 75.00  | credit
5          | 5        | 45.00  | debit

-- order_id=3: total=200.00 vs amount=150.00 (差50)
-- order_id=5: total=59.99 vs amount=45.00 (差14.99)`,
    hint: '使用 JOIN 连接 orders 和 payments 表 ON order_id。比较 orders.total 和 payments.amount。筛选 WHERE orders.total != payments.amount。',
    solution: `SELECT o.order_id, o.total, p.amount, (o.total - p.amount) AS diff
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.total != p.amount`,
    expected: '预期: 2行 — order 3 (200 vs 150) 和 order 5 (59.99 vs 45)',
    levelId: 41,
  },
  {
    diff: '⭐⭐⭐', label: '窗口函数分析', domain: 'QA 分析',
    task: '找出随时间变慢的测试。对每个 test_id，比较第一次运行和最后一次运行的 duration_sec。标记最后一次运行时长 >= 第一次运行时长的 2 倍的测试。',
    placeholder: '-- 使用 ROW_NUMBER() 窗口函数标记第一次和最后一次运行\nWITH ranked AS (\n  SELECT ...\n)',
    schema: `-- test_runs 表
test_id | run_date   | status | duration_sec
1       | 2024-01-01 | pass   | 1.2
1       | 2024-01-08 | pass   | 1.5
1       | 2024-01-15 | pass   | 2.1
1       | 2024-01-22 | pass   | 3.8   ← 变慢 3.2x
2       | 2024-01-01 | pass   | 0.8
2       | 2024-01-08 | pass   | 0.9
2       | 2024-01-15 | pass   | 0.7
2       | 2024-01-22 | pass   | 1.0   ← 稳定 (1.25x)
3       | 2024-01-01 | pass   | 2.5
3       | 2024-01-08 | pass   | 3.2
3       | 2024-01-15 | fail   | 5.1
3       | 2024-01-22 | pass   | 6.0   ← 变慢 2.4x
4       | 2024-01-01 | pass   | 0.5
4       | 2024-01-08 | pass   | 0.6
4       | 2024-01-15 | pass   | 0.5
4       | 2024-01-22 | pass   | 0.7   ← 稳定 (1.4x)`,
    hint: 'ROW_NUMBER() OVER (PARTITION BY test_id ORDER BY run_date) 给每个 test 的运行编号。rn_asc=1 是第一次，rn_desc=1 是最后一次。用 HAVING 比较两次的 duration。',
    solution: `WITH ranked AS (
  SELECT test_id, duration_sec,
    ROW_NUMBER() OVER (PARTITION BY test_id ORDER BY run_date) AS rn_asc,
    ROW_NUMBER() OVER (PARTITION BY test_id ORDER BY run_date DESC) AS rn_desc
  FROM test_runs
)
SELECT DISTINCT test_id
FROM ranked
WHERE rn_asc = 1 OR rn_desc = 1
GROUP BY test_id
HAVING MAX(CASE WHEN rn_desc = 1 THEN duration_sec END)
     > 2 * MAX(CASE WHEN rn_asc = 1 THEN duration_sec END)`,
    expected: '预期: 2行 — test_id 1 和 3 (变慢超2x)',
    levelId: 42,
  },
  {
    diff: '⭐⭐⭐', label: 'NULL 处理 & 数据质量', domain: '数据质量',
    task: '审计 products 表。完成 3 个查询:\n① 找出 price 为 NULL 的产品（不应发生）\n② 找出 description 为 NULL 但 category 不为 NULL 的产品\n③ 统计每列的 NULL 数量',
    placeholder: '-- 查询①: 找出 price IS NULL 的产品\nSELECT ...',
    schema: `-- products 表
product_id | name         | price | description      | category
1          | Widget A     | 19.99 | A useful widget  | electronics
2          | Widget B     | NULL  | Another widget   | electronics
3          | Gadget X     | 29.99 | NULL             | electronics
4          | Gadget Y     | NULL  | NULL             | electronics
5          | Tool Pro     | 49.99 | Professional tool| NULL
6          | Tool Lite    | 9.99  | NULL             | NULL
7          | Super Widget | NULL  | Premium widget   | electronics
8          | Mystery Box  | NULL  | NULL             | NULL

NULL 统计: price=4个, description=4个, category=3个`,
    hint: '查询①: WHERE price IS NULL。查询②: WHERE description IS NULL AND category IS NOT NULL。查询③: COUNT(*) - COUNT(column) 得到 NULL 数量。',
    solution: `-- ① 找出 price 为 NULL 的产品
SELECT * FROM products WHERE price IS NULL;

-- ② description 为 NULL 但 category 不为 NULL
SELECT * FROM products WHERE description IS NULL AND category IS NOT NULL;

-- ③ 统计每列的 NULL 数量
SELECT
  COUNT(*) - COUNT(price) AS null_price,
  COUNT(*) - COUNT(description) AS null_description,
  COUNT(*) - COUNT(category) AS null_category
FROM products;`,
    expected: '查询①预期: 4行 (product_id 2,4,7,8) | 查询②预期: 1行 (product_id 3) | 查询③预期: null_price=4, null_description=4, null_category=3',
    levelId: 43,
  },
]

function selectChallenge(i) {
  chIdx.value = i
  showHint.value = false
  showSolution.value = false
  result.value = null
  sql.value = ''
}

async function execute() {
  loading.value = true; result.value = null
  try {
    const challenge = challenges[chIdx.value]
    result.value = await labs.sql(sql.value, challenge.levelId)
    // Auto-mark solved if results look right
    if (result.value.ok && result.value.row_count > 0) {
      chSolved.value[chIdx.value] = true
    }
  } catch (e) {
    result.value = { ok: false, error: e.message }
  }
  loading.value = false
}
</script>

<style scoped>
.lab-page { max-width: 900px; margin: 0 auto; }

.challenge-bar { display: flex; gap: 6px; margin-bottom: var(--space-md); flex-wrap: wrap; }
.challenge-btn {
  padding: 8px 16px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); cursor: pointer; font-size: .8rem; font-weight: 500;
  transition: all var(--fast); font-family: var(--font-sans);
}
.challenge-btn:hover { border-color: var(--primary); }
.challenge-btn.active { border-color: var(--primary); background: var(--primary-light); color: var(--primary); font-weight: 600; }
.challenge-btn.solved { border-color: var(--success); background: var(--success-light); }

.ch-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.ch-header h3 { font-size: 1rem; font-weight: 650; margin: 0; }
.ch-task-text { font-size: .86rem; color: var(--text); line-height: 1.7; margin-bottom: 10px; white-space: pre-line; }

.schema-details { margin-bottom: 10px; font-size: .8rem; }
.schema-details summary { color: var(--primary); font-weight: 600; cursor: pointer; margin-bottom: 6px; }
.schema-pre {
  font-size: .72rem; font-family: var(--font-mono); line-height: 1.5;
  background: var(--bg-subtle); color: var(--text-secondary);
  padding: 10px 14px; border-radius: var(--radius-sm); overflow-x: auto;
  white-space: pre; max-height: 240px; overflow-y: auto;
}

.sql-input {
  width: 100%; padding: 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-family: var(--font-mono); font-size: .82rem; line-height: 1.7;
  background: #1a1a2e; color: #e5e7eb; outline: none; resize: vertical;
}
[data-theme="dark"] .sql-input { background: #0f1117; color: #e5e7eb; }
.sql-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; flex-wrap: wrap; gap: 8px; }
.hint-text { font-size: .74rem; color: var(--text-muted); }

.info-box {
  margin-top: 10px; padding: 10px 14px; background: var(--primary-light); color: var(--primary);
  border-radius: var(--radius-sm); font-size: .8rem; line-height: 1.6;
}
.solution-box {
  margin-top: 10px; padding: 12px 14px; background: var(--success-light); border-radius: var(--radius-sm); font-size: .8rem;
}
.solution-code {
  font-size: .74rem; font-family: var(--font-mono); line-height: 1.6;
  background: #1a1a2e; color: #e5e7eb; padding: 10px; border-radius: var(--radius-sm);
  margin-top: 6px; overflow-x: auto; white-space: pre-wrap; word-break: break-all;
}
[data-theme="dark"] .solution-code { background: #0f1117; }

.result-table { width: 100%; border-collapse: collapse; font-size: .82rem; }
.result-table th { background: var(--primary-light); color: var(--primary); padding: 10px 14px; text-align: left; font-weight: 600; font-size: .76rem; white-space: nowrap; }
.result-table td { padding: 8px 14px; border-top: 1px solid var(--border-light); }
.result-table tbody tr:hover { background: var(--surface-hover); }
</style>
