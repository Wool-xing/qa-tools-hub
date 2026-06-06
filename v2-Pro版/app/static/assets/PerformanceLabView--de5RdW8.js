import{E as e,H as t,O as n,P as r,c as i,d as a,ft as o,i as s,m as c,mt as l,p as u,pt as ee,s as d,t as te,u as f}from"./_plugin-vue_export-helper-Dx7e6khD.js";import{f as p,i as ne}from"./index-WgzYGVY0.js";var re={class:`lab-page`},ie={class:`perf-layout`},ae={class:`perf-left`},oe={class:`card`,style:{"margin-bottom":`var(--space-md)`}},se={class:`template-bar`},ce=[`onClick`],le={class:`slider-group`},m={class:`slider-label`},h={class:`slider-group`},g={class:`slider-label`},_=[`disabled`],v={key:0,class:`spinner`},y={class:`perf-right`},b={key:0,class:`card empty-state`},x={key:1,class:`card`,style:{"text-align":`center`,padding:`32px`,color:`var(--text-secondary)`}},S={key:2,class:`results-panel`},C={class:`stat-grid`},w={class:`stat-card`},T={class:`stat-num`},E={class:`stat-num`},D={class:`stat-card`},O={class:`stat-num`},k={class:`stat-card`},A={class:`stat-num`},j={class:`card`,style:{"margin-bottom":`var(--space-md)`,padding:`12px 16px`}},M={class:`endpoint-info`},N={class:`ep-path`},P={class:`ep-meta`},F={class:`card`,style:{"margin-bottom":`var(--space-md)`}},I={class:`latency-bars`},L={class:`lat-key`},ue={class:`lat-bar-track`},R={class:`lat-val`},z={class:`card`,style:{"margin-bottom":`var(--space-md)`}},B={class:`timeline-chart`},V=[`viewBox`],H=[`y1`,`y2`],U=[`points`],de=[`points`],fe=[`points`],pe={class:`card`},me={class:`checks-row`},W=580,G=160,K=te({__name:`PerformanceLabView`,setup(te){let K=t(`import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  const res = http.get('https://api.example.com/users');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}`),q=t(20),J=t(60),Y=t(!1),X=t(null),Z=t(`quick`),he=[{id:`quick`,label:`快速入门`,script:`import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  const res = http.get('https://api.example.com/users');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}`,vus:10,duration:30},{id:`ramp`,label:`渐进加压`,script:`import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const res = http.get('https://api.example.com/products');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}`,vus:100,duration:180},{id:`stress`,label:`压力测试`,script:`import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '1m', target: 100 },
    { duration: '1m', target: 200 },
    { duration: '2m', target: 200 },
    { duration: '1m', target: 0 },
  ],
};

export default function () {
  const res = http.post('https://api.example.com/orders',
    JSON.stringify({ productId: 1, quantity: 1 }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(res, { 'status is 201': (r) => r.status === 201 });
  sleep(0.5);
}`,vus:200,duration:300}],ge=[{key:`min`,label:`Min`},{key:`avg`,label:`Avg`},{key:`p50`,label:`P50`},{key:`p90`,label:`P90`},{key:`p95`,label:`P95`},{key:`p99`,label:`P99`},{key:`max`,label:`Max`}],_e=[`HTTP 状态码`,`响应体非空`,`响应时间 < P95 阈值`];function Q(e){K.value=e.script,q.value=e.vus,J.value=e.duration,Z.value=e.id}async function ve(){Y.value=!0,X.value=null;try{X.value=await ne.performance(K.value,q.value,J.value)}catch(e){X.value={ok:!1,error:e.message}}Y.value=!1}function ye(e){if(!X.value)return`0%`;let t=X.value.latency.max||1;return Math.min(e/t*100,100)+`%`}let be=d(()=>{let e=[];for(let t=1;t<4;t++)e.push(G/4*t);return e}),$=d(()=>{if(!X.value||!X.value.per_second)return``;let e=X.value.per_second;if(e.length===0)return``;let t=Math.max(...e.map(e=>e.rps),1),n=W/Math.max(e.length-1,1);return e.map((e,r)=>{let i=r*n,a=G-e.rps/t*(G-10)-5;return`${i.toFixed(1)},${a.toFixed(1)}`}).join(` `)}),xe=d(()=>{let e=$.value;return e?`0,${G} ${e} ${W},${G}`:``}),Se=d(()=>{if(!X.value||!X.value.per_second)return``;let e=X.value.per_second;if(e.length===0)return``;let t=Math.max(...e.map(e=>e.errors),1),n=W/Math.max(e.length-1,1);return e.map((e,r)=>{let i=r*n,a=G-e.errors/t*(G-10)-5;return`${i.toFixed(1)},${a.toFixed(1)}`}).join(` `)});return(t,d)=>(e(),a(`div`,re,[i(`div`,ie,[i(`div`,ae,[i(`div`,oe,[i(`div`,se,[d[3]||=i(`span`,{class:`template-label`},`📄 模板：`,-1),(e(),a(s,null,n(he,e=>i(`button`,{key:e.id,class:o([`template-btn`,{active:Z.value===e.id}]),onClick:t=>Q(e)},l(e.label),11,ce)),64))]),r(i(`textarea`,{"onUpdate:modelValue":d[0]||=e=>K.value=e,class:`script-editor`,rows:`12`,placeholder:`编写 k6 脚本...`,spellcheck:`false`},null,512),[[p,K.value]]),i(`div`,le,[i(`label`,m,[i(`span`,null,[d[4]||=c(`虚拟用户数 (VUs): `,-1),i(`strong`,null,l(q.value),1)])]),r(i(`input`,{type:`range`,"onUpdate:modelValue":d[1]||=e=>q.value=e,min:`1`,max:`500`,class:`slider`},null,512),[[p,q.value,void 0,{number:!0}]]),d[5]||=i(`span`,{class:`slider-range`},`1 — 500`,-1)]),i(`div`,h,[i(`label`,g,[i(`span`,null,[d[6]||=c(`⏱️ 持续时间: `,-1),i(`strong`,null,l(J.value)+`s`,1)])]),r(i(`input`,{type:`range`,"onUpdate:modelValue":d[2]||=e=>J.value=e,min:`10`,max:`600`,step:`10`,class:`slider`},null,512),[[p,J.value,void 0,{number:!0}]]),d[7]||=i(`span`,{class:`slider-range`},`10s — 600s`,-1)]),i(`button`,{class:`btn-primary btn-run`,disabled:Y.value||!K.value.trim(),onClick:ve},[Y.value?(e(),a(`span`,v)):f(``,!0),i(`span`,null,l(Y.value?` 运行中...`:`▶ 运行测试`),1)],8,_)])]),i(`div`,y,[!X.value&&!Y.value?(e(),a(`div`,b,[...d[8]||=[i(`div`,{class:`empty-icon`},`📊`,-1),i(`p`,null,`点击「运行测试」查看负载测试结果`,-1)]])):f(``,!0),Y.value?(e(),a(`div`,x,` ⏳ 模拟负载测试中... `)):f(``,!0),X.value?(e(),a(`div`,S,[i(`div`,C,[i(`div`,w,[i(`span`,T,l(X.value.total_requests.toLocaleString()),1),d[9]||=i(`span`,{class:`stat-label`},`总请求数`,-1)]),i(`div`,{class:o([`stat-card`,X.value.error_rate>5?`stat-warn`:`stat-ok`])},[i(`span`,E,l(X.value.error_rate)+`%`,1),d[10]||=i(`span`,{class:`stat-label`},`错误率`,-1)],2),i(`div`,D,[i(`span`,O,l(X.value.throughput.avg_rps),1),d[11]||=i(`span`,{class:`stat-label`},`平均 RPS`,-1)]),i(`div`,k,[i(`span`,A,[c(l(X.value.latency.p95),1),d[12]||=i(`span`,{class:`stat-unit`},`ms`,-1)]),d[13]||=i(`span`,{class:`stat-label`},`P95 延迟`,-1)])]),i(`div`,j,[i(`div`,M,[i(`span`,{class:o([`ep-method`,`m-`+X.value.method])},l(X.value.method),3),i(`code`,N,l(X.value.endpoint),1),i(`span`,P,l(X.value.vus)+` VUs · `+l(X.value.duration_sec)+`s`,1)])]),i(`div`,F,[d[14]||=i(`h3`,{class:`section-title`},`⏱️ 延迟分位数 (ms)`,-1),i(`div`,I,[(e(),a(s,null,n(ge,e=>i(`div`,{key:e.key,class:`latency-row`},[i(`span`,L,l(e.label),1),i(`div`,ue,[i(`div`,{class:`lat-bar-fill`,style:ee({width:ye(e.value)})},null,4)]),i(`span`,R,l(X.value.latency[e.key])+` ms`,1)])),64))])]),i(`div`,z,[d[16]||=i(`h3`,{class:`section-title`},`吞吐量时间线 (RPS)`,-1),i(`div`,B,[(e(),a(`svg`,{viewBox:`0 0 580 160`,class:`chart-svg`},[(e(!0),a(s,null,n(be.value,t=>(e(),a(`line`,{key:`g`+t,x1:`0`,x2:W,y1:t,y2:t,stroke:`var(--border-light)`,"stroke-width":`0.5`},null,8,H))),128)),i(`polygon`,{points:xe.value,fill:`var(--primary-light)`,stroke:`none`},null,8,U),i(`polyline`,{points:$.value,fill:`none`,stroke:`var(--primary)`,"stroke-width":`2`},null,8,de),i(`polyline`,{points:Se.value,fill:`none`,stroke:`var(--danger)`,"stroke-width":`1`,"stroke-dasharray":`4,3`},null,8,fe)],8,V)),d[15]||=u(`<div class="chart-legend" data-v-4821f4d8><span class="legend-item" data-v-4821f4d8><span class="legend-dot rps-dot" data-v-4821f4d8></span> RPS</span><span class="legend-item" data-v-4821f4d8><span class="legend-dot err-dot" data-v-4821f4d8></span> 错误数</span></div>`,1)])]),i(`div`,pe,[d[17]||=i(`h3`,{class:`section-title`},`检查结果`,-1),i(`div`,me,[(e(!0),a(s,null,n(X.value.checks_total,t=>(e(),a(`span`,{class:o([`check-badge`,t<X.value.checks_passed?`check-pass`:`check-fail`]),key:t},l(t<=X.value.checks_passed?`✅`:`❌`)+` `+l(_e[t-1]),3))),128))])])])):f(``,!0)])]),d[18]||=u(`<details class="edu-details" data-v-4821f4d8><summary data-v-4821f4d8>📖 这些指标是什么意思？</summary><div class="edu-content" data-v-4821f4d8><div class="edu-grid" data-v-4821f4d8><div class="edu-card" data-v-4821f4d8><h4 data-v-4821f4d8>延迟分位数 (Latency Percentiles)</h4><p data-v-4821f4d8><strong data-v-4821f4d8>P50 (中位数)：</strong>50% 的请求比这个值快。反映&quot;典型用户体验&quot;。</p><p data-v-4821f4d8><strong data-v-4821f4d8>P95：</strong>95% 的请求比这个值快。SLA 常用指标——只允许 5% 的请求超过它。</p><p data-v-4821f4d8><strong data-v-4821f4d8>P99：</strong>99% 的请求比这个值快。捕捉&quot;长尾延迟&quot;——那 1% 最慢的用户在经历什么。</p><p class="edu-tip" data-v-4821f4d8>💡 平均值会隐藏长尾问题。P95/P99 才是性能测试的核心关注点。</p></div><div class="edu-card" data-v-4821f4d8><h4 data-v-4821f4d8>RPS vs VUs</h4><p data-v-4821f4d8><strong data-v-4821f4d8>VUs (虚拟用户)：</strong>同时&quot;在线&quot;并发送请求的模拟用户数量。</p><p data-v-4821f4d8><strong data-v-4821f4d8>RPS (每秒请求数)：</strong>系统实际每秒处理的请求数。这是吞吐量。</p><p class="edu-tip" data-v-4821f4d8>💡 VUs 增加不意味着 RPS 线性增长——当系统饱和时，延迟上升，RPS 反而可能下降。这就是瓶颈点。</p></div><div class="edu-card" data-v-4821f4d8><h4 data-v-4821f4d8>🐌 错误率</h4><p data-v-4821f4d8>负载测试中失败请求的百分比。高错误率通常意味着：</p><ul data-v-4821f4d8><li data-v-4821f4d8>连接池耗尽（数据库 / Redis 连接不够）</li><li data-v-4821f4d8>超时（下游服务在高负载下响应变慢）</li><li data-v-4821f4d8>资源限制（CPU / 内存 / 文件描述符）</li></ul><p class="edu-tip" data-v-4821f4d8>💡 目标：生产环境错误率通常应 &lt; 1%。性能测试的目标是找到错误率开始飙升的那个拐点。</p></div><div class="edu-card" data-v-4821f4d8><h4 data-v-4821f4d8>📐 吞吐量曲线</h4><p data-v-4821f4d8>上面的折线图展示了测试期间 RPS 随时间变化的曲线：</p><ul data-v-4821f4d8><li data-v-4821f4d8><strong data-v-4821f4d8>上升阶段：</strong>VUs 逐步启动，RPS 爬升</li><li data-v-4821f4d8><strong data-v-4821f4d8>稳态阶段：</strong>全部 VUs 运行，RPS 在均值附近波动</li><li data-v-4821f4d8><strong data-v-4821f4d8>下降：</strong>如果 RPS 在 VUs 不变的情况下持续走低，说明系统在退化</li></ul><p class="edu-tip" data-v-4821f4d8>💡 真实的 k6 测试中，你看的是同样的曲线。这个模拟器用对数正态分布生成逼真的延迟数据。</p></div></div></div></details>`,1)]))}},[[`__scopeId`,`data-v-4821f4d8`]]);export{K as default};