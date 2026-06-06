import{B as e,E as t,M as n,ft as r,i,l as a,p as o,s,t as c,u as l,ut as u,w as d}from"./_plugin-vue_export-helper-DXz6b_sJ.js";import{d as f,r as p}from"./index-CeCIGGd0.js";var m={class:`lab-page`},h={class:`challenge-bar`},g=[`onClick`],_={key:0,class:`card`,style:{"margin-bottom":`var(--space-md)`}},v={class:`ch-header`},y={class:`tag tag-warning`},b={class:`ch-task-text`},x={class:`schema-details`},S={class:`schema-pre`},C={style:{"margin-top":`12px`}},w=[`placeholder`],T={class:`toolbar`},E={style:{display:`flex`,gap:`8px`}},D=[`disabled`],O={key:0,class:`info-box`},k={key:1,class:`solution-box`},A={class:`solution-code`},j={key:1,class:`card`,style:{"text-align":`center`,padding:`32px`,color:`var(--text-secondary)`}},M={key:2,class:`card`,style:{overflow:`hidden`,padding:`0`}},N={key:0},P={style:{padding:`12px 20px`,"font-size":`.78rem`,color:`var(--text-secondary)`,"border-bottom":`1px solid var(--border)`}},F={key:0,style:{"margin-left":`12px`,color:`var(--text-muted)`}},I={style:{"overflow-x":`auto`}},L={key:0,class:`result-table`},R={key:0,style:{padding:`32px`,"text-align":`center`,color:`var(--text-muted)`}},z={key:1,style:{padding:`16px 20px`,color:`var(--danger)`,background:`var(--danger-light)`,"font-size":`.84rem`}},B=c({__name:`DBTestLabView`,setup(c){let B=e(``),V=e(null),H=e(!1),U=e(!1),W=e(!1),G=e(0),K=e([!1,!1,!1]),q=[{diff:`⭐⭐`,label:`JOINs 数据校验`,domain:`数据完整性`,task:`找出所有订单中 payment 金额与 order total 不一致的记录。这是一个数据完整性检查——确保每笔支付金额与订单金额匹配。`,placeholder:`-- 连接 orders 和 payments 表，比较 total 和 amount
SELECT ...`,schema:`-- orders 表
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
-- order_id=5: total=59.99 vs amount=45.00 (差14.99)`,hint:`使用 JOIN 连接 orders 和 payments 表 ON order_id。比较 orders.total 和 payments.amount。筛选 WHERE orders.total != payments.amount。`,solution:`SELECT o.order_id, o.total, p.amount, (o.total - p.amount) AS diff
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.total != p.amount`,expected:`预期: 2行 — order 3 (200 vs 150) 和 order 5 (59.99 vs 45)`,levelId:41},{diff:`⭐⭐⭐`,label:`窗口函数分析`,domain:`QA 分析`,task:`找出随时间变慢的测试。对每个 test_id，比较第一次运行和最后一次运行的 duration_sec。标记最后一次运行时长 >= 第一次运行时长的 2 倍的测试。`,placeholder:`-- 使用 ROW_NUMBER() 窗口函数标记第一次和最后一次运行
WITH ranked AS (
  SELECT ...
)`,schema:`-- test_runs 表
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
4       | 2024-01-22 | pass   | 0.7   ← 稳定 (1.4x)`,hint:`ROW_NUMBER() OVER (PARTITION BY test_id ORDER BY run_date) 给每个 test 的运行编号。rn_asc=1 是第一次，rn_desc=1 是最后一次。用 HAVING 比较两次的 duration。`,solution:`WITH ranked AS (
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
     > 2 * MAX(CASE WHEN rn_asc = 1 THEN duration_sec END)`,expected:`预期: 2行 — test_id 1 和 3 (变慢超2x)`,levelId:42},{diff:`⭐⭐⭐`,label:`NULL 处理 & 数据质量`,domain:`数据质量`,task:`审计 products 表。完成 3 个查询:
① 找出 price 为 NULL 的产品（不应发生）
② 找出 description 为 NULL 但 category 不为 NULL 的产品
③ 统计每列的 NULL 数量`,placeholder:`-- 查询①: 找出 price IS NULL 的产品
SELECT ...`,schema:`-- products 表
product_id | name         | price | description      | category
1          | Widget A     | 19.99 | A useful widget  | electronics
2          | Widget B     | NULL  | Another widget   | electronics
3          | Gadget X     | 29.99 | NULL             | electronics
4          | Gadget Y     | NULL  | NULL             | electronics
5          | Tool Pro     | 49.99 | Professional tool| NULL
6          | Tool Lite    | 9.99  | NULL             | NULL
7          | Super Widget | NULL  | Premium widget   | electronics
8          | Mystery Box  | NULL  | NULL             | NULL

NULL 统计: price=4个, description=4个, category=3个`,hint:`查询①: WHERE price IS NULL。查询②: WHERE description IS NULL AND category IS NOT NULL。查询③: COUNT(*) - COUNT(column) 得到 NULL 数量。`,solution:`-- ① 找出 price 为 NULL 的产品
SELECT * FROM products WHERE price IS NULL;

-- ② description 为 NULL 但 category 不为 NULL
SELECT * FROM products WHERE description IS NULL AND category IS NOT NULL;

-- ③ 统计每列的 NULL 数量
SELECT
  COUNT(*) - COUNT(price) AS null_price,
  COUNT(*) - COUNT(description) AS null_description,
  COUNT(*) - COUNT(category) AS null_category
FROM products;`,expected:`查询①预期: 4行 (product_id 2,4,7,8) | 查询②预期: 1行 (product_id 3) | 查询③预期: null_price=4, null_description=4, null_category=3`,levelId:43}];function J(e){G.value=e,U.value=!1,W.value=!1,V.value=null,B.value=``}async function Y(){H.value=!0,V.value=null;try{let e=q[G.value];V.value=await p.sql(B.value,e.levelId),V.value.ok&&V.value.row_count>0&&(K.value[G.value]=!0)}catch(e){V.value={ok:!1,error:e.message}}H.value=!1}return(e,c)=>(d(),l(`div`,m,[s(`div`,h,[(d(),l(i,null,t(q,(e,t)=>s(`button`,{key:t,class:u([`challenge-btn`,{active:G.value===t,solved:K.value[t]}]),onClick:e=>J(t)},r(e.diff)+` `+r(e.label),11,g)),64))]),q[G.value]?(d(),l(`div`,_,[s(`div`,v,[s(`h3`,null,r(q[G.value].diff)+` `+r(q[G.value].label),1),s(`span`,y,r(q[G.value].domain),1)]),s(`p`,b,r(q[G.value].task),1),s(`details`,x,[c[3]||=s(`summary`,null,`表结构 & 数据预览`,-1),s(`pre`,S,r(q[G.value].schema),1)]),s(`div`,C,[n(s(`textarea`,{"onUpdate:modelValue":c[0]||=e=>B.value=e,placeholder:q[G.value].placeholder,rows:`6`,class:`sql-input`},null,8,w),[[f,B.value]]),s(`div`,T,[c[4]||=s(`span`,{class:`hint-text`},`提示: SELECT · FROM · JOIN · WHERE · GROUP BY · HAVING · ORDER BY · LIMIT`,-1),s(`div`,E,[s(`button`,{class:`btn-ghost`,style:{"font-size":`.72rem`},onClick:c[1]||=e=>U.value=!U.value},r(U.value?`隐藏`:`💡`)+` 提示`,1),s(`button`,{class:`btn-ghost`,style:{"font-size":`.72rem`},onClick:c[2]||=e=>W.value=!W.value},r(W.value?`隐藏`:`🔑`)+` 答案`,1),s(`button`,{class:`btn-primary`,disabled:!B.value.trim()||H.value,onClick:Y},`▶ 执行`,8,D)])])]),U.value?(d(),l(`div`,O,[c[5]||=s(`strong`,null,`💡 提示:`,-1),o(` `+r(q[G.value].hint),1)])):a(``,!0),W.value?(d(),l(`div`,k,[c[6]||=s(`strong`,null,`🔑 参考解答:`,-1),s(`pre`,A,r(q[G.value].solution),1)])):a(``,!0)])):a(``,!0),H.value?(d(),l(`div`,j,`⏳ 执行中...`)):a(``,!0),V.value?(d(),l(`div`,M,[V.value.ok?(d(),l(`div`,N,[s(`div`,P,[c[7]||=o(` 返回 `,-1),s(`strong`,null,r(V.value.row_count),1),o(` 行 · `+r(V.value.columns.length)+` 列 `,1),q[G.value].expected?(d(),l(`span`,F,r(q[G.value].expected),1)):a(``,!0)]),s(`div`,I,[V.value.rows.length?(d(),l(`table`,L,[s(`thead`,null,[s(`tr`,null,[(d(!0),l(i,null,t(V.value.columns,e=>(d(),l(`th`,{key:e},r(e),1))),128))])]),s(`tbody`,null,[(d(!0),l(i,null,t(V.value.rows,(e,n)=>(d(),l(`tr`,{key:n},[(d(!0),l(i,null,t(V.value.columns,t=>(d(),l(`td`,{key:t},r(e[t]===null?`NULL`:e[t]),1))),128))]))),128))])])):a(``,!0)]),V.value.rows.length?a(``,!0):(d(),l(`p`,R,`查询执行成功，无返回数据`))])):(d(),l(`div`,z,`❌ `+r(V.value.error),1))])):a(``,!0)]))}},[[`__scopeId`,`data-v-4eb0edb3`]]);export{B as default};