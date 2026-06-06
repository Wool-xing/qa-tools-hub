import{A as e,B as t,E as n,M as r,f as i,ft as a,i as o,l as s,o as c,p as l,s as u,t as d,u as f,ut as p,w as m}from"./_plugin-vue_export-helper-DXz6b_sJ.js";import{d as h,u as g}from"./index-CeCIGGd0.js";var _={class:`lab-page`},v={class:`card`,style:{"margin-bottom":`var(--space-md)`}},y={class:`mode-bar`},b=[`value`],x={class:`task-desc`},S={class:`selector-bar`},C={class:`sel-prefix`},w=[`placeholder`],T={class:`html-preview`},E=[`innerHTML`],D={key:0,class:`card match-info`,style:{"margin-top":`12px`}},O={class:`match-tag`},k={class:`match-text`},A={key:0,class:`match-attrs`},j={class:`card`},M={class:`cheat-grid`},N={class:`cheat-css`},P={class:`cheat-xpath`},F=d({__name:`XPathLabView`,setup(d){let F=t(`css`),I=t(``),L=t(0),R=t([]),z=t(``),B=[{name:`📋 登录表单`,task:`定位「登录」按钮`,html:`<form class="login-form" id="login">
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
</div>`}],V=t(0),H=c(()=>B[V.value].html),U=c(()=>F.value===`css`?`button.primary`:`button[@class="primary"]`);function W(e){return e.replace(/&/g,`&amp;`).replace(/</g,`&lt;`).replace(/>/g,`&gt;`)}function G(){if(z.value=W(H.value),!I.value.trim()){L.value=0,R.value=[];return}try{let e=new DOMParser().parseFromString(`<div>`+H.value+`</div>`,`text/html`),t=e.body.firstChild,n=[];if(F.value===`css`)n=[...t.querySelectorAll(I.value)];else{let r=e.evaluate(`.//`+I.value,t,null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null);for(let e=0;e<r.snapshotLength;e++)n.push(r.snapshotItem(e))}L.value=n.length,R.value=n.map(e=>({tag:e.tagName?.toLowerCase()||`#text`,text:e.textContent||``,attrs:e.attributes?[...e.attributes].map(e=>`${e.name}="${e.value}"`).join(` `):``}))}catch{L.value=0,R.value=[]}}e(V,()=>{I.value=``,G()});let K=[{css:`.class`,xpath:`//*[@class="class"]`,desc:`按 class 匹配`},{css:`#id`,xpath:`//*[@id="id"]`,desc:`按 id 匹配`},{css:`div`,xpath:`//div`,desc:`按标签名匹配`},{css:`div > p`,xpath:`//div/p`,desc:`直接子元素`},{css:`div p`,xpath:`//div//p`,desc:`任意后代`},{css:`[data-id]`,xpath:`//*[@data-id]`,desc:`按属性存在`},{css:`[data-id="101"]`,xpath:`//*[@data-id="101"]`,desc:`按属性值`},{css:`button.primary`,xpath:`//button[@class="primary"]`,desc:`标签 + class`},{css:`:first-child`,xpath:`//*[1]`,desc:`第一个子元素`},{css:`:nth-child(2)`,xpath:`//*[2]`,desc:`第 N 个子元素`},{css:`:contains("文本")`,xpath:`//*[contains(text(),"文本")]`,desc:`按文本内容（仅XPath）`},{css:`li.active`,xpath:`//li[contains(@class,"active")]`,desc:`包含 class`}];return(e,t)=>(m(),f(`div`,_,[u(`div`,v,[u(`div`,y,[u(`button`,{class:p({active:F.value===`css`}),onClick:t[0]||=e=>F.value=`css`},`CSS 选择器`,2),u(`button`,{class:p({active:F.value===`xpath`}),onClick:t[1]||=e=>F.value=`xpath`},`XPath`,2),r(u(`select`,{"onUpdate:modelValue":t[2]||=e=>V.value=e,class:`scenario-pick`},[(m(),f(o,null,n(B,(e,t)=>u(`option`,{key:t,value:t},a(e.name),9,b)),64))],512),[[g,V.value]])]),u(`div`,x,[t[4]||=u(`strong`,null,`目标：`,-1),l(a(B[V.value].task),1)]),u(`div`,S,[u(`span`,C,a(F.value===`css`?``:`//`),1),r(u(`input`,{"onUpdate:modelValue":t[3]||=e=>I.value=e,placeholder:U.value,class:`sel-input`,spellcheck:`false`,onInput:G},null,40,w),[[h,I.value]]),u(`span`,{class:p([`match-count`,{hit:L.value>0}])},a(L.value)+` 个匹配`,3)]),u(`div`,T,[t[5]||=i(`<div class="html-header" data-v-cc27b97d><span class="html-dot red" data-v-cc27b97d></span><span class="html-dot yellow" data-v-cc27b97d></span><span class="html-dot green" data-v-cc27b97d></span><span class="html-title" data-v-cc27b97d>page.html</span></div>`,1),u(`pre`,{class:`html-code`,innerHTML:z.value},null,8,E)]),L.value>0?(m(),f(`div`,D,[t[6]||=u(`h4`,null,`匹配的元素`,-1),(m(!0),f(o,null,n(R.value,(e,t)=>(m(),f(`div`,{key:t,class:`match-row`},[u(`span`,O,`<`+a(e.tag)+`>`,1),u(`span`,k,a(e.text?.trim().slice(0,60)||`(空元素)`),1),e.attrs?(m(),f(`span`,A,a(e.attrs),1)):s(``,!0)]))),128))])):s(``,!0)]),u(`div`,j,[t[7]||=u(`h3`,null,`📖 速查表`,-1),u(`div`,M,[(m(),f(o,null,n(K,e=>u(`div`,{key:e.css,class:`cheat-row`},[u(`code`,N,a(e.css),1),u(`code`,P,a(e.xpath),1),u(`span`,null,a(e.desc),1)])),64))])])]))}},[[`__scopeId`,`data-v-cc27b97d`]]);export{F as default};