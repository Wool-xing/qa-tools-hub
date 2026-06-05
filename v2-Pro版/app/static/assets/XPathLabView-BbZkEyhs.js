import{A as e,F as t,L as n,N as r,S as i,V as a,_ as o,b as s,d as c,f as l,g as u,h as d,k as f,n as p,x as m,y as h,z as g}from"./index-ugAq7dZ4.js";var _={class:`lab-page`},v={class:`card`,style:{"margin-bottom":`var(--space-md)`}},y={class:`mode-bar`},b=[`value`],x={class:`task-desc`},S={class:`selector-bar`},C={class:`sel-prefix`},w=[`placeholder`],T={class:`html-preview`},E=[`innerHTML`],D={key:0,class:`card match-info`,style:{"margin-top":`12px`}},O={class:`match-tag`},k={class:`match-text`},A={key:0,class:`match-attrs`},j={class:`card`},M={class:`cheat-grid`},N={class:`cheat-css`},P={class:`cheat-xpath`},F=p({__name:`XPathLabView`,setup(p){let F=n(`css`),I=n(``),L=n(0),R=n([]),z=n(``),B=[{name:`📋 登录表单`,task:`定位「登录」按钮`,html:`<form class="login-form" id="login">
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
</form>`},{name:`📊 数据表格`,task:`定位表格中所有状态为「已完成」的行`,html:`<table id="data-table" class="table striped">
  <thead><tr><th>ID</th><th>名称</th><th>状态</th><th>操作</th></tr></thead>
  <tbody>
    <tr class="row"><td>1</td><td>需求分析</td><td><span class="badge done">已完成</span></td><td><button>编辑</button></td></tr>
    <tr class="row"><td>2</td><td>用例设计</td><td><span class="badge done">已完成</span></td><td><button>编辑</button></td></tr>
    <tr class="row"><td>3</td><td>测试执行</td><td><span class="badge pending">进行中</span></td><td><button>编辑</button></td></tr>
    <tr class="row"><td>4</td><td>缺陷验证</td><td><span class="badge done">已完成</span></td><td><button>编辑</button></td></tr>
  </tbody>
</table>`},{name:`🧭 导航菜单`,task:`定位当前激活的导航项`,html:`<nav class="sidebar">
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
</nav>`},{name:`🔔 通知列表`,task:`定位所有未读通知`,html:`<div class="notifications">
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
</div>`}],V=n(0),H=u(()=>B[V.value].html),U=u(()=>F.value===`css`?`button.primary`:`button[@class="primary"]`);function W(e){return e.replace(/&/g,`&amp;`).replace(/</g,`&lt;`).replace(/>/g,`&gt;`)}function G(){if(z.value=W(H.value),!I.value.trim()){L.value=0,R.value=[];return}try{let e=new DOMParser().parseFromString(`<div>`+H.value+`</div>`,`text/html`),t=e.body.firstChild,n=[];if(F.value===`css`)n=[...t.querySelectorAll(I.value)];else{let r=e.evaluate(`.//`+I.value,t,null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null);for(let e=0;e<r.snapshotLength;e++)n.push(r.snapshotItem(e))}L.value=n.length,R.value=n.map(e=>({tag:e.tagName?.toLowerCase()||`#text`,text:e.textContent||``,attrs:e.attributes?[...e.attributes].map(e=>`${e.name}="${e.value}"`).join(` `):``}))}catch{L.value=0,R.value=[]}}r(V,()=>{I.value=``,G()});let K=[{css:`.class`,xpath:`//*[@class="class"]`,desc:`按 class 匹配`},{css:`#id`,xpath:`//*[@id="id"]`,desc:`按 id 匹配`},{css:`div`,xpath:`//div`,desc:`按标签名匹配`},{css:`div > p`,xpath:`//div/p`,desc:`直接子元素`},{css:`div p`,xpath:`//div//p`,desc:`任意后代`},{css:`[data-id]`,xpath:`//*[@data-id]`,desc:`按属性存在`},{css:`[data-id="101"]`,xpath:`//*[@data-id="101"]`,desc:`按属性值`},{css:`button.primary`,xpath:`//button[@class="primary"]`,desc:`标签 + class`},{css:`:first-child`,xpath:`//*[1]`,desc:`第一个子元素`},{css:`:nth-child(2)`,xpath:`//*[2]`,desc:`第 N 个子元素`},{css:`:contains("文本")`,xpath:`//*[contains(text(),"文本")]`,desc:`按文本内容（仅XPath）`},{css:`li.active`,xpath:`//li[contains(@class,"active")]`,desc:`包含 class`}];return(n,r)=>(f(),s(`div`,_,[o(`div`,v,[o(`div`,y,[o(`button`,{class:g({active:F.value===`css`}),onClick:r[0]||=e=>F.value=`css`},`CSS 选择器`,2),o(`button`,{class:g({active:F.value===`xpath`}),onClick:r[1]||=e=>F.value=`xpath`},`XPath`,2),t(o(`select`,{"onUpdate:modelValue":r[2]||=e=>V.value=e,class:`scenario-pick`},[(f(),s(d,null,e(B,(e,t)=>o(`option`,{key:t,value:t},a(e.name),9,b)),64))],512),[[c,V.value]])]),o(`div`,x,[r[4]||=o(`strong`,null,`目标：`,-1),i(a(B[V.value].task),1)]),o(`div`,S,[o(`span`,C,a(F.value===`css`?``:`//`),1),t(o(`input`,{"onUpdate:modelValue":r[3]||=e=>I.value=e,placeholder:U.value,class:`sel-input`,spellcheck:`false`,onInput:G},null,40,w),[[l,I.value]]),o(`span`,{class:g([`match-count`,{hit:L.value>0}])},a(L.value)+` 个匹配`,3)]),o(`div`,T,[r[5]||=m(`<div class="html-header" data-v-cc27b97d><span class="html-dot red" data-v-cc27b97d></span><span class="html-dot yellow" data-v-cc27b97d></span><span class="html-dot green" data-v-cc27b97d></span><span class="html-title" data-v-cc27b97d>page.html</span></div>`,1),o(`pre`,{class:`html-code`,innerHTML:z.value},null,8,E)]),L.value>0?(f(),s(`div`,D,[r[6]||=o(`h4`,null,`匹配的元素`,-1),(f(!0),s(d,null,e(R.value,(e,t)=>(f(),s(`div`,{key:t,class:`match-row`},[o(`span`,O,`<`+a(e.tag)+`>`,1),o(`span`,k,a(e.text?.trim().slice(0,60)||`(空元素)`),1),e.attrs?(f(),s(`span`,A,a(e.attrs),1)):h(``,!0)]))),128))])):h(``,!0)]),o(`div`,j,[r[7]||=o(`h3`,null,`📖 速查表`,-1),o(`div`,M,[(f(),s(d,null,e(K,e=>o(`div`,{key:e.css,class:`cheat-row`},[o(`code`,N,a(e.css),1),o(`code`,P,a(e.xpath),1),o(`span`,null,a(e.desc),1)])),64))])])]))}},[[`__scopeId`,`data-v-cc27b97d`]]);export{F as default};