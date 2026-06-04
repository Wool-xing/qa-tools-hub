"""Database seed data for QA通关."""

import bcrypt
from sqlalchemy import text
from app.database import sync_engine
from app.models.tool import Tool
from app.models.level import Level
from app.models.user import User

TOOL_SEED = [
    ("Jira","🎯","测试管理","全流程","初级","Atlassian项目管理与缺陷跟踪工具","商业","https://www.atlassian.com/software/jira",True),
    ("Selenium","🤖","自动化测试","测试执行","中级","最流行的Web自动化测试框架","开源","https://www.selenium.dev/",True),
    ("JMeter","⚡","性能测试","测试执行","中级","Apache开源性能测试工具","开源","https://jmeter.apache.org/",True),
    ("Postman","📮","API测试","用例设计/测试执行","初级","最流行的API开发与测试工具","免费","https://www.postman.com/",True),
    ("Cypress","🌲","自动化测试","测试执行","中级","现代前端自动化测试框架","开源","https://www.cypress.io/",True),
    ("Playwright","🎭","自动化测试","测试执行","中级","微软出品跨浏览器E2E框架","开源","https://playwright.dev/",True),
    ("k6","📈","性能测试","测试执行","中级","Grafana现代负载测试工具","开源","https://k6.io/",True),
    ("OWASP ZAP","🛡️","安全测试","测试执行","中级","OWASP旗舰开源安全扫描工具","开源","https://www.zaproxy.org/",True),
]

LEVEL_SEED = [
    (1,"beginner","什么是软件测试？","理解测试定义与基本术语",
     "软件测试是验证软件是否满足需求、发现缺陷的过程。目的是**发现缺陷、评估质量、降低风险**。永远不能说'测完了没bug'（ISTQB原则1），只能说'在给定条件下未发现新缺陷'。",
     None,
     "quiz",{"question":"软件测试的主要目的是什么？","options":["A.证明软件没有缺陷","B.发现缺陷、评估质量、降低风险","C.替代开发人员写代码"],"correct_index":1,"explanation":"测试不能证明软件没有缺陷（原则1），但可以发现缺陷、评估质量、降低风险。"},10,None),
    (2,"beginner","穷尽测试不可能","学会等价类划分和边界值分析",
     "**原则2：穷尽测试是不可能的。** 即使最简单的登录功能，用户名+密码组合是天文数字。必须使用**等价类划分**（将输入分组，每组选代表值）和**边界值分析**（边界是最容易出错的位置）。",
     None,
     "quiz",{"question":"1-100整数输入框的边界值分析应该测试哪些？","options":["A.只测50","B.每个数都测","C.0, 1, 50, 100, 101"],"correct_index":2,"explanation":"边界值：0(边界外)、1(下边界)、50(正常值)、100(上边界)、101(边界外)。不是穷举1到100。"},10,None),
    (3,"beginner","尽早测试 (Shift-Left)","缺陷发现越早成本越低",
     "**原则3：尽早介入测试。** 缺陷修复成本按1:10:100增长——需求阶段发现=1元，开发阶段=10元，生产环境=100元。测试应从需求评审就开始（静态测试），而非等到代码写完。",
     None,
     "explore",{"keywords":["需求","评审","尽早","早期","成本","shift","left"]},10,None),
    (4,"beginner","测试金字塔","理解单元/集成/E2E三层及投入配比",
     "**测试金字塔**由Mike Cohn提出：底层70%**单元测试**(快、稳、多)、中层20%**集成测试**(API/DB交互)、顶层10%**E2E测试**(核心业务链路、慢、脆)。",
     None,
     "quiz",{"question":"测试金字塔中应投入最多的是哪一层？","options":["A.E2E端到端测试","B.集成测试","C.单元测试","D.三层平均分配"],"correct_index":2,"explanation":"单元测试最快、最稳定、维护成本最低，应该在金字塔底层占最大比例(约70%)。"},10,None),
    (5,"beginner","测试用例设计实战","为登录功能写测试用例",
     "测试用例 = **前置条件 + 操作步骤 + 预期结果**。设计方法：等价类划分(有效/无效输入)、边界值(最大/最小/边界外)、正向场景(Happy Path)和异常场景(Error Path)。",
     None,
     "explore",{"keywords":["用户名","密码","登录","测试","用例","预期","边界","有效","无效"]},15,None),
    (6,"beginner","缺陷集群 + 杀虫剂悖论","80%的bug在20%的模块",
     "**原则4：缺陷集群效应。** 大约80%的缺陷集中在20%的模块中——通常是最复杂、改动最频繁的代码。**原则5：杀虫剂悖论**——反复用同一组测试用例最终不再发现新bug，需定期更新。",
     None,
     "quiz",{"question":"杀虫剂悖论的正确应对方式是什么？","options":["A.每次测试都用同样的用例","B.定期审查和更新测试用例","C.只用自动化测试"],"correct_index":1,"explanation":"相同测试用例重复使用会'免疫'，需要定期更新、引入探索性测试等新方法。"},15,None),
    (7,"beginner","上下文依赖 + 无错谬论","航空软件 ≠ 电商网站",
     "**原则6：测试依赖上下文**——航空软件与电商网站的测试策略完全不同。**原则7：无错谬论**——修复了所有已知缺陷 ≠ 产品成功，还得符合用户真实需求、好用。",
     None,
     "quiz",{"question":"以下哪个是'无错谬论'的正确理解？","options":["A.修完所有bug产品就成功了","B.修完bug但不符合用户需求=失败","C.不需要修bug"],"correct_index":1,"explanation":"即使修复了所有缺陷，如果系统不符合用户需求、难以使用，仍然是失败的产品。"},15,None),
    (8,"beginner","测试计划怎么写","学会制定测试策略和排期",
     "测试计划包含：1.测试范围(测什么/不测什么) 2.测试策略(手工/自动化/探索) 3.资源分配(人/环境/工具) 4.排期(什么时候测) 5.风险(可能阻碍测试的因素)。",
     None,
     "explore",{"keywords":["范围","策略","资源","排期","风险","计划","测试"]},10,None),
    (9,"intermediate","API测试入门：Postman","发送第一个API请求",
     "**API测试**验证接口正确性：请求方法(GET/POST/PUT/DELETE)、URL、Headers、Body、响应状态码(200/400/500)、响应体(JSON)。Postman是最流行的API测试工具。",
     "安装Postman→Create Collection→Add Request→输入https://httpbin.org/get→Send→查看响应。在Tests标签写断言：pm.test(\"Status is 200\", ()=>{pm.response.to.have.status(200)})。",
     "quiz",{"question":"HTTP状态码200和500分别表示什么？","options":["A.200=成功, 500=服务器错误","B.200=服务器错误, 500=成功","C.都表示成功"],"correct_index":0,"explanation":"200 OK=请求成功。500 Internal Server Error=服务器内部错误。"},15,4),
    (10,"intermediate","自动化测试：Selenium","打开浏览器、定位元素、点击按钮",
     "**Selenium**是最流行的Web自动化框架。核心流程：打开浏览器→定位元素(by ID/Class/XPath)→操作元素(click/type)→断言(验证结果)。**Page Object Model(POM)**是最佳实践。",
     "安装Selenium：pip install selenium。下载ChromeDriver。编写脚本：打开网页、定位元素、操作、断言。运行观察浏览器自动执行。",
     "code",{"checks":["webdriver","get(","driver.","title"],"test_input":"","expected":""},20,2),
    (11,"intermediate","前端测试：Cypress","实时重载+时间旅行调试",
     "**Cypress**新一代前端测试框架。优势：实时重载(改代码自动重跑)、时间旅行(回看每一步的状态)、自动等待(无需sleep)。开发体验远优于Selenium。",
     "安装：npm i -D cypress。npx cypress open→选择E2E Testing→创建cypress/e2e/first.cy.js→编写cy.visit()→cy.get()→cy.click()。保存后Cypress自动运行。",
     "code",{"checks":["describe(","it(","cy.visit","cy.get"],"test_input":"","expected":""},20,5),
    (12,"advanced","安全测试：OWASP Top 10","理解最常见Web安全漏洞",
     "**OWASP Top 10**最关键10类Web安全风险：1.Injection(SQL注入) 2.Broken Access Control(越权) 3.XSS 4.Insecure Design 5.Security Misconfiguration 6.Vulnerable Components 7.Auth Failures 8.Integrity Failures 9.Logging Failures 10.SSRF。",
     "打开任意网站F12→Network标签→查看请求头中是否包含敏感信息(token/password)。'安全配置错误'的一种——敏感信息通过URL参数传递会被日志记录。",
     "quiz",{"question":"以下哪个是SQL注入攻击的经典示例？","options":["A.输入正确用户名密码","B.输入 ' OR 1=1 --","C.使用HTTPS访问"],"correct_index":1,"explanation":"SQL注入将恶意SQL代码注入输入字段。' OR 1=1 --是经典注入模式，闭合引号+永真条件+注释绕过验证。"},25,8),
    (13,"advanced","端到端测试：Playwright","编写完整登录→操作→验证流程",
     "**Playwright**微软现代E2E框架。优势：3大浏览器引擎、自动等待、网络拦截(API mock)、Trace Viewer。E2E测试应该只覆盖核心业务链路。",
     "安装：npm i -D @playwright/test && npx playwright install。创建tests/e2e.spec.ts→page.goto('/login')→page.fill('#email')→page.click('#submit')→expect(page).toHaveURL()。",
     "code",{"checks":["test(","page.goto","expect","toHaveURL","click"],"test_input":"","expected":""},30,6),
    (14,"advanced","代码覆盖率实践","用Istanbul/JaCoCo衡量测试质量",
     "**代码覆盖率**四维度：行覆盖率、分支覆盖率、函数覆盖率、语句覆盖率。目标：行覆盖率>=80%。100%覆盖率 != 测得好（没覆盖边界条件），但<60%一定不够。",
     None,
     "quiz",{"question":"代码覆盖率100%意味着什么？","options":["A.代码完全没有bug","B.所有代码行都执行过，但不代表没有逻辑缺陷","C.不需要再做任何测试"],"correct_index":1,"explanation":"100%覆盖率只说明代码都被执行过，不代表覆盖了所有输入组合和边界条件。"},20,None),
    (15,"advanced","动手：写一个Python测试脚本","用pytest编写单元测试并运行",
     "**pytest**是Python最流行的测试框架。AAA模式：Arrange(准备数据)→Act(执行)→Assert(断言)。运行：pytest -v。pytest --cov输出覆盖率。",
     "创建test_math.py：\ndef add(a,b): return a+b\ndef test_add():\n    assert add(1,2) == 3\n    assert add(-1,1) == 0\n    assert add(0,0) == 0\n\n运行：pytest test_math.py -v",
     "code",{"checks":["def test","assert","==","def add"],"test_input":"","expected":""},30,None),
    # ===== Web测试 (16-19)，tool_id=2=Selenium =====
    (16,"web","Web自动化：Selenium实战","用Selenium打开浏览器、定位元素、点击按钮",
     "**Selenium WebDriver**是最经典的Web自动化工具。核心API：`find_element(By.ID,'x')`定位、`.click()`点击、`.send_keys()`输入、`.text`获取文本。**Page Object Model(POM)**将页面封装为对象，提高复用性。",
     "pip install selenium\nfrom selenium import webdriver\nfrom selenium.webdriver.common.by import By\ndriver = webdriver.Chrome()\ndriver.get('https://example.com')\nelem = driver.find_element(By.ID, 'search')\nelem.send_keys('test')\nprint(driver.title)\ndriver.quit()",
     "code",{"checks":["webdriver","get(","find_element","By"],"test_input":"","expected":""},20,2),
    (17,"web","前端测试：Cypress组件测试","用Cypress测试Vue/React组件",
     "**Cypress组件测试**支持对单个UI组件进行隔离测试。不同于E2E，组件测试更快更稳定，可直接mount组件并断言其行为和渲染。",
     "npm i -D cypress @cypress/vue\n// cypress/component/Button.cy.js\nimport Button from './Button.vue'\nmount(Button, { props: { label: 'Submit' } })\ncy.get('button').contains('Submit').click()\ncy.get('button').should('be.disabled')",
     "code",{"checks":["mount(","cy.get","click","should"],"test_input":"","expected":""},20,5),
    (18,"web","浏览器DevTools调试技巧","掌握Elements/Console/Network/Application面板",
     "**Chrome DevTools**是测试工程师最常用的调试工具。Elements：查看DOM/CSS，模拟hover/focus状态。Console：执行JS，查看错误。Network：分析请求/响应、时间线、瀑布图。Application：Cookie/LocalStorage/Session。",
     "打开任意网站 → F12 → 切换到Network标签 → 刷新页面 → 点击任一请求查看Headers/Response/Timing → 切换到Console → 输入 document.querySelectorAll('*').length 统计DOM节点数",
     "explore",{"keywords":["F12","DevTools","Network","Console","Elements","请求","响应","localStorage","Cookie"]},15,None),
    (19,"web","Playwright网络拦截与Mock","用Playwright拦截API请求并返回Mock数据",
     "**Playwright网络拦截**是E2E测试的核心技能。`page.route()`拦截特定URL，返回自定义响应，无需真实后端。适合测试各种边界情况（空数据/错误/超时）。",
     "import { test, expect } from '@playwright/test'\ntest('mock API response', async ({ page }) => {\n  await page.route('**/api/users', route => {\n    route.fulfill({ body: JSON.stringify([{name:'Test'}]) })\n  })\n  await page.goto('/users')\n  await expect(page.getByText('Test')).toBeVisible()\n})",
     "code",{"checks":["test(","page.route","fulfill","expect"],"test_input":"","expected":""},20,6),
    # ===== API测试 (20-22) =====
    (20,"api","HTTP协议基础与RESTful API测试","理解HTTP方法、状态码、请求/响应结构",
     "**HTTP协议**是所有API测试的基础。请求=方法(GET/POST/PUT/DELETE/PATCH)+URL+Headers+Body。响应=状态码(2xx成功/4xx客户端错误/5xx服务端错误)+Headers+Body。**RESTful**设计原则：资源用名词复数(/users)，操作用HTTP方法。",
     None,
     "quiz",{"question":"RESTful API中，获取用户列表的正确请求是？","options":["A. POST /getUsers","B. GET /users","C. PUT /user/list","D. DELETE /allUsers"],"correct_index":1,"explanation":"RESTful规范：GET获取资源，/users复数名词。POST用于创建，不是获取。URL只含名词，不含动词。"},15,4),
    (21,"api","GraphQL测试入门","理解Query/Mutation/Subscription三种操作",
     "**GraphQL**是Facebook开发的API查询语言。与REST不同，客户端可以精确指定需要哪些字段，减少过度获取。三种操作：Query(查询)、Mutation(修改)、Subscription(实时订阅)。测试要点：验证查询语法、字段选择、变量、错误处理。",
     "query GetUser($id: ID!) {\n  user(id: $id) {\n    name\n    email\n    posts { title }\n  }\n}\n\n# Variables: { \"id\": \"123\" }\n# 测试要点：验证返回字段与查询一致，无多余字段",
     "explore",{"keywords":["Query","Mutation","GraphQL","字段","变量","Subscription","schema","类型"]},20,None),
    (22,"api","WebSocket实时通信测试","测试WebSocket连接、消息推送、断线重连",
     "**WebSocket**提供全双工通信，与HTTP不同——连接建立后双方都可以随时推送数据。测试要点：连接建立、心跳保活、消息收发顺序、断线重连、并发连接数。常用工具：wscat命令行、Postman WebSocket、Playwright WebSocket支持。",
     None,
     "quiz",{"question":"WebSocket与HTTP的主要区别是？","options":["A. WebSocket更快","B. WebSocket支持全双工通信，连接建立后双方可随时推送","C. HTTP是二进制协议","D. 没有区别"],"correct_index":1,"explanation":"WebSocket是全双工协议，建立连接后服务端可主动推送。HTTP是请求-响应模式，只能客户端发起。"},15,None),
    # ===== APP/移动测试 (23-26) =====
    (23,"mobile","Android APP测试：ADB命令实战","掌握ADB常用命令进行APP调试",
     "**ADB(Android Debug Bridge)**是Android测试核心工具。常用：`adb devices`查看设备、`adb install`安装APK、`adb logcat`查看日志、`adb shell screencap`截图、`adb shell input tap x y`模拟点击、`adb shell dumpsys`系统信息。",
     "adb devices  # 列出连接的设备/模拟器\nadb install app.apk  # 安装应用\nadb logcat | grep -i error  # 过滤错误日志\nadb shell screencap /sdcard/screen.png  # 截图\nadb pull /sdcard/screen.png .  # 导出文件",
     "explore",{"keywords":["adb","devices","install","logcat","shell","screencap","pull","dumpsys"]},15,None),
    (24,"mobile","iOS APP测试：XCTest框架","用XCTest编写iOS自动化测试",
     "**XCTest**是Apple官方iOS/macOS测试框架。支持单元测试、UI测试(XCUITest)、性能测试。UI测试通过accessibility identifiers定位元素，模拟用户操作（tap/swipe/type），自动截图。",
     "import XCTest\nclass LoginUITests: XCTestCase {\n  func testLogin() {\n    let app = XCUIApplication()\n    app.launch()\n    app.textFields[\"email\"].tap()\n    app.textFields[\"email\"].typeText(\"test@test.com\")\n    app.buttons[\"login\"].tap()\n  }\n}",
     "code",{"checks":["XCTest","XCUIApplication","launch","tap","typeText"],"test_input":"","expected":""},25,None),
    (25,"mobile","Appium跨平台移动自动化","一份代码同时测试Android和iOS",
     "**Appium**是最流行的开源移动自动化框架，支持Android/iOS原生/混合/Web应用。基于WebDriver协议，用标准Selenium API写移动测试。Desired Capabilities配置平台、设备、应用信息。",
     "from appium import webdriver\ncaps = {\n  'platformName': 'Android',\n  'deviceName': 'emulator',\n  'app': '/path/to/app.apk'\n}\ndriver = webdriver.Remote('http://localhost:4723', caps)\nel = driver.find_element('id', 'login_btn')\nel.click()",
     "code",{"checks":["appium","webdriver","platformName","find_element","click"],"test_input":"","expected":""},20,None),
    (26,"mobile","小程序测试专项","微信/支付宝小程序特有的测试要点",
     "**小程序测试**与普通Web/App不同：1.环境兼容——微信/支付宝/百度等多平台 2.包大小限制——主包≤2MB 3.审核规范——需过平台审核 4.API权限——部分API需用户授权 5.支付流程——微信支付/支付宝支付链路 6.分享链路——转发/朋友圈。",None,
     "explore",{"keywords":["小程序","微信","支付宝","包大小","审核","授权","支付","分享"]},15,None),
    # ===== 性能测试 (27-29) =====
    (27,"performance","k6性能测试实战","用k6编写负载测试脚本",
     "**k6**是Grafana出品的现代负载测试工具，用JavaScript编写测试脚本。核心概念：VUs(虚拟用户)、stages(加压阶段)、checks(断言)、thresholds(阈值)。k6不像JMeter需要GUI，纯命令行+脚本，适合CI集成。",
     "import http from 'k6/http';\nimport { check, sleep } from 'k6';\nexport const options = {\n  stages: [\n    { duration: '30s', target: 20 },  // 30秒内升至20并发\n    { duration: '1m', target: 20 },   // 保持20并发1分钟\n    { duration: '30s', target: 0 },   // 30秒内降至0\n  ],\n};\nexport default function () {\n  const res = http.get('http://test.k6.io');\n  check(res, { 'status is 200': (r) => r.status === 200 });\n  sleep(1);\n}",
     "code",{"checks":["http.get","check","sleep","stages","VUs|stages"],"test_input":"","expected":""},20,7),
    (28,"performance","JMeter进阶：分布式压测","配置Master-Slave分布式压测架构",
     "**JMeter分布式压测**突破单机瓶颈。架构：Master控制机(调度+收集结果) + 多台Slave执行机(实际发压)。配置：Slave启动jmeter-server，Master的jmeter.properties配置remote_hosts。测试时Master远程启动所有Slave。",
     None,
     "quiz",{"question":"JMeter分布式压测中Master的角色是？","options":["A. 执行压力请求","B. 调度控制+汇总结果","C. 存储测试数据","D. 替代所有Slave"],"correct_index":1,"explanation":"Master负责调度控制（通知Slave开始/停止）和汇总各Slave的测试结果。Slave是真正的压力执行节点。"},20,3),
    (29,"performance","性能监控：Grafana+Kibana","用监控面板观察系统性能指标",
     "**性能测试不止跑脚本**，还需观察系统指标。Grafana：查看CPU/内存/QPS/延迟/错误率等时序指标。Kibana：查询日志中的错误、慢请求。关键指标：P50/P95/P99延迟、TPS/QPS、错误率、资源利用率。",
     None,
     "explore",{"keywords":["Grafana","Kibana","CPU","延迟","QPS","错误率","P99","监控","面板"]},15,None),
    # ===== 安全测试 (30-33) =====
    (30,"security","Burp Suite抓包与渗透基础","用Burp Suite拦截和修改HTTP请求",
     "**Burp Suite**是Web安全测试的瑞士军刀。核心功能：Proxy拦截请求/响应、Repeater重放修改请求、Intruder自动化攻击(爆破/注入)、Scanner自动扫描漏洞。测试流程：配置代理→拦截请求→分析参数→修改重放→观察响应。",
     "1.打开Burp Suite → Proxy → Intercept is on\n2.浏览器设置代理127.0.0.1:8080\n3.访问目标网站 → Burp拦截请求\n4.右键 → Send to Repeater\n5.在Repeater中修改参数 → Send →查看响应\n6.测试点：修改价格参数、修改用户ID、添加XSS payload",
     "explore",{"keywords":["Burp","Proxy","拦截","Repeater","修改","请求","响应","参数"]},20,None),
    (31,"security","SQL注入原理与防御","理解SQL注入并学会参数化查询",
     "**SQL注入**是最古老但仍在OWASP Top 3的安全漏洞。攻击：输入`' OR 1=1 --`闭合引号+永真条件。防御：参数化查询(PreparedStatement)、ORM框架、输入校验、最小权限原则。作为测试工程师，需要能识别代码中的注入风险点。",
     "# 危险代码（可注入）：\nquery = f\"SELECT * FROM users WHERE name='{username}'\"\n\n# 安全代码（参数化查询）：\nquery = \"SELECT * FROM users WHERE name=?\"\ncursor.execute(query, [username])",
     "code",{"checks":["SELECT","WHERE","execute","%s|\\$1|\\?","def test"],"test_input":"","expected":""},25,8),
    (32,"security","XSS跨站脚本攻击与防御","理解反射型/存储型/DOM型XSS",
     "**XSS(跨站脚本)**将恶意脚本注入页面，在用户浏览器中执行。三种类型：反射型(URL参数直接渲染)、存储型(存入数据库后展示)、DOM型(前端JS处理不当)。防御：输出编码、CSP头、HttpOnly Cookie、输入校验。",
     None,
     "quiz",{"question":"以下哪个是最有效的XSS防御措施？","options":["A. 仅在前端校验输入","B. 输出编码+Content-Security-Policy","C. 使用HTTPS","D. 关闭JavaScript"],"correct_index":1,"explanation":"输出编码是XSS防御核心（将<转义为&lt;等）。CSP限制脚本来源作为纵深防御。前端校验可绕过，HTTPS不防XSS。"},20,None),
    (33,"security","认证与授权测试","测试登录、Session、JWT、OAuth、权限控制",
     "**认证(Authentication)≠授权(Authorization)**。认证验证你是谁（登录），授权验证你能做什么（权限）。测试要点：弱密码策略、暴力破解防护、Session固定、JWT过期验证、越权(IDOR——修改URL中的ID访问他人数据)、角色权限绕过。",
     "# JWT测试要点：\n# 1. 过期token是否被拒绝\n# 2. 修改payload中的role/userId能否越权\n# 3. 无token请求是否返回401\n# 4. token刷新机制是否正确\nimport requests\nr = requests.get('/api/user/123', headers={'Authorization': 'Bearer ' + token})\nassert r.status_code == 200",
     "code",{"checks":["token","Authorization","401|403|Bearer","assert","requests"],"test_input":"","expected":""},25,None),
    # ===== 网络协议 & 抓包 (34-36) =====
    (34,"network","TCP/IP协议栈与测试","理解TCP三次握手、四次挥手、拥塞控制",
     "**TCP/IP**是互联网基石。TCP：面向连接、可靠传输(确认+重传)、流量控制、拥塞控制。UDP：无连接、不可靠但快。测试视角：理解连接建立过程才能分析超时错误、端口占用、半开连接。**三次握手**：SYN→SYN-ACK→ACK。**四次挥手**：FIN→ACK→FIN→ACK。",
     None,
     "quiz",{"question":"TCP三次握手中，第二步服务器发送什么？","options":["A. SYN","B. ACK","C. SYN-ACK","D. FIN"],"correct_index":2,"explanation":"三步：1.客户端→SYN→服务器 2.服务器→SYN-ACK→客户端 3.客户端→ACK→服务器。SYN-ACK同时确认客户端的SYN并发送自己的SYN。"},20,None),
    (35,"network","Charles抓包工具实战","用Charles拦截HTTP/HTTPS、模拟弱网、Rewrite",
     "**Charles**是QA最常用的HTTP调试代理。核心功能：1.Structure/Sequence视图查看请求 2.Map Local用本地文件替换响应 3.Rewrite修改请求/响应 4.Throttle模拟2G/3G弱网 5.Breakpoints断点修改实时请求。HTTPS抓包需安装Charles证书。",
     "1. Charles → Proxy → SSL Proxying Settings → 添加 *.*\n2. 手机设置代理为电脑IP:8888 → 安装证书\n3. Tools → Throttle → 选择3G → 感受慢速加载\n4. Tools → Rewrite → 添加规则修改响应体\n5. 右键请求 → Breakpoints → 实时修改请求参数",
     "explore",{"keywords":["Charles","代理","抓包","SSL","Throttle","Rewrite","Map Local","断点"]},15,None),
    (36,"network","Wireshark网络协议分析","用Wireshark抓取和分析网络包",
     "**Wireshark**是网络层抓包工具，比Charles更底层——可以看TCP握手、TLS协商、DNS查询等。显示过滤器：`tcp.port==443`、`http`、`dns`、`ip.src==192.168.1.1`。追踪TCP流：右键→Follow→TCP Stream。",
     "1.选择网卡 → 开始抓包\n2.浏览器访问 http://example.com\n3.停止抓包 → 显示过滤器输入 http\n4.找到HTTP请求 → 右键 Follow HTTP Stream\n5.观察请求头和响应内容\n6.过滤器改为 dns → 看DNS查询过程",
     "explore",{"keywords":["Wireshark","抓包","过滤器","tcp","http","dns","Stream","Follow"]},15,None),
    # ===== 运维 & 数据库 (37-39) =====
    (37,"ops","Linux日志分析实战","用grep/awk/sed命令分析应用日志",
     "**日志分析**是QA排查问题的核心技能。`tail -f app.log`实时追踪；`grep ERROR app.log`过滤错误；`grep -c`统计行数；`awk '{print $1,$3}'`提取列；`sort | uniq -c | sort -rn`排序统计。组合使用是最强日志分析方式。",
     "# 模拟Nginx访问日志分析\n# 192.168.1.1 - [2024-01-15] \"GET /api/users HTTP/1.1\" 200 1234\n\n# 统计每个状态码出现次数\ncat access.log | awk '{print $NF}' | sort | uniq -c | sort -rn\n\n# 统计访问最多的10个IP\ncat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10\n\n# 过滤所有5xx错误\ngrep ' 5[0-9][0-9] ' access.log",
     "code",{"checks":["grep","awk","sort","uniq","cat|tail"],"test_input":"","expected":""},20,None),
    (38,"ops","SQL for QA：数据验证查询","用SQL查询验证测试数据正确性",
     "**SQL是QA必备技能**：验证数据是否正确写入、统计测试数据量、检查数据一致性。常用：SELECT+WHERE过滤、JOIN关联查询、GROUP BY+HAVING分组统计、子查询嵌套。每个测试工程师应该能写出基本的CRUD和统计查询。",
     None,
     "quiz",{"question":"查询每个模块的缺陷数，按数量降序排列的正确SQL是？","options":["A. SELECT * FROM bugs","B. SELECT module, COUNT(*) FROM bugs GROUP BY module ORDER BY COUNT(*) DESC","C. SELECT module FROM bugs SORT BY COUNT","D. SELECT COUNT module FROM bugs"],"correct_index":1,"explanation":"GROUP BY module按模块分组，COUNT(*)统计每组数量，ORDER BY DESC降序排列。"},15,None),
    (39,"ops","Redis缓存测试","测试Redis缓存行为：过期、淘汰、一致性",
     "**Redis**常用于缓存Session、热点数据、消息队列、限流计数。测试要点：TTL过期后key是否删除、内存满时的淘汰策略(LRU/LFU)、缓存与DB一致性、并发读写、哨兵/集群模式故障切换。`redis-cli`命令行可直接操作。",
     "# Redis CLI 常用命令\nredis-cli SET user:123 '{\"name\":\"test\"}' EX 300  # 设置带TTL的缓存\nredis-cli TTL user:123  # 查看剩余过期时间（秒）\nredis-cli KEYS 'session:*'  # 查看所有session\nredis-cli INFO stats  # 查看命中率等统计",
     "explore",{"keywords":["Redis","缓存","TTL","过期","SET","GET","KEYS","INFO"]},15,None),
    # ===== CI/CD (40-41) =====
    (40,"cicd","Jenkins流水线测试集成","用Jenkins Pipeline实现自动化测试CI",
     "**Jenkins**是经典的CI/CD工具。Pipeline as Code用Jenkinsfile定义构建→测试→部署流程。测试阶段：代码检出→依赖安装→单元测试→代码扫描→打包→部署测试环境→自动化测试→报告。post块定义成功/失败时的操作。",
     "pipeline {\n  agent any\n  stages {\n    stage('Test') {\n      steps {\n        sh 'pip install -r requirements.txt'\n        sh 'pytest --junitxml=report.xml --cov'\n        sh 'bandit -r .'\n      }\n      post {\n        always { junit 'report.xml' }\n        failure { emailext body: '测试失败', subject: 'Build Failed', to: 'qa@team.com' }\n      }\n    }\n  }\n}",
     "code",{"checks":["pipeline","stage","steps","pytest|test","post"],"test_input":"","expected":""},20,None),
    (41,"cicd","GitHub Actions自动化测试","用GitHub Actions在PR时自动运行测试",
     "**GitHub Actions**是GitHub内置CI/CD。在`.github/workflows/`下创建YAML文件定义工作流。on: pull_request触发PR测试。matrix策略可同时测试多Python版本/多OS。测试失败PR自动标红，通过标绿。",
     "name: Run Tests\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n        python-version: [3.10, 3.11, 3.12]\n    steps:\n    - uses: actions/checkout@v4\n    - uses: actions/setup-python@v5\n      with: { python-version: '${{ matrix.python-version }}' }\n    - run: pip install -r requirements.txt\n    - run: pytest --cov --cov-report=xml\n    - uses: codecov/codecov-action@v3",
     "code",{"checks":["on:","jobs:","steps:","pytest|test","runs-on"],"test_input":"","expected":""},20,None),
    # ===== 车载测试 (42-43) =====
    (42,"automotive","ASPICE与车载软件质量","理解Automotive SPICE过程评估模型",
     "**ASPICE(Automotive SPICE)**是汽车行业软件过程改进和能力评估标准。定义了V模型开发流程中的32个过程域。与通用测试不同，车载测试强调整车集成测试、HIL(Hardware-in-the-Loop)硬件在环测试、功能安全(ISO 26262)。",
     None,
     "quiz",{"question":"ASPICE中HIL测试是指什么？","options":["A. 纯软件单元测试","B. 硬件在环测试——用真实ECU+仿真环境","C. 手动测试","D. 性能测试"],"correct_index":1,"explanation":"HIL(Hardware-in-the-Loop)将真实ECU(电子控制单元)连接到仿真环境，测试硬件和软件协同行为，是车载测试核心方法。"},25,None),
    (43,"automotive","CAN总线协议与测试","理解CAN总线通信原理和测试方法",
     "**CAN(Controller Area Network)**是汽车内部ECU通信的核心总线协议。特点：多主架构、优先级仲裁、错误检测(CRC)。测试需要CAN分析仪硬件+工具(CANoe/CANalyzer)来监控、注入、分析CAN报文。测试要点：信号正确性、时序、错误帧、总线负载。",
     None,
     "explore",{"keywords":["CAN","总线","ECU","报文","CANoe","CANalyzer","仲裁","帧"]},25,None),
    # ===== Debug挑战 (44-45) =====
    (44,"advanced","Debug：修复登录验证逻辑","找出并修复代码中的Bug",
     "**Debug是QA的核心能力**——不只是发现问题，还要定位根因。下面的代码有逻辑错误：正常用户登录被拒绝。\n\n错误现象：用户输入正确的admin/password123，返回'Invalid credentials'。但代码逻辑看起来应该匹配。\n\n提示：检查字符串比较和字典访问。",
     "# Bug: 输入 admin / password123 无法登录\ndef login(username, password):\n    users = {\"admin\": \"pass123\", \"alice\": \"password123\"}\n    if username in users:\n        if users[username] = password:\n            return \"Login OK\"\n    return \"Invalid credentials\"\n\nprint(login(\"admin\", \"password123\"))",
     "debug",{"checks":["==","password123","Login OK"],"test_input":""},30,None),
    (45,"web","Debug：修复CSS选择器测试","修复Selenium定位器中的错误",
     "**Debug #2：测试代码Bug**——下面的Selenium测试脚本找不到登录按钮。\n\n错误现象：`NoSuchElementException: Unable to locate element: #login-btn`。但HTML中确实有id='login-btn'的按钮。\n\n提示：检查window切换和等待逻辑。",
     "# Bug: driver.find_element 找不到 #login-btn\ndef test_login():\n    driver = webdriver.Chrome()\n    driver.get(\"https://example.com\")\n    driver.find_element_by_id(\"login-btn\").click()\n    return \"OK\"",
     "debug",{"checks":["find_element","By.ID","login-btn"],"test_input":""},25,None),
    # ===== 场景判断 Scenario (46-50) =====
    (46,"advanced","场景判断：紧急上线决策","产品要求2小时内上线一个hotfix，你只有时间做一件事。选择最佳方案。",
     "**背景：** 用户报告支付成功但订单状态不更新的P0 Bug。开发修复了订单状态更新的SQL查询。产品要求2小时内上线——你的完整回归测试套件需要4小时。\n\n**作为QA，你只有时间做一件事。你选择？**",
     None,
     "scenario",{
         "question": "只能做一件事，你选择什么？",
         "options": [
             "A. 跑完整回归测试套件——质量第一，延迟上线",
             "B. 只测试支付→订单这条关键链路 + 边界条件，通过就上线",
             "C. 信任开发，直接上线——这是小改动",
             "D. 让产品和开发自己决定，QA不担责任"
         ],
         "correct_index": 1,
         "explanation": "P0线上Bug的hotfix需要风险平衡——不是不测也不是全测。B是正确做法：识别关键路径（支付→订单），测试核心流程+常见边界（空购物车、重复支付、金额边界），通过后上线并在生产环境监控。A延迟上线意味着P0 Bug继续影响用户(风险更大)，C无质量控制，D是消极逃避。",
         "option_analysis": [
             "跑完整回归——理想但实际不可行。P0 Bug每多在线上一分钟就多影响用户。4小时延迟 = 4小时用户受损。QA的价值是管理风险，不是消除风险。",
             "✅ 正确！风险驱动的测试决策。识别核心影响路径，在有限时间内做最高价值的测试。上线后配合生产监控和灰度发布。",
             "信任不等于放弃验证。即使是「小改动」，SQL查询修改可能影响其他依赖订单状态的模块(报表、库存、通知)。最低限度应验证核心路径。",
             "QA的核心职责是提供质量信息，不是推卸责任。产品和开发依赖你的专业判断来做出上线决策。不做判断等于放弃职业价值。"
         ]
     },35,None),
    (47,"advanced","场景判断：1000个自动化用例全红","CI管道中1000个自动化用例一夜之间全部失败。你如何响应？",
     "**背景：** 周一早上打开CI，发现周末的自动化测试运行全部失败——1000个用例，全部红色。昨晚最后一次部署是前端CSS改动。\n\n**你应该首先做什么？**",
     None,
     "scenario",{
         "question": "1000个用例全红，第一步做什么？",
         "options": [
             "A. 逐个检查1000个失败用例，找出所有Bug",
             "B. 先检查是否是基础设施问题（环境/网络/数据库），再抽样分析失败模式",
             "C. 立即回滚昨晚的部署",
             "D. 忽略——可能是环境抖动，重跑一次"
         ],
         "correct_index": 1,
         "explanation": "1000个用例同时失败几乎不可能是1000个不同的Bug——一定是共性原因。B正确：先检查基础设施（环境宕机、数据库连接池耗尽、DNS故障、证书过期），然后看几个失败用例的报错堆栈找共性模式。C可能正确但不是第一步（如果是网络抖动回滚没用）。D浪费CI资源。A在找到根因前逐个检查是低效的。",
         "option_analysis": [
             "逐个检查1000个失败用例——效率极低。1000个用例同时失败意味着共性原因，不是1000个独立Bug。寻找模式比逐个排查快100倍。",
             "✅ 正确！系统性思维。1000个全红 → 检查基础设施 → 分析失败模式 → 定位根因 → 修复。90%的情况是环境问题而非代码Bug。",
             "回滚可能是正确的最终操作，但不应该是第一步。如果故障原因是数据库迁移，回滚部署不能恢复数据库。先诊断再决定行动。",
             "重跑浪费资源且可能掩盖真正问题。如果是间歇性基础设施故障，重跑可能通过但下次还会发生。永远先调查原因。"
         ]
     },35,None),
    (48,"advanced","场景判断：自动化还是手工？","新项目只有你一个QA，需要决定测试策略。预算有限。",
     "**背景：** 你加入一个新项目——初创公司，只有你一个QA。产品每2周发布一次，UI频繁变动。产品经理想你写自动化覆盖所有功能，但你知道UI还在剧烈变化。\n\n**你建议什么策略？**",
     None,
     "scenario",{
         "question": "作为唯一QA，你的测试策略建议是？",
         "options": [
             "A. 立刻开始写Selenium UI自动化，覆盖所有核心流程",
             "B. 聚焦API/单元测试自动化 + 核心UI手工测试 + 探索性测试",
             "C. 全手工测试——反正只有一个人，自动化投资回报不够",
             "D. 等UI稳定后再开始任何测试工作"
         ],
         "correct_index": 1,
         "explanation": "UI频繁变动时，UI自动化维护成本极高（定位器频繁失效）。B遵循测试金字塔：底层API/单元测试稳定且维护成本低，手工测试灵活应对UI变化，探索性测试发现自动化遗漏的Bug。这是有限资源下的最优策略。A的UI自动化在UI稳定后可以逐步引入，但不应是第一步。",
         "option_analysis": [
             "UI频繁变动时写UI自动化是资源的浪费——每次UI改版你的定位器就失效，维护成本远超编写成本。等UI稳定后再做UI自动化。",
             "✅ 正确！遵循测试金字塔：底层自动化(API/单元)投入70%，手工20%，探索10%。API比UI稳定，自动化投资回报更高。",
             "完全手工测试在快速迭代项目中也无法持续——每2周回归测试会越来越长。关键API的自动化可以释放你的时间做更有价值的探索性测试。",
             "等UI稳定 = 不测试。项目永远在变化中。测试应该与开发并行，帮助项目早期发现架构问题。API测试可以立即开始。"
         ]
     },35,None),
    (49,"advanced","场景判断：无法复现的Bug","用户报告了一个严重Bug但你无法复现。如何处理？",
     "**背景：** VIP客户报告：「导出报表功能点击后页面一直转圈，最终超时。数据量约10万行。」你尝试导出100行——正常。1000行——正常。10000行——也正常。但你只有标准测试环境，客户是生产环境。\n\n**你如何推进这个Bug？**",
     None,
     "scenario",{
         "question": "VIP客户的Bug你无法复现，正确的处理方式是？",
         "options": [
             "A. 标记为「无法复现」并关闭——测试环境正常",
             "B. 请求生产环境访问权限或日志 + 用10万行数据在性能环境复现 + 即使无法复现也保持Open",
             "C. 告诉客户这是他们环境的问题，不是Bug",
             "D. 反复在测试环境尝试——总能复现的"
         ],
         "correct_index": 1,
         "explanation": "无法复现 ≠ 不存在。VIP客户的Bug必须严肃对待。B正确：获取生产日志/数据（脱敏），在性能环境中模拟真实负载（10万行），并保持Bug Open直到确认修复或排除。A会失去客户信任。C推卸责任。D没有改变测试条件无法产生不同结果。",
         "option_analysis": [
             "无法复现就关闭是QA最危险的惯性思维。你的测试环境和生产环境在数据量、并发、网络拓扑上可能完全不同。Bug可能只在特定条件下触发。",
             "✅ 正确！VIP客户的Bug需要主动调查：获取生产数据+日志，在匹配环境中复现，即使无法复现也保持跟踪+添加监控+与客户保持沟通。",
             "推给客户环境既不专业也不准确。QA的职责是帮助定位问题根源——可能是数据量、并发、特定数据格式，甚至是配置差异。",
             "在相同条件下重复测试期望不同结果是低效的。改变条件：更大的数据量、更慢的网络、更高的并发、生产数据快照。"
         ]
     },35,None),
    (50,"advanced","场景判断：测试报告怎么说","CEO要求你明天汇报产品质量状态。你有30分钟准备。说什么？",
     "**背景：** 明天要向CEO汇报产品质量状态。你有：200个Bug（30个P0/P1已修复，5个P0未修复），自动化覆盖率62%，上周生产环境3次事故（全部已恢复），性能测试显示首页加载3.2秒（目标<2秒）。\n\n**你选择什么作为汇报重点？**",
     None,
     "scenario",{
         "question": "面对CEO的30分钟汇报，你的核心信息是？",
         "options": [
             "A. 详细展示200个Bug的分布图和自动化覆盖率趋势——数据说话",
             "B. 聚焦5个未修复P0 Bug的风险+首页性能问题+上周事故根因和改进措施——用业务语言讲质量风险",
             "C. 只汇报好的指标——62%覆盖率在增长，30个P0已修复",
             "D. 逐条汇报上周3次事故的详细时间线和责任人"
         ],
         "correct_index": 1,
         "explanation": "CEO不关心Bug数量和覆盖率细节——他们关心的是：「产品能发布吗？」「有什么风险？」「我们的用户受影响吗？」B正确：用业务语言讲质量风险（这5个P0可能影响多少用户、首页慢3.2秒可能损失多少转化率），每个风险附带你建议的缓解措施。这是QA从「测试员」到「质量顾问」的转变。",
         "option_analysis": [
             "CEO不需要看Bug分布图——那是测试经理关心的。向高管汇报要用业务影响语言：「首页慢1.2秒可能导致X%的收入损失」比「覆盖率62%」更有说服力。",
             "✅ 正确！高管汇报公式：风险(用户影响×发生概率) + 缓解措施 + 发布建议。用业务语言讲质量故事，不是测试指标堆砌。",
             "选择性汇报是隐瞒风险。5个未修复P0和3次事故是你最应该汇报的内容。掩盖坏消息的QA最终会失去信任。透明 ≠ 悲观。",
             "事故逐条分析可以在事后复盘会做，不是CEO汇报的重点。CEO需要的是：发生了什么→为什么→如何防止再次发生→当前风险状态。"
         ]
     },35,None),
    # ===== 扩展薄弱领域 (51-57) =====
    (51,"automotive","车载软件测试流程：从V模型到敏捷","理解车载软件开发的V模型生命周期",
     "**车载软件开发遵循V模型**：左侧需求→架构→详细设计→编码，右侧单元测试→集成测试→系统测试→验收测试。与互联网敏捷不同，车载软件有ASPICE强制约束——每个阶段必须有对应的测试活动。\n\n关键区别：需求冻结后不可随意变更（安全影响），测试证据必须可追溯（审计要求），硬件在环(HIL)测试是强制项。",
     None,
     "quiz",{"question":"车载软件V模型中，单元测试对应哪个开发阶段？","options":["A. 需求分析","B. 架构设计","C. 详细设计/编码","D. 系统集成"],"correct_index":2,"explanation":"V模型左右对称：左侧的详细设计/编码对应右侧的单元测试。这是最底层的测试，验证每个函数/模块的正确性。"},20,None),
    (52,"automotive","ISO 26262 功能安全与测试","理解汽车功能安全等级(ASIL)与测试的关系",
     "**ISO 26262定义ASIL等级：** QM(无安全要求) → ASIL A(最低) → ASIL B → ASIL C → ASIL D(最高)。等级越高，要求的测试覆盖率越高、测试方法越严格。\n\nASIL D（如刹车系统）：需MC/DC覆盖率+故障注入测试+冗余验证+形式化方法。ASIL A（如仪表盘）：语句覆盖率+基本功能测试即可。",
     None,
     "quiz",{"question":"ASIL D级别（如刹车系统）要求的代码覆盖率是？","options":["A. 语句覆盖(Statement)","B. 分支覆盖(Branch)","C. MC/DC覆盖(Modified Condition/Decision)","D. 不需要覆盖率"],"correct_index":2,"explanation":"ASIL D最高安全等级要求MC/DC覆盖——每个条件独立影响决策结果，比分支覆盖更严格（如 if(A && B) 需要4个测试用例而不是2个）。"},25,None),
    (53,"cicd","GitLab CI/CD vs GitHub Actions：选择与迁移","对比两大CI平台的异同，学会技术选型",
     "**GitLab CI：** `.gitlab-ci.yml`，内置Docker Registry + Auto DevOps，适合自托管GitLab实例。**GitHub Actions：** `.github/workflows/*.yml`，Marketplace 2万+ Actions，适合开源项目。\n\n关键区别：GitLab CI的Runner可部署在私有网络（安全合规场景），GitHub Actions的矩阵策略更灵活（多OS/多版本并行）。",
     None,
     "quiz",{"question":"企业内网有合规要求（代码不出公司网络），应选哪个CI平台？","options":["A. GitHub Actions——社区Actions最多","B. GitLab CI——Runner可部署在内网","C. Jenkins——最灵活","D. 无所谓，都能配置"],"correct_index":1,"explanation":"GitLab CI Runner可部署在公司内网，代码和构建产物不出企业网络。GitHub Actions的Runner在GitHub托管（SaaS），不符合合规要求。Jenkins(C)也是可行选择但不是最优——GitLab CI与版本控制紧密集成。"},20,None),
    (54,"cicd","CI中的测试分层策略：快慢分离","如何组织CI pipeline让测试既快又全面",
     "**CI测试策略：** ①Pre-commit(5s)：lint + 格式化检查 ②PR阶段(5min)：单元测试 + 组件测试 ③合并后(15min)：集成测试 + API测试 ④夜间(2h)：E2E + 性能 + 安全扫描。\n\n原则：越早的测试越快，覆盖面越小。PR阶段让开发者快速获得反馈，夜间任务保证全面覆盖。",
     None,
     "explore",{"keywords":["Pre-commit","PR","lint","单元","集成","E2E","快慢","夜间","分层","反馈"]},15,None),
    (55,"performance","前端性能测试：Core Web Vitals","理解LCP/FID/INP/CLS指标及其测试方法",
     "**Google Core Web Vitals：** LCP(最大内容绘制≤2.5s)、INP(交互延迟≤200ms)、CLS(累计布局偏移≤0.1)。测试工具：Lighthouse(实验室数据)、Chrome UX Report(真实用户数据)、Web Vitals JS库(实时监控)。\n\n前端性能测试 ≠ 后端压力测试——前者关注用户体验感知，后者关注系统吞吐量。",
     None,
     "quiz",{"question":"LCP (Largest Contentful Paint) 衡量什么？","options":["A. 服务器响应时间","B. 页面主要内容加载完成的时间","C. JavaScript执行时间","D. 数据库查询时间"],"correct_index":1,"explanation":"LCP衡量视口内最大内容元素（图片/视频/文本块）完成渲染的时间——用户感知的「页面加载好了」的时刻。优化方向：CDN加速、预加载关键资源、压缩图片。"},20,7),
    (56,"ops","容器化测试环境管理","用Docker Compose搭建可复现的测试环境",
     "**测试环境一致性**是QA的常见痛点——「在我的环境上能跑」不应是借口。Docker Compose解决：一个YAML定义所有服务(DB+缓存+消息队列+被测应用)，一条命令启动完整环境。\n\n`docker compose up -d` → 运行测试 → `docker compose down`。CI中每个PR都启动全新环境→测试→销毁，确保环境隔离。",
     None,
     "code",{"checks":["docker","compose","image|build","ports|port","depends_on|depends"],"test_input":"","expected":""},25,None),
    (57,"api","契约测试：Pact基础","理解Consumer-Driven Contract Testing解决什么问题",
     "**契约测试(Contract Testing)**解决微服务间的接口兼容性问题。Provider(API服务)和Consumer(客户端)之间定义契约：「若Provider保证响应的JSON包含{id:int,name:string}，Consumer就能正常工作」。\n\n**Pact流程：** Consumer生成契约→Provider验证契约→Pact Broker存储结果→CI中自动验证。比E2E更快（无需启动全部服务），比单元测试更真实（真实HTTP交互）。",
     None,
     "explore",{"keywords":["契约","Pact","Consumer","Provider","Contract","微服务","兼容","Mock"]},20,None),
    # ===== 新领域: 无障碍测试 (58-59) =====
    (58,"accessibility","无障碍测试入门：WCAG 2.1与a11y","理解为什么无障碍测试是QA必须掌握的技能",
     "**无障碍测试(Accessibility Testing)**确保残疾人（视障/听障/运动障碍/认知障碍）能正常使用产品。欧美法律要求（ADA/Section 508/EN 301 549），不达标可能面临诉讼。\n\n**WCAG 2.1四大原则(POUR)：** Perceivable(可感知)、Operable(可操作)、Understandable(可理解)、Robust(健壮)。三个等级：A(最低)、AA(标准)、AAA(最优)。大多数法律要求AA级。\n\n测试工具：aXe引擎、WAVE、Lighthouse Accessibility、屏幕阅读器(NVDA/VoiceOver)、键盘导航测试。",
     None,
     "quiz",{"question":"WCAG 2.1的四个核心原则缩写POUR代表什么？","options":["A. Performance, Operation, UI, Response","B. Perceivable, Operable, Understandable, Robust","C. Process, Output, User, Report","D. Page, Object, URL, Request"],"correct_index":1,"explanation":"POUR = Perceivable(信息必须能被用户感知)、Operable(界面必须能操作)、Understandable(内容和操作必须可理解)、Robust(内容必须能被各种用户代理解析)。"},15,None),
    (59,"accessibility","无障碍测试实操：键盘+屏幕阅读器","动手实践——只用键盘和屏幕阅读器完成一个任务",
     "**实操挑战：** 关闭鼠标，只用Tab/Shift+Tab/Enter/Space/方向键完成以下操作。你会发现大量无障碍问题：无法聚焦的元素、不清晰的焦点指示器、缺失的skip-link、无意义的aria-label。\n\n**屏幕阅读器测试：** 打开NVDA(Windows)或VoiceOver(Mac)，闭上眼睛，只用键盘和声音导航。判断：①是否能理解页面结构？②是否能完成核心任务（如登录）？③是否在任何步骤「迷路」？",
     None,
     "explore",{"keywords":["键盘","Tab","焦点","NVDA","VoiceOver","屏幕阅读器","aria","skip-link","alt","heading"]},20,None),
    # ===== 新领域: 数据测试 (60-61) =====
    (60,"data","数据测试基础：ETL验证","理解数据管道中QA的角色——验证数据完整性和正确性",
     "**ETL(Extract-Transform-Load)测试**是数据工程中最关键的QA环节。数据从源系统抽取→转换→加载到数仓的过程中，任何一步出错都会导致决策错误。\n\n**核心验证点：** ①行数校验(源=目标)、②数据完整性(无截断/无null异常)、③转换逻辑(公式/聚合是否正确)、④增量vs全量(第二次ETL是否正确处理重复数据)、⑤边界值(空值/极大值/特殊字符)。",
     None,
     "quiz",{"question":"ETL测试中最容易被忽略的检查是哪一项？","options":["A. 总行数是否一致","B. 字段映射是否正确","C. 增量加载的去重逻辑——同一批数据跑两次ETL不应产生重复记录","D. 日期格式是否正确"],"correct_index":2,"explanation":"增量加载的去重/幂等性是最常见的ETL Bug——第二次运行ETL时，已存在的数据应该被更新(Upsert)而非重复插入，否则导致报表翻倍。A/B/D都可以用自动脚本验证，C需要理解业务逻辑。"},20,None),
    (61,"data","测试数据管理：生成、脱敏与清理","学会用Faker生成测试数据、脱敏生产数据、清理测试残留",
     "**测试数据三大难题：** ①生成——需要大量真实感数据但手动造太慢；②脱敏——从生产环境拷贝数据时必须移除PII（个人身份信息）；③清理——测试后残留数据导致下次测试失败（非唯一约束冲突）。\n\n**解决方案：** 使用Faker库生成1000条用户数据只需3行代码；生产数据脱敏用正则替换(email→hash、手机号→随机号)；测试后自动执行cleanup脚本删除测试数据。",
     None,
     "code",{"checks":["Faker|faker","fake.","seed|add_provider","def test","clean|delete|truncate"],"test_input":"","expected":""},25,None),
    # ===== 混沌工程 (62-64) =====
    (62,"chaos","混沌工程入门：什么是Chaos Engineering","理解混沌工程的核心概念和五大原则",
     "**混沌工程(Chaos Engineering)**是在分布式系统上进行有控制实验，以建立对系统抵御生产环境动荡能力的信心。Netflix于2011年首创Chaos Monkey——随机终止生产实例来验证系统弹性。\n\n**五大原则：**\n1. **定义稳态假设**——正常时系统行为是什么？(如p99延迟<200ms)\n2. **多样化真实事件**——模拟真实故障(CPU飙升/网络延迟/磁盘满)\n3. **在生产环境实验**——测试环境无法模拟真实流量和配置\n4. **自动化持续运行**——不是一次性活动，而是持续验证\n5. **最小化爆炸半径**——先影响1%流量，确认安全再扩大\n\nQA在混沌工程中的角色：设计实验假设、验证监控告警是否触发、评估爆炸半径控制是否有效。",
     None,
     "quiz",{"question":"混沌工程的核心目的是什么？","options":["A.随机破坏系统以测试运维反应速度","B.通过有控制的实验验证系统的弹性和容错能力","C.替代所有传统测试方法","D.只在测试环境中运行故障模拟"],"correct_index":1,"explanation":"混沌工程不是随机破坏，而是科学实验——定义假设→注入故障→观察行为→验证稳态→学习改进。Netflix的经验证明这是一种高效的韧性验证方法。"},15,None),
    (63,"chaos","故障注入实验设计","学习设计CPU、内存、网络、磁盘等多维度故障注入实验",
     "**故障注入(Fault Injection)**是混沌工程的核心手段。\n\n**常见注入类型：**\n- **CPU压力：** 消耗CPU资源至80%/95%，观察服务降级和限流行为\n- **内存压力：** 填充内存至接近OOM，验证OOM Killer行为和优雅降级\n- **网络故障：** 延迟注入(100ms/500ms/2s)、丢包率(1%/10%/50%)、DNS故障\n- **磁盘故障：** 磁盘满(95%+)、IO Hang、只读文件系统\n- **进程故障：** Kill关键进程、SIGSTOP暂停、SIGKILL强杀\n\n**实验设计模板：** 稳态假设(正常指标) + 故障类型 + 爆炸半径(影响范围) + 回滚条件(何时停止) + 预期结果 = 完整实验。",
     "设计一个验证Order Service弹性的混沌实验。微服务链: API Gateway → Order Service → Payment Service → DB。稳态假设：p99延迟<200ms，错误率<0.1%。写出实验假设、爆炸半径和回滚条件。",
     "explore",{"keywords":["稳态","Order Service","p99","延迟","故障","回滚","爆炸半径","假设","观察","恢复","监控","告警"]},20,None),
    (64,"chaos","GameDay与混沌工程文化","理解故障演练日的组织方式和团队文化变革",
     "**GameDay(故障演练日)**是定期组织的混沌工程实战活动——全团队(开发/测试/运维/产品)在预定时间内集中执行故障注入实验。\n\n**GameDay流程：**\n1. 提前1-2周公布时间和范围(不公布具体故障类型)\n2. 团队齐聚「作战室」\n3. 按优先级逐一执行实验: 注入故障→观察系统→验证监控→必要时回滚→记录发现\n4. 事后复盘：什么意外发生了？什么没发生但我们担心的？学到的最重要一课是什么？\n\n**组织文化是最大挑战：** Netflix经验表明，文化阻力比技术挑战大10倍——很多人本能反对在生产环境注入故障。QA需要推动一种「把失败当作学习机会」的文化。",
     None,
     "scenario",{
         "question":"你的团队第一次组织GameDay。CTO说'这太危险了，万一真的搞挂生产怎么办？'作为QA Lead，你怎么回应？",
         "options":[
             "A. 让步——先在测试环境做GameDay，以后再说生产",
             "B. 先解释爆炸半径控制（0.1%流量、监控告警联动、即时回滚）+ 提议先在测试环境跑一次让团队建立信心",
             "C. 放弃——CTO不支持就不要强推",
             "D. 找Netflix/Amazon的案例强行说服——顶级公司都这么做"
         ],
         "correct_index":1,
         "explanation":"B是正确做法。先教育(爆炸半径/回滚/监控安全网)→再渐进(测试环境先建立信心)→逐步推进到生产。Cultural change is incremental——领导者需要看到安全网才会放心。",
         "option_analysis":[
             "只在测试环境做GameDay无法验证生产环境的真实行为——网络拓扑、数据量级、用户行为模式完全不同。但作为第一步建立信心是可行的。",
             "正确！渐进式推进：Step 1在测试环境建立信心 → Step 2按0.1%→1%→10%流量在生产推进 → Step 3成为团队常规活动。重点展示安全网(监控+回滚+爆炸半径)让CTO放心。",
             "放弃是最差选项。混沌工程的价值已被大量实践验证。但需要找到适合自己组织的推进方式——不是不做，是做得聪明。",
             "成功案例有说服力但不是核心。CTO要的不是'别人做了'而是'我们做安全吗'。展示你们的安全网设计比讲案例更有效。"
         ]
     },30,None),
    # ===== 视觉回归测试 (65-66) =====
    (65,"visual","视觉回归测试入门","理解像素级diff、布局快照对比和视觉测试的必要性",
     "**视觉回归测试(Visual Regression Testing)**捕获UI的视觉快照并与基线对比，检测任何意外的视觉变化。功能测试验证'是否工作'，视觉测试验证'是否好看'。\n\n**常见工具链：**\n- **Percy** — SaaS平台，自动截屏+diff+审批流程\n- **Chromatic** — Storybook生态，组件级视觉测试\n- **BackstopJS** — 开源，Puppeteer截图+对比+报告\n- **Loki** — Storybook + Docker简单diff方案\n\n**何时需要视觉测试？**\n1. 组件库/设计系统——任何CSS变更都可能影响数十个组件\n2. 多浏览器兼容性——Chrome/Firefox/Safari渲染差异\n3. 响应式布局——不同断点下的布局完整性\n4. CSS重构后回归——确保重构前后视觉效果一致\n5. 品牌页面——首页/营销页/落地页的视觉一致性",
     None,
     "quiz",{"question":"视觉回归测试和传统功能测试的核心区别是什么？","options":["A.没有本质区别——都是自动化测试","B.功能测试验证行为正确性，视觉测试验证UI外观一致性——两者互补","C.视觉测试可以替代所有功能测试","D.视觉测试只在设计阶段有用"],"correct_index":1,"explanation":"功能测试验证'点击按钮后提交成功'，视觉测试验证'按钮没有位移/颜色没有意外变化/新旧版本看起来一样'。两者是互补关系——都需要。"},15,None),
    (66,"visual","视觉差异分类与判定","学习识别和分类视觉差异——真Bug vs 可接受的差异 vs 误报",
     "**视觉测试最大挑战：误报(False Positive)。** 1px的抗锯齿差异可能触发diff——但人眼看不出。QA的核心价值是判断哪些差异是真Bug。\n\n**差异严重度分类：**\n- P0-布局破坏：元素重叠、错位、溢出屏幕——阻塞发布\n- P1-元素缺失：按钮/文字/图标消失——高优先级\n- P2-样式漂移：颜色轻微变化、字体不同、间距微调——需评估\n- P3-渲染差异：不同OS/GPU的抗锯齿差异——通常可忽略\n\n**判定流程：**\n1. 自动diff检测到变化 → 2.人工Review(真Bug or 可接受变化？) → 3.更新基线(Accept)或报告Bug(Reject) → 4.将已知误报加入忽略规则\n\n关键原则：**视觉测试的目的是减少人工review成本，不是完全消除人工review。**",
     None,
     "explore",{"keywords":["diff","基线","误报","抗锯齿","布局","颜色","Percy","快照","像素","阈值","分类","Accept","Reject"]},20,None),
    # ===== 毕业考核 (99) =====
    (99,"advanced","🏆 毕业考核：发布就绪评估","作为QA Lead综合所有领域知识，做出Go/No-Go发布决策",
     "**恭喜你完成了所有学习关卡！**\n\n这是毕业考核——你需要作为QA Lead，综合运用14个领域的知识，对一个真实场景做出发布决策判断。\n\n**场景：** 你是电商平台'ShopFast'的QA Lead。团队计划明天发布v3.0版本——这是一个包含新支付方式、UI改版和性能优化的大版本。\n\n**你的职责是：** 评估各领域测试结果，识别风险，量化影响，给出Go/No-Go建议。\n\n记住：**QA不只是找Bug的人，更是质量决策的顾问。** 你的判断直接影响数百万用户的体验和公司收入。",
     "# ShopFast v3.0 各领域测试结果汇总\n\n## 1. 功能测试\n- 120个用例，自动化通过率94%\n- 6个失败用例：3个环境不稳定(重跑通过)，3个真Bug\n- **Bug #1201 (P1):** 订单详情页偶发加载超时(1/20概率)。根因：支付回调接口超时3s\n- **Bug #1202 (P2):** 用户头像上传后预览不更新。根因：缓存未失效\n- **Bug #1203 (P3):** 搜索建议下拉在移动端偶尔显示不全\n\n## 2. 性能测试\n- 首页 p95 延迟 2.1s (目标 < 2s) 未达标\n- 商品列表接口 p99 延迟 890ms\n- 支付接口 p95 延迟 1.2s (目标 < 1s) 未达标\n\n## 3. 安全扫描\n- OWASP ZAP 扫描无 High/Critical 发现\n- 2个 Medium：缺少 X-Frame-Options、CSP 无 nonce\n- 1个 Low：Cookie 未设 SameSite\n\n## 4. 无障碍审计\n- Lighthouse a11y 分数 72/100\n- 主要问题：搜索框无 label 关联、购物车图标无 aria-label\n- 均已记录 Jira，计划下版本修复\n\n## 5. 生产监控（v2.9 过去 7 天）\n- 错误率 0.05%，p99 延迟稳定\n- 数据库慢查询 Top 1 已优化\n\n## 6. 测试覆盖率\n- 后端单元测试 82%，前端组件测试 61%\n- E2E 覆盖支付/下单/登录三条核心链路",
     "scenario",{
         "question":"作为QA Lead，你的发布建议是什么？",
         "options":[
             "A. No-Go —— Bug #1201 涉及支付(P1)、首页性能不达标、前端测试覆盖率低——三个问题叠加不应发布",
             "B. Conditional Go —— Bug #1201 加降级方案(超时展示缓存订单)+监控告警。性能问题已记录下版本。安全 Medium 不阻塞。附带完整风险说明和监控要求。",
             "C. Go —— 小问题不阻塞发布。94%自动化通过率、无安全Critical发现、核心链路E2E覆盖——质量已经足够",
             "D. 推迟决策到明天 —— 需要更多时间跑完整回归确认"
         ],
         "correct_index":1,
         "explanation":"B是QA Leader的专业判断。核心理由：Bug #1201偶发(5%)且有workaround(刷新恢复)加降级方案——风险可控不阻塞；首页p95差0.1s不是严重退化且已记录——不影响核心功能；安全无Critical、a11y有计划——不构成阻塞条件。QA的职责是给出专业风险评估和建议——不是追求零风险(不现实)也不是草率放行。Conditional Go = 可以发布但必须附带条件和监控。",
         "option_analysis":[
             "P1偶发Bug+轻度性能退化不应自动阻止发布。需要评估实际用户影响：5%支付场景延迟=多少用户受影响？有降级方案吗？修复成本+回归时间 vs 延期成本？不做量化分析就直接No-Go不是专业QA的判断。",
             "正确！Conditional Go体现QA从'质量警察'到'质量顾问'的转变。附带条件：监控P1 Bug发生率并准备回滚、支付超时降级方案已部署、首页性能下版本设具体目标、安全Medium和a11y有Jira跟踪。",
             "只看表面数字(94%通过率)不做风险分析是危险的。QA的责任不是回避风险，而是主动识别、量化并建议缓解措施。",
             "推迟不解决任何问题——明天还是同样的数据。如果推迟是为了做更多测试，应该明确要测什么、为什么今天没测、测完后决策标准是什么。否则就是犹豫不决——这不是QA Leader该有的表现。"
         ]
     },50,None),
    # ===== 风险驱动测试 (67-69) =====
    (67,"risk","风险识别与评估：FMEA入门","学会用FMEA方法识别软件风险并计算风险优先级数",
     "**风险(Risk)** = 发生概率(Probability) × 影响程度(Impact)。QA的核心职责之一就是在有限的时间和资源下，优先测试风险最高的部分。\n\n**FMEA(Failure Mode and Effects Analysis)**起源于航天和汽车工业，现在被广泛应用于软件测试：\n1. **识别失效模式**——这个功能可能以什么方式失败？\n2. **评估影响**——失败会造成什么后果？（1-10分）\n3. **评估概率**——失败发生的可能性多大？（1-10分）\n4. **评估可检测性**——现有测试能多容易发现这个失败？（1-10分）\n5. **计算RPN** = 影响 × 概率 × 可检测性。RPN越高越优先测试。\n\n**案例分析：** 电商支付功能——失效模式：多扣用户款。影响=10(重大财务+法律风险)，概率=2(少见)，可检测性=3(容易发现)。RPN=60。vs 失效模式：UI加载慢。影响=3，概率=7，可检测性=5。RPN=105。说明高概率低影响的问题可能比低概率高影响的问题更值得优先测试！",
     None,
     "quiz",{"question":"关于FMEA的RPN（风险优先级数），以下哪个说法是正确的？","options":["A. RPN越低越优先测试","B. RPN = 影响程度 × 发生概率 × 可检测性，数字越高越优先测试","C. RPN只取决于影响程度，概率和可检测性不重要","D. FMEA只能用于硬件，不能用于软件"],"correct_index":1,"explanation":"RPN帮助QA量化风险优先级。关键洞察：一个高概率中等影响的问题（如UI加载慢影响10%用户）可能比低概率高影响的问题（如多扣款影响0.01%交易）更值得优先投入测试资源。"},20,None),
    (68,"risk","风险驱动测试策略","学会在有限时间和资源下，根据风险优先级分配测试投入",
     "**核心问题：** 你永远没有足够的时间和资源测试所有东西。风险驱动测试就是：用系统化的方法决定「测什么、测多深、不测什么」。\n\n**四象限风险矩阵：**\n- 🔴 高概率高影响 → 深度测试（自动化+探索+性能+安全）\n- 🟠 高概率低影响 → 适度测试（自动化+抽样探索）\n- 🟡 低概率高影响 → 针对性测试（故障注入+场景演练）\n- 🟢 低概率低影响 → 轻量检查（Smoke test或跳过）\n\n**测试预算分配原则：** 不是平均分配——而是按风险比例分配。如果支付模块贡献了30%的业务风险，它就应该获得30%的测试预算。\n\n你的任务：一个电商App的5个模块各有不同的风险特征。你有40人·时的测试预算。如何分配？",
     "一个电商App有5个模块：①用户登录(低概率高影响——账户被盗)、②商品搜索(高概率低影响——搜索结果不准确)、③购物车(高概率高影响——加购失败导致流失)、④支付(低概率高影响——财务风险)、⑤订单历史(低概率低影响——展示错误)。你只有40人·时测试预算。请说明你的分配方案和理由——每个模块分配多少时间？测什么？为什么？",
     "explore",{"keywords":["风险","概率","影响","分配","购物车","支付","测试预算","优先级","登录","搜索","订单","40人时","自动化","探索"]},25,None),
    (69,"risk","Go/No-Go：基于风险的发布决策","综合风险分析做出专业发布建议——这是QA Lead的核心职责",
     "**场景：** 你是FinTech产品'PayFast'的QA Lead。明天是v2.0发布窗口。CEO希望按时发布（市场部门已通知用户），但你需要基于风险做出独立判断。\n\n**风险登记册(Risk Register)：**\n1. [P=3% I=Critical] 新支付网关在极端并发下偶发超时——风险：用户被重复扣款\n2. [P=8% I=High] 新UI在旧版Android(API<26)上布局错位——风险：5%用户无法完成下单\n3. [P=25% I=Medium] 搜索索引重建可能导致搜索结果不完整——风险：用户体验下降\n4. [P=1% I=Critical] 数据库迁移脚本在特定条件下可能死锁——风险：服务中断\n5. [P=60% I=Low] 新功能的通知文案未翻译——风险：非中文用户看到空白\n\n每个风险都有缓解措施和回滚方案。你的任务：做出Go/No-Go/Conditional Go建议，附完整推理。",
     None,
     "scenario",{
         "question":"作为QA Lead，基于以上风险登记册，你的发布建议是什么？",
         "options":[
             "A. No-Go——风险#4(数据库死锁)和#1(支付超时)都是Critical影响，任何可能导致资金损失或服务中断的风险都不应发布",
             "B. Conditional Go——风险#1已有自动回滚+告警(发生概率仅3%)；风险#4死锁条件已知且已设监控告警+备有快速回滚方案。风险#2仅影响5%旧版用户且有降级方案。但必须：①监控面板就位②回滚手册已演练③所有on-call到位",
             "C. Go——概率都很低，影响可控。CEO和市场需要按时发布——不要成为瓶颈",
             "D. 推迟决策——需要再做一轮完整回归确认"
         ],
         "correct_index":1,
         "explanation":"B是QA Leader的专业风险判断。核心理由：(1)两个Critical风险都有具体的缓解措施和回滚方案——不是裸奔；(2)发生概率极低(3%和1%)且触发条件已知；(3)Conditional Go的精髓是'可以发布但必须满足条件'——不是盲目放行。A不考虑缓解措施(任何系统都有残余风险)。C忽视QA专业职责(不是瓶颈而是质量顾问)。D没有给出判断(明天还是同样的数据)。",
         "option_analysis":[
             "追求零风险是不现实的——任何系统都有残余风险。当Critical风险已有缓解+回滚方案且发生概率极低时，不应自动No-Go。关键是评估'有缓解的风险'vs'无缓解的风险'。",
             "正确！Conditional Go体现QA从'质量警察'到'风险顾问'的转变。条件：监控到位、回滚已演练、on-call就位。这些条件将残余风险的预期影响降到可接受水平。",
             "QA不是瓶颈——但QA有独立的质量判断职责。当CEO和市场压力要求Go时，QA的专业价值恰恰是冷静地评估风险并给出有条件的建议——而不是放弃判断。",
             "推迟不解决任何分析性问题——如果推迟是为了缓解风险#4或加强监控，那应该明确说。否则就是犹豫不决。QA Leader需要敢于在不确定性中做判断。"
         ]
     },30,None),
    # ===== 质量度量与分析 (70-73) =====
    (70,"metrics","质量度量基础：DORA指标体系","理解DevOps时代最重要的四个质量度量指标",
     "**DORA(DevOps Research and Assessment)**定义了四个衡量软件交付效能的关键指标。这已成为全球科技公司的标准度量框架。\n\n**四个DORA指标：**\n1. **部署频率(Deployment Frequency)**——多久部署一次？精英团队：每天多次。\n2. **变更前置时间(Lead Time for Changes)**——代码提交到上线要多久？精英团队：<1小时。\n3. **平均恢复时间(MTTR)**——发生故障后多久恢复？精英团队：<1小时。\n4. **变更失败率(Change Failure Rate)**——部署中有多少比例导致故障？精英团队：<5%。\n\n**为什么QA需要关注DORA？** DORA指标将QA从'找Bug的人'升级为'交付效能的关键贡献者'——MTTR和变更失败率直接反映测试质量。\n\n**与其他指标的关系：**\n- 测试覆盖率↑ → 变更失败率↓(但边际递减)\n- 自动化率↑ → 部署频率↑\n- 监控完善度↑ → MTTR↓\n- 代码审查+QA sign-off → 变更失败率↓\n",
     None,
     "analyze",{"data_block":"某团队过去6个月的DORA指标趋势：\n| 月份 | 部署频率(次/周) | 变更前置时间 | MTTR(分钟) | 变更失败率 |\n|------|----------------|-------------|-----------|----------|\n| Jan  | 1 | 6天 | 180 | 18% |\n| Feb  | 1.5 | 5天 | 150 | 15% |\n| Mar  | 2 | 3天 | 120 | 12% |\n| Apr  | 3 | 2天 | 90 | 10% |\n| May  | 5 | 1天 | 45 | 7% |\n| Jun  | 7 | 4小时 | 15 | 3% |","question":"分析这个团队的DORA指标趋势。哪个指标最先表现出改善？哪个改善最慢？这反映了什么测试策略变化？","options":["A. 部署频率改善最快——团队从周部署升级到日部署，说明CI/CD基础设施改善","B. MTTR改善最显著——从180分钟降到15分钟，说明监控和告警能力大幅提升","C. 变更失败率改善最慢——从18%到3%是6个月的渐进改善，说明测试质量提升是逐步积累的，不能一蹴而就","D. 所有四个指标同步改善——说明团队进行了系统性的DevOps转型"],"correct_index":2,"explanation":"变更失败率从18%降到3%用了6个月——这是最慢但最重要的改善。部署频率和前置时间可以通过工具自动化快速提升（第1-2个月就看到效果），MTTR可以通过部署监控快速改善。但降低变更失败率需要：提高测试覆盖率、改进代码审查、积累测试用例——这些都是逐步积累的，没有捷径。"},20,None),
    (71,"metrics","构建QA仪表板：选择正确的度量","学会选择对决策者最有价值的3-5个核心指标",
     "**不是所有度量都有用——很多度量是虚荣指标(Vanity Metrics)。**\n\n**坏度量(应避免)：**\n- 测试用例总数——多不代表质量好\n- 代码覆盖率单独使用——100%覆盖率可以没有断言\n- Bug数量——取决于发现的努力程度，越多可能说明测试越深入\n\n**好度量(GOOD Metrics)：**\n- G: Graded(有分级的——不只是数字，有绿/黄/红阈值)\n- O: Owned(有责任人——每个指标有人负责改善)\n- O: Outcome-based(结果导向——关联业务结果，不只是测试产出)\n- D: Decision-driven(驱动决策——看到数字后知道该做什么)\n\n**推荐QA仪表板5核心指标：** ①生产缺陷逃逸率(上周发布了10个Bug，客户发现了2个=逃逸率20%) ②自动化通过率趋势 ③P0/P1 Bug平均修复时间 ④测试环境可用率 ⑤发布后7天内回滚率\n\n**构建原则：** 控制台给执行层看（10-20个详细指标）→ 仪表板给管理层看（5-8个趋势指标）→ 报告给高管看（1-3个关键数字+一句话解读）",
     "你刚加入一个中型SaaS团队。CEO抱怨'QA部门到底做了什么？'——因为上周生产环境出了两次故障。CTO让你建立一个QA仪表板来展示QA的价值。你从以下数据中选出3个最应该展示的指标并解释你的选择：①测试用例数(5000+)②上月发现的Bug数(287)③生产缺陷逃逸率(12%，行业平均8%)④代码覆盖率(78%)⑤自动化通过率趋势(93%→96%上升中)⑥MTTR(从45min降到15min)⑦P0 Bug平均修复时间(4小时)",
     "explore",{"keywords":["仪表板","度量","逃逸率","MTTR","自动化","覆盖率","Bug","DORA","指标","决策"]},25,None),
    (72,"metrics","MTTR/MTTD与事件分析","区分检测时间和恢复时间——诊断不同的问题需要不同的解决方案",
     "**MTTD(Mean Time to Detect)和MTTR(Mean Time to Resolve)**是两个常被混淆但本质不同的指标。\n\n**区分MTTD/MTTR的重要性：**\n- MTTD高 = 监控/告警/可观测性差 —— 需要投资监控\n- MTTR高 = 故障响应/诊断/恢复流程差 —— 需要投资Runbook和自动化恢复\n\n**三个事件分析案例：**\n\n**事件A：** 检测时间2分钟（告警自动触发），恢复时间15分钟（值班工程师按Runbook重启服务即可）。分析：MTTD优秀，MTTR可接受。\n\n**事件B：** 检测时间6小时（用户反馈才知道），恢复时间30分钟（重启解决）。分析：MTTD极差——6小时盲区说明监控缺失。投资监控比优化恢复流程更重要。\n\n**事件C：** 检测时间5分钟（告警触发），恢复时间3天（复杂数据修复+人工验证）。分析：MTTD优秀，但MTTR极差——需要投资自动化恢复或优化恢复流程。\n\n**关键洞察：** 同样造成'用户受影响'，但根因完全不同——A是运维常态(可接受)、B需要监控投资、C需要流程/自动化投资。不能只看'出了故障'。",
     None,
     "analyze",{"data_block":"过去一个月生产环境的4个事件：\n| 事件 | MTTD | MTTR | 用户影响 | 根因 |\n|------|------|------|---------|------|\n| #101 | 2min | 15min | 500用户 | 内存泄漏导致OOM，重启恢复 |\n| #102 | 8hr | 20min | 12000用户 | 第三方API凭证过期，更新凭证恢复 |\n| #103 | 3min | 4hr | 300用户 | 数据库死锁，需要DBA手动kill会话 |\n| #104 | 30min | 45min | 8000用户 | 新部署的代码有bug，回滚恢复 |\n\n请判断哪个事件暴露了最严重的过程缺陷，应该优先投入改进资源。","question":"分析这4个事件。哪个事件暴露了最严重的过程缺陷，最应该优先投入改进资源？","options":["A. 事件#101——内存泄漏是代码质量问题，应该加强代码审查和静态分析","B. 事件#102——MTTD 8小时是不可接受的。第三方凭证过期应该有提前告警","C. 事件#103——MTTR 4小时说明故障恢复能力差。数据库死锁应该有自动检测和kill机制","D. 事件#104——新部署导致的问题说明测试和发布流程有缺陷，这是最大的过程问题"],"correct_index":1,"explanation":"事件#102的8小时MTTD是最严重的问题——不是故障本身(20分钟就修复了)，而是8小时没人知道出问题了。这说明：①凭证过期监控缺失 ②12000用户在8小时内受影响——如果提前1个月设置凭证到期告警，这个事件完全可以避免。其他事件：A需要代码质量改善(正常优先级)、C需要自动化死锁处理(重要但较复杂)、D回滚流程已经工作(45分钟内恢复了，过程基本正常)。"},20,None),
    (73,"metrics","测试ROI与质量经济学","学会计算测试的投资回报率——用业务语言说服决策者",
     "**质量成本(CoQ: Cost of Quality)分为四类：**\n\n**1. 预防成本(Prevention)：** 培训、设计审查、代码审查、测试策略规划——花在'防止Bug出现'上的钱\n**2. 检测成本(Appraisal)：** 测试执行、代码分析、测试环境维护——花在'发现Bug'上的钱\n**3. 内部失败成本：** Bug在发布前被发现——修复+回归测试\n**4. 外部失败成本：** Bug在发布后被用户发现——修复+客服+赔偿+声誉+用户流失\n\n**1:10:100规则：** 在需求阶段修复一个Bug需要1元，在开发阶段需要10元，在测试阶段需要100元，在生产阶段需要1000元。\n\n**QA的ROI计算：** 如果QA团队年薪100万，自动化测试投入50万，但减少了70%的生产缺陷（假设每个生产缺陷平均造成5万元损失，去年50个生产缺陷=250万损失，今年只要15个=75万损失），那么QA投入150万节省了175万——ROI=117%。\n\n**但注意：** ROI不是QA证明自己的唯一方式。有些QA价值无法量化——比如避免了一场潜在的品牌危机。",
     None,
     "scenario",{
         "question":"公司VP提出：'QA团队花了公司总研发预算的25%。如果我们把QA砍掉一半，把省下的钱给开发团队，让他们自己保证质量，是不是更高效？'作为QA Lead，你怎么回应？",
         "options":[
             "A. 展示QA的ROI数据——去年QA投入150万，但通过预防和早期发现避免了至少250万的生产缺陷损失。净节省100万",
             "B. 先认可VP的成本关注，然后展示数据(ROI)+讲一个案例(上季度QA在发布前拦截了一个可能导致数据丢失的P0 Bug)+提出试点(选一个非核心模块让开发自测3个月，对比缺陷逃逸率)",
             "C. 强烈反对——没有专业QA团队质量必然崩溃。列举Facebook/Google都有QA团队",
             "D. 妥协——砍掉20%的QA做试点，看看效果",
             "A. 先在测试环境做GameDay，以后再说生产","B. 展示QA的ROI数据——去年QA投入150万，通过预防和早期发现避免了至少250万的生产缺陷损失。净节省100万","C. 强烈反对——没有专业QA团队质量必然崩溃","D. 妥协——砍掉QA做试点看看效果"
         ],
         "correct_index":1,
         "explanation":"B是QA Leader应对预算挑战的正确姿势。理由：(1)先认可VP的成本关注——你不是在保护自己的地盘，而是在帮VP做更好的成本决策 (2)数据+案例+试点三步法——用逻辑(ROI数据)、情感(数据丢失案例)、和行动(试点)构建完整的论证 (3)试点是杀手锏——让数据说话，如果开发自测后缺陷逃逸率翻倍，VP自己会收回提议。A只讲数字太冷。C只防守没有建设性。D太被动缺乏领导力。",
         "option_analysis":[
             "只用ROI数据不够——VP看到的可能只是'你找了数字证明自己'。需要结合案例(情感诉求)和行动建议(试点)才能构建完整的论证。",
             "正确！三合一论证：①数据(ROI)证明QA的价值是可以用业务语言量化的 ②案例(数据丢失Bug)让VP感受到QA的不可替代性 ③试点(开发自测对比)把决策权还给数据——如果开发自测质量一样好，你应该拥抱这个结果。",
             "纯粹防守姿态——VP听到的是'你在保护自己的地盘'而不是'你在帮公司做更好的决策'。大公司的案例容易被反驳'他们业务和规模不同'。",
             "被动妥协不是领导力。如果试点后发现质量下降再找VP说'我早说了'——你已经失去了先机和信任。主动提出试点作为论证的一部分(B方案)才是正确的。"
         ]
     },30,None),
    # ===== 测试自动化架构 (74-77) =====
    (74,"automation-arch","自动化框架设计：POM与Screenplay模式","深入理解Page Object Model、Screenplay Pattern和Keyword-Driven三种主流框架设计模式",
     "**测试自动化架构**不只是写脚本——是设计可维护、可扩展、可复用的测试框架。\n\n**三大设计模式：**\n\n1. **Page Object Model (POM)**：每个页面一个类，封装页面元素和操作。`class LoginPage: def enter_username(self, name): ...`。优点：易学易用，社区支持广泛。缺点：页面对象膨胀（一个复杂页面可能有50+方法）。\n\n2. **Screenplay Pattern**：演员(Actor)→任务(Task)→能力(Ability)→问题(Question)。`actor.attemptsTo(Login.withCredentials(user, pass)).then(actor.should(seeThat(LoginStatus.isSuccessful())))`。优点：SOLID原则友好，适合复杂业务流程。缺点：学习曲线陡峭。\n\n3. **Keyword-Driven Framework**：用表格驱动测试——非技术人员也能编写自动化测试。优点：业务人员参与。缺点：维护关键词库成本高。\n\n**反模式：** 录制-回放（Record & Playback）——录制生成的脚本没有抽象层，页面一改全部报废。\n\n**选择指南：** 小型项目→POM，复杂业务流程→Screenplay，需要业务人员参与→Keyword-Driven。",
     None,
     "quiz",{"question":"关于Page Object Model(POM)和Screenplay Pattern的区别，以下哪个说法是正确的？","options":["A. POM总是比Screenplay更好，应该始终使用POM","B. POM以页面为中心组织代码，Screenplay以用户任务为中心组织代码——Screenplay更适合复杂业务流程但也更复杂","C. Screenplay Pattern已经过时了，2016年后不再使用","D. 两者完全相同，只是名字不同"],"correct_index":1,"explanation":"POM适合页面结构稳定的场景——简单直观。但当业务流程跨越多个页面（如'登录→搜索→加入购物车→结账'），Screenplay的任务驱动模型让代码更清晰、更易维护。选择取决于系统复杂度和团队技能。"},20,None),
    (75,"automation-arch","BDD与Gherkin：从需求到可执行规范","用Given/When/Then编写可执行的需求规范并实现步骤定义",
     "**BDD(Behavior-Driven Development)**是一种协作实践，不是测试技术。核心思想：用自然语言描述系统行为，让开发、测试和业务人员都能理解，然后变成可执行的验证代码。\n\n**Gherkin语法：**\n```gherkin\nFeature: 用户登录\n  Scenario: 使用有效凭证登录\n    Given 用户在登录页面\n    When 输入用户名\"demo\"和密码\"secret\"\n    And 点击登录按钮\n    Then 跳转到主页\n    And 显示欢迎消息\n```\n\n**Python实现（behave库）：**\n```python\nfrom behave import given, when, then\n@given('用户在登录页面')\ndef step_impl(context): context.driver.get('/login')\n@when('输入用户名\"{user}\"和密码\"{pwd}\"')\ndef step_impl(context, user, pwd): ...\n```\n\n**关键：** BDD的价值是协作——需求用Gherkin写出来，业务人员能Review，测试人员能自动化。但不要为了BDD而BDD——确认团队真的需要这种协作方式。",
     "# 编写一个登录功能的.feature文件和对应的step definitions\n# 场景: 使用无效密码登录应显示错误消息\n# 要求: Feature文件包含Given/When/Then, step definitions用Python behave库风格实现",
     "code",{"checks":["Feature","Scenario","Given","When","Then","behave|context","def step"],"test_input":"","expected":""},25,None),
    (76,"automation-arch","测试数据工厂与数据独立性","学会使用工厂模式和Builder模式创建独立、真实、可复用的测试数据",
     "**测试数据三大问题：** ①硬编码——测试依赖特定数据库记录，换环境就挂 ②共享数据——多个测试用一个用户，改密码导致其他测试失败 ③数据泄漏——测试数据残留影响后续测试。\n\n**解决方案——数据工厂模式：**\n```python\n# factory_boy 风格\nclass UserFactory(factory.Factory):\n    class Meta: model = User\n    username = factory.Faker('user_name')\n    email = factory.Faker('email')\n    age = factory.Faker('random_int', min=18, max=80)\n\n# 每个测试创建自己的数据\ndef test_user_update():\n    user = UserFactory()  # 全新独立的数据\n    result = update_profile(user.id, {'age': 30})\n    assert result.age == 30\n```\n\n**关键原则：** ①每个测试创建自己需要的数据（数据独立性）②使用Faker生成随机但真实的数据（而非test1/test2/test3）③测试后清理（或使用事务回滚）④工厂支持覆盖——`UserFactory(age=25)`可以覆盖默认值。",
     "# 实现一个简单的测试数据工厂\n# 要求: 定义一个create_user()函数, 用Faker生成username/email/age\n# 然后写一个参数化测试函数, 测试不同age值的验证逻辑\n# 提示: from faker import Faker; fake = Faker()",
     "code",{"checks":["def create_user|class.*Factory","Faker|faker","fake\\.","parametrize|for.*in","assert"],"test_input":"","expected":""},25,None),
    (77,"automation-arch","测试并行化与大规模执行策略","决策场景——测试套件从4小时优化到合理时间，面临并行化架构选择",
     "**场景：** 你的团队自动化测试套件包含500个测试：300个UI测试(Selenium WebDriver)，150个API测试，50个单元测试。总共运行时间超过4小时（单机Chrome）。\n\n**需求：** 团队要求每次PR提交后30分钟内得到测试结果。你有预算购买10台云VM。\n\n**并行化挑战：**\n1. **UI测试并行需要多个浏览器实例**——Selenium Grid还是云服务(BrowserStack/Sauce Labs)？Grid省钱但需维护，云服务省心但贵。\n2. **测试隔离问题：** 两个UI测试同时操作同一个测试账号→数据竞争→假失败\n3. **Flaky测试在并行下放大：** 单机通过率95%→并行后可能降到70%（时序问题暴露）\n4. **测试分片策略：** 按文件分？按时间均衡分？上次最慢的5个测试占了40%的时间\n5. **数据库瓶颈：** 所有测试共享一个测试DB→并行更新产生死锁\n\n**你的决策任务：** 设计并行化方案，考虑成本、可靠性、维护复杂度。",
     None,
     "scenario",{
         "question":"你需要在以下方案中做出决策。哪个是最佳的第一步？",
         "options":[
             "A. 直接买10台VM全部跑UI测试并行——最大化并行度，应该能压缩到30分钟以内",
             "B. 先用测试时间数据识别慢测试，分离API测试(快、可独立并行)和UI测试(慢、需浏览器)，然后对UI测试使用Selenium Grid+4节点分片。Flaky测试单独隔离到Quarantine套件并行观察",
             "C. 购买BrowserStack等云服务——最省心，不需要维护Grid",
             "D. 放弃UI测试并行——UI测试太不稳定，只并行API测试和单元测试"
         ],
         "correct_index":1,
         "explanation":"B是正确的工程决策。理由：①分离快慢测试——API测试(150个)只需5分钟可先完成，UI测试(300个)是瓶颈 ②4节点Grid+按时间分片可将300个UI测试从4h降到1h左右 ③Flaky隔离——不要删除Flaky测试（它们仍提供价值），但不要让它阻塞PR。关键是分步骤渐进——而不是一步到位。",
         "option_analysis":[
             "直接10VM全并行看似最快但最危险：没有数据驱动（哪些测试最慢？），没有解决数据竞争，Flaky爆炸——很可能大量假失败导致团队忽略CI结果。",
             "正确！数据驱动优化：①分析时间分布（最慢5个测试占40%时间→优先优化它们）②分层并行（API独立并行+UI分片）③渐进投资（Grid先用4节点→效果好再加）④Flaky管理（隔离不删除）",
             "云服务省维护但：①成本高（10并行×按分钟计费）②网络延迟增加测试时间 ③问题调试困难（看不到浏览器）。不是第一步——先用Grid验证并行可行性和ROI，再考虑云。",
             "放弃UI并行意味着PR反馈时间仍然是4小时——没有解决需求。UI测试是发现回归Bug的主力——不能放弃，需要更聪明地并行。"
         ]
     },30,None),
    # ===== 现代API测试 (78-80) =====
    (78,"advanced-api","gRPC测试：Protocol Buffers与流式调用","学习测试gRPC服务的四种调用模式和ProtoBuf验证",
     "**gRPC**是Google开发的高性能RPC框架，被Netflix、Uber、Square等广泛采用。使用Protocol Buffers(protobuf)作为接口定义语言和消息格式——二进制、强类型、双向流。\n\n**四种调用模式：**\n1. **Unary（一元）**：客户端发一个请求，服务端回一个响应——类似REST\n2. **Server Streaming**：客户端发一个请求，服务端流式回多个响应\n3. **Client Streaming**：客户端流式发多个请求，服务端回一个响应\n4. **Bidirectional Streaming**：双向流——客户端和服务端同时发送消息\n\n**gRPC测试要点：**\n- Proto文件是合约——任何字段变更都要检查向后兼容性\n- 强类型意味着测试更精确——不需要验证JSON结构\n- grpcurl是调试利器（类似curl for gRPC）\n- 超时设置：gRPC默认无超时——必须显式设置deadline\n\n**与REST测试的区别：** REST关注HTTP状态码和JSON schema，gRPC关注gRPC状态码和ProtoBuf消息验证。",
     "# 用Python grpcio库写一个gRPC测试客户端\n# 假设有个UserService的proto定义：\n# service UserService { rpc GetUser(GetUserRequest) returns (User); }\n# message GetUserRequest { int32 user_id = 1; }\n# message User { int32 id = 1; string name = 2; string email = 3; }\n# 请写一个测试函数，调用GetUser并验证返回的User对象含有id/name/email字段",
     "code",{"checks":["grpc|grpcio","UserService|GetUser","stub|channel","assert.*id|assert.*name|assert.*email","def test"],"test_input":"","expected":""},25,None),
    (79,"advanced-api","事件驱动测试：Kafka消息验证","理解事件驱动架构的测试挑战——生产者、消费者、Schema演进和幂等性",
     "**事件驱动架构**中，服务不直接调用API，而是通过事件总线(Kafka/RabbitMQ/SQS)异步通信。这带来全新的测试挑战。\n\n**关键测试点：**\n1. **生产者测试：** 事件是否正确发布到Topic？消息格式是否符合Schema？Header中的trace-id是否正确传递？\n2. **消费者测试：** 消费者是否正确处理事件？重复消息是否导致副作用（幂等性）？消息乱序是否影响业务逻辑？\n3. **Schema演进测试：** 新版本Producer改了字段类型→旧版本Consumer能处理吗？（Avro/ProtoBuf向后兼容性）\n4. **死信队列测试：** 无法处理的消息是否正确进入DLQ？DLQ消息能否重放？\n5. **传递语义测试：** 系统设计是At-most-once还是At-least-once还是Exactly-once？每种语义的测试策略完全不同。\n\n**测试工具：** Testcontainers + Kafka、Spring Kafka Test、kcat命令行。",
     "你负责测试一个订单系统的事件驱动架构。订单服务→Kafka Topic→通知服务。订单服务发布OrderCreated事件(包含order_id/user_id/amount)，通知服务消费后发送邮件。请描述你的测试策略：①如何测试订单服务正确发布了事件？②如何测试通知服务正确处理了事件？③如果事件被重复消费（At-least-once语义），通知服务应该如何设计以保证不会发送两封邮件？",
     "explore",{"keywords":["Topic","Producer","Consumer","Schema","幂等","去重","重复","死信","DLQ","兼容","order_id","事件","消息"]},25,None),
    (80,"advanced-api","OpenAPI合约验证与Schema测试","用OpenAPI Specification做合约测试——确保API实现和文档一致",
     "**OpenAPI Specification(OAS，前Swagger)**不仅生成文档——更是可执行的API合约。\n\n**合约测试三层次：**\n1. **Schema验证：** 实际响应是否符合OpenAPI定义的Schema？字段类型、required、enum、pattern、min/max——全部自动验证。\n2. **属性级约束：** age字段定义为`minimum: 0, maximum: 150`——API返回age: -5应该被Schema验证捕获。\n3. **语义验证：** age: 30通过了Schema验证（类型和范围都对），但用户的实际年龄应该是25——这是Schema无法检测的，需要额外的业务验证。\n\n**测试工具：** Schemathesis(基于属性的API测试——自动生成测试用例)、Dredd(验证API实现和API文档一致)、Prism(API Mock from OpenAPI spec)。\n\n**关键洞察：** Schema验证告诉你的API '语法正确'，语义验证告诉你的API '意思对'——两者都需要。",
     "# 给定下面的OpenAPI 3.0片段，写一个合约验证测试\n# /users/{id}:\n#   get:\n#     parameters:\n#       - name: id\n#         in: path\n#         required: true\n#         schema: { type: integer, minimum: 1 }\n#     responses:\n#       '200':\n#         content:\n#           application/json:\n#             schema:\n#               type: object\n#               required: [id, name, email]\n#               properties:\n#                 id: { type: integer }\n#                 name: { type: string, minLength: 1 }\n#                 email: { type: string, format: email }\n# 请写一个测试函数验证：① id=-1应该返回400(违反minimum=1) ② 正常响应必须包含id/name/email ③ email格式必须合法",
     "code",{"checks":["def test","assert.*400|assert.*status_code","id|name|email","schema|OpenAPI|openapi","valid|validate"],"test_input":"","expected":""},25,None),
    # ===== 合规与受监管行业测试 (81-83) =====
    (81,"compliance","受监管行业测试全景","理解FDA、HIPAA、SOC2、GDPR、PCI-DSS等法规对测试的要求",
     "**受监管行业(Regulated Industries)**有特殊的测试和验证要求——不是'测得好不好'的问题，是'不按要求测就违法'的问题。\n\n**主要法规速览：**\n\n| 法规 | 行业 | 关键测试要求 |\n|------|------|------------|\n| FDA 21 CFR Part 820 | 医疗器械 | 设计验证+可追溯性矩阵+DHF文档 |\n| HIPAA | 医疗数据 | 隐私安全测试+PHI数据保护验证 |\n| SOC2 Type II | SaaS/云服务 | 安全/可用性/机密性控制测试 |\n| GDPR | 欧盟数据 | 数据主体权利测试+删除验证+泄露通知 |\n| PCI-DSS | 支付卡 | 渗透测试+SAQ自评+季度扫描 |\n| GxP/21 CFR Part 11 | 制药 | 电子记录+电子签名+审计追踪+CSV |\n| ISO 26262 | 汽车 | 功能安全完整性等级(ASIL)+MISRA |\n\n**QA在合规中的角色演变：** 传统QA→验证执行者。合规QA→审计证据的生产者和质量体系的守护者。测试不只是为了找Bug——更为了生成可以被审计的证据。",
     None,
     "quiz",{"question":"以下关于受监管行业测试的说法，哪个是正确的？","options":["A. 所有行业的测试方法都一样——ISTQB标准适用所有场景","B. FDA 21 CFR Part 820要求医疗器械测试必须有设计验证和需求可追溯性矩阵——这是审计必需文档","C. GDPR只影响欧洲公司——中国公司不需要遵守","D. 合规测试和普通测试完全一样——只是多一些文档"],"correct_index":1,"explanation":"FDA的Part 820(质量体系法规)明确要求医疗器械制造商建立和维护设计验证程序——每一个需求必须有对应的验证测试，且结果必须文档化。这是审计时首先被检查的内容。QA的工作不仅仅是执行测试，更是生成可被审计的证据。"},20,None),
    (82,"compliance","审计追踪与需求可追溯性","实践构建可审计的需求可追溯性矩阵",
     "**需求可追溯性矩阵(RTM — Requirements Traceability Matrix)**是受监管行业最核心的QA文档。每一行都是一个从需求到测试的完整链条。\n\n**双向可追溯性：**\n- **正向追溯：** 需求 → 设计 → 实现 → 测试用例。确保每个需求都被测试覆盖。\n- **反向追溯：** 测试用例 → 需求。确保每个测试都在验证真实需求（没有'为了测试而测试'）。\n\n**RTM示例（胰岛素泵剂量计算器）：**\n| 需求ID | 需求描述 | 风险等级 | 测试用例ID | 验证方法 | 结果 |\n|--------|---------|---------|-----------|---------|------|\n| REQ-001 | 剂量范围0.1-25.0单位 | High | TC-001 | 边界值测试(0.09/0.1/25.0/25.1) | Pass |\n| REQ-002 | 连续3次给药间隔≥5分钟 | Critical | TC-002 | 时序测试(间隔4分59秒应拦截) | Pass |\n| REQ-003 | 电池电量<10%时报警 | Medium | TC-003 | 状态测试(模拟电池9%/10%/11%) | Pass |\n\n**审计追踪(Audit Trail)：** 谁在什么时候做了什么测试？结果是什么？谁Review的？任何变更都必须有记录——不只是测试结果，更是完整的操作历史。",
     "一个心脏起搏器软件有三项关键需求：①起搏频率范围(30-200 BPM)必须在所有条件下精确控制(误差<1%) ②电池电压低于2.5V时必须切换到安全模式(固定60 BPM) ③软件升级过程中必须持续运行(不允许中断)。请为这三项需求构建一个可追溯性矩阵：为每个需求至少设计2个测试用例、标注风险等级、选择验证方法、说明为什么这些测试用例能被审计。",
     "explore",{"keywords":["可追溯性","矩阵","需求","风险","测试用例","验证方法","审计","边界","安全模式","升级","精确","BPM"]},25,None),
    (83,"compliance","GxP与计算机系统验证(CSV)","作为QA Lead处理制药企业LIMS系统的验证挑战",
     "**GxP(Good Practice)是制药行业的质量规范集合：** GMP(生产)、GLP(实验室)、GCP(临床)、GDP(分销)。计算机系统验证(CSV)是确保用于GxP流程的软件系统符合预期用途的正式过程。\n\n**GAMP 5软件分类：**\n- Category 1: 基础设施(OS/网络)——基本配置管理\n- Category 3: 不可配置软件(COTS)——简单验证\n- Category 4: 可配置软件(Configured)——**最常见的类别，需要最复杂的验证**\n- Category 5: 定制开发软件(Bespoke)——完全验证\n\n**CSV生命周期(基于GAMP 5)：**\n1. 计划(Validation Plan) → 2. 规格(URS/FS/DS) → 3. 测试(IQ安装确认/OQ运行确认/PQ性能确认) → 4. 报告(Validation Report)\n\n**IQ/OQ/PQ概念：**\n- **IQ (Installation Qualification)：** 系统安装正确吗？\n- **OQ (Operational Qualification)：** 系统按规格运行吗？\n- **PQ (Performance Qualification)：** 系统在真实使用场景下工作吗？",
     None,
     "scenario",{
         "question":"你是一家制药公司的QA Lead。公司正在实施一套新的LIMS(实验室信息管理系统)，属于GAMP Category 4(可配置软件)。供应商声称他们的软件'已通过预验证(Pre-validated)'，建议你们只需做最少的验证。但你知道——预验证只覆盖了出厂标准功能，没有覆盖你们的实际配置和使用场景。作为QA Lead，你怎么回应？",
         "options":[
             "A. 接受供应商的预验证包——减少验证成本和时间。如果供应商说已验证，我们应该信任他们",
             "B. 向领导层解释预验证不等于CSV——需要补充IQ/OQ/PQ覆盖实际配置和使用场景。提议：①审核供应商的预验证包(了解覆盖了什么) ②基于差距分析补充验证 ③特别关注配置和接口(最常出问题的地方)——这些预验证通常不覆盖",
             "C. 完全拒绝预验证——从头做完整的CSV，确保万无一失",
             "D. 建议使用SaaS版本避免验证——云服务通常已经通过验证"
         ],
         "correct_index":1,
         "explanation":"B是正确的合规QA判断。理由：①预验证只覆盖了软件出厂时的标准功能——你们的实际配置(工作流、字段、报表、权限)、与现有系统(ERP/MES)的接口、实际使用场景都不在预验证范围内 ②从头做完整CSV浪费了预验证包的价值——可以审核+补充而非替代 ③C过度保守(浪费时间和成本)，A过度信任(暴露合规风险)，D误解了SaaS验证(云基础架构验证≠应用验证)。",
         "option_analysis":[
             "完全接受预验证而不做配置/接口/使用场景的补充验证——这是FDA审计中最常见的发现项(Observation)。预验证包对IQ有帮助，但不能替代OQ/PQ。",
             "正确！实用主义的合规路线：利用预验证包做IQ的基础，但OQ(验证实际配置后的功能)和PQ(验证真实使用场景下的性能)必须自己做。关键是为补充验证的范围提供清晰的理由——这是审计时被审查的重点。",
             "完全拒绝预验证是浪费。好的验证策略应该利用所有可用的证据——只要你能证明预验证数据和你们的使用场景之间的关系。从头做所有事情不增加合规性，只增加成本和时间。",
             "SaaS版本仍然需要验证——云基础设施的SOC2/SOC3报告可以简化IQ但绝不能省略OQ/PQ。此外，制药行业对数据主权(数据存储在哪里？)有严格要求——不是所有SaaS都合适。"
         ]
     },30,None),
    # ===== 薄域补全 (84-89) =====
    (84,"accessibility","自动化无障碍测试管道","用axe-core和Lighthouse CI将无障碍测试集成到CI/CD管道",
     "手动无障碍测试无法规模化——你不可能每次部署前手动检查所有页面。自动化a11y测试管道是唯一可行的规模化方案。\n\n**核心工具链：**\n- **axe-core**：Deque Labs开源的无障碍规则引擎。可以集成到Playwright/Puppeteer/Cypress测试中，自动检测WCAG违规。\n- **Lighthouse CI**：Google的自动化审计工具。可以在CI中设置a11y分数阈值——低于90分则阻止部署。\n- **pa11y**：命令行无障碍测试工具，适合快速扫描。\n\n**管道设计：**\n1. 每次PR → Playwright+axe-core扫描所有核心页面 → 报告a11y违规\n2. CI检查：无Critical/Serious违规 → 合并\n3. Lighthouse CI检查a11y分数≥90 → 部署\n4. 定期全站扫描(每周) → 趋势Dashboard\n\n**关键限制：** 自动化工具只能检测约30-57%的WCAG问题——无法检测键盘导航体验、屏幕阅读器兼容性、颜色对比度感知。自动化是基础，不是替代。",
     None,
     "code",{"checks":["axe|playwright|cypress","a11y|accessibility|wcag","Lighthouse|lighthouse","CI|pipeline|automated|threshold","assert|check"],"test_input":"","expected":""},20,None),
    (85,"accessibility","移动端无障碍：TalkBack与VoiceOver","学习移动端屏幕阅读器的测试方法和手势导航",
     "移动端无障碍测试与桌面端有本质不同：没有鼠标，只有触摸和手势。屏幕阅读器用户依赖TalkBack(Android)或VoiceOver(iOS)的线性导航。\n\n**关键测试点：**\n- **焦点顺序：** 滑动浏览的顺序是否符合逻辑？\n- **焦点指示器：** 每个元素是否有清晰的焦点边框？\n- **动态内容：** 弹窗/Toast出现时，焦点是否自动移动？\n- **手势冲突：** 应用自定义手势是否覆盖了系统无障碍手势？\n- **内容描述：** TalkBack/VoiceOver朗读的内容是否准确？\n- **动态字体：** 系统字体放大到200%时布局是否正常？\n- **颜色反转/高对比度：** 启用系统无障碍设置后是否可用？\n\n**测试方法：** 关闭屏幕（真正模拟盲人操作），只用滑动和双击导航。你会发现大量'看得见但摸不到'的问题。",
     "描述移动端无障碍测试的三个关键场景：①如何使用TalkBack测试一个电商App的完整下单流程？②如何验证动态内容(如验证码倒计时)的无障碍体验？③如何测试App在系统字体放大200%后的可用性？",
     "explore",{"keywords":["TalkBack","VoiceOver","焦点","滑动","双击","手势","动态","字体","放大","屏幕阅读器","iOS","Android","描述"]},20,None),
    (86,"data","数据质量六维度：完整、一致、及时、唯一、有效、准确","掌握评估数据质量的6维度框架——不只是'数据对不对'",
     "**数据质量(DQ)六维度框架**是评估和测试数据质量的标准方法。ETL验证告诉你数据'有没有丢失'，DQ维度告诉你数据'有没有意义'。\n\n| 维度 | 定义 | 检查方法 | QA示例 |\n|------|------|---------|--------|\n| 完整性 | 所有需要的数据都存在 | COUNT(*), NOT NULL检查 | '所有订单都有对应的用户ID吗？' |\n| 一致性 | 数据在不同地方一致 | 跨表JOIN比对 | '订单表的总金额=用户表中累计消费金额吗？' |\n| 及时性 | 数据在需要时可用 | 延迟监控 | '昨天订单的数据今天能用了吗？' |\n| 唯一性 | 没有重复记录 | UNIQUE约束, 去重检查 | '同一个用户是否被创建了两次？' |\n| 有效性 | 数据符合定义的格式和范围 | 约束检查 | '年龄字段是否有-1或999的值？' |\n| 准确性 | 数据反映真实世界 | 业务逻辑验证 | '价格×数量=总价吗？' |\n\n**在实际项目中：** DQ维度不是一次性检查——应该作为SLA的一部分持续监控。",
     None,
     "analyze",{"data_block":"某电商平台用户订单数据质量报告：\n| 维度 | 检查结果 |\n|------|--------|\n| 完整性 | 5000条订单中32条缺少user_id字段 |\n| 一致性 | 订单总金额汇总=1,234,567元 vs 支付系统=1,230,000元(差4567元) |\n| 及时性 | 订单数据T+1可用(昨天数据今天早上6点同步) |\n| 唯一性 | 发现17条重复订单(相同order_id+相同user_id) |\n| 有效性 | 3条订单的amount为负数(可能是退款未标记) |\n| 准确性 | 抽查100条订单：98条的金额×数量=总价，2条存在0.01元精度误差 |\n\n请问哪个维度的问题最紧急，应该优先修复？","question":"分析这份数据质量报告。哪个维度的问题最紧急，应该最先修复？","options":["A. 完整性——32条缺少user_id的订单无法关联到用户，影响报表和用户行为分析","B. 一致性——两个系统差了4567元，可能是支付成功的订单未同步或财务数据缺失，直接影响收入核算","C. 唯一性——17条重复订单可能导致库存被重复扣减","D. 有效性——3条负金额订单如果实际是退款，数据本身没问题，只是状态标记错误"],"correct_index":1,"explanation":"一致性问题(两个系统金额差4567元)最紧急——它直接影响财务对账和收入确认。如果你告诉CFO'我们不知道这4567元去哪了'，这是无法接受的。修复顺序：①一致性(影响财务) ②完整性(影响分析) ③唯一性(可能影响库存) ④有效性(可能不是真bug)。"},20,None),
    (87,"data","数据管道可观测性与异常检测","在数据管道中建立监控和告警——从'发现Bug'到'预防Bug'",
     "**数据管道(Data Pipeline)**负责从A点到B点搬运和转换数据。传统QA测试管道的方式是：跑一次→检查输出→发现错误→修复→再跑一次。但生产环境的数据管道是持续运行的——数据源、数据量、数据分布都在不断变化。\n\n**从测试到可观测性：**\n1. **新鲜度监控**：数据是否按时到达？设置SLA告警（'订单数据延迟>2小时'→告警）\n2. **分布监控**：数据的统计特征是否偏移？昨天用户平均订单金额=200元，今天=2000元→可能有问题\n3. **量级监控**：数据量是否异常？昨天1万条订单，今天1条→管道可能卡住了\n4. **Schema监控**：数据结构是否变化？字段类型从int变成string→下游会崩溃\n5. **空值率监控**：某个字段的NULL比例突然从1%升到30%→源系统可能有变更\n\n**QA的角色转变：** 从'执行一次性测试'→'设计持续验证规则'。这些规则不是测完就扔的脚本，而是持续运行的守卫。",
     None,
     "scenario",{
         "question":"你负责一个用户行为数据管道的质量。每天早上6点，管道从App日志→ETL处理→数据仓库。今天早上8点你收到了3条告警：①数据量只有平时的30% ②某个字段的NULL率从2%升到45% ③数据延迟3小时(通常30分钟)。你应该先调查哪一个？为什么？",
         "options":[
             "A. 先调查数据量下降——可能管道只处理了部分数据，其他数据丢失了",
             "B. 先调查NULL率升高——数据质量已经受损，会直接影响下游分析",
             "C. 先调查数据延迟——如果管道还没跑完，数据量和NULL率的问题可能是暂时的。等待管道完成后重新评估",
             "D. 三条告警一起调查——它们是同一个根因的不同表现"
         ],
         "correct_index":2,
         "explanation":"C是最合理的。三条告警很可能是同一个根因：管道延迟(还没处理完数据)。如果管道只跑了30%就慢了，那么数据量自然只有30%，未处理的70%可能包含大部分非NULL值。先检查管道是否还在运行中，等完成后重新评估——如果有问题再深入调查A和B。这个思维过程体现了QA从'看到告警就惊慌'→'系统性诊断根因'的成长。",
         "option_analysis":[
             "数据量下降很严重但如果是延迟导致的（管道还没处理完），调查A就是浪费时间。等管道跑完再看的建议是对的——但需要一个更系统化的诊断顺序。",
             "NULL率升高如果是延迟导致的（NULL值集中的分区还没处理），调查B就是误导。",
             "正确！系统化诊断：Step 1检查管道状态(是否仍在运行？) Step 2等管道完成后重新评估告警 Step 3如果仍有问题→深入调查具体指标。这个优先序避免了在临时状态下做出错误判断。",
             "它们确实可能是同一个根因——但这个结论应该是诊断的结果而不是起点。不先排除最可能的原因(延迟)就直接假设根因是'其他什么东西'，是低效的。"
         ]
     },25,None),
    (88,"visual","设计系统中的视觉测试：Storybook与Chromatic","在组件级别集成视觉快照测试到设计系统开发流程",
     "**视觉测试在生产环境的最佳实践：** 不是在页面级别截图对比，而是在组件级别——每个UI组件独立拍摄快照，版本化和基线管理。\n\n**工作流：**\n1. **设计系统(Storybook)**：每个组件有多个Stories（不同状态：Normal/Hover/Disabled/Error）\n2. **Chromatic**：每次PR自动拍摄所有组件Stories的快照\n3. **Diff Review**：自动对比新快照 vs 基线快照 → 标注差异\n4. **人工审批**：QA Review差异 → Accept(更新基线) 或 Reject(报告Bug)\n5. **CI集成**：Chromatic作为CI Check → 未审批的差异阻止Merge\n\n**关键原则：**\n- 组件级快照比页面级快照稳定100倍——因为每个组件独立，不受其他组件随机状态影响\n- 设计系统变更的可视化审计——一个CSS变量改了，自动显示所有受影响组件\n- 协作流程：设计师+开发+QA共同Review视觉变更",
     "# 写一个Playwright测试脚本，为一个按钮组件拍摄3种状态的截图\n# 要求：\n# 1. 使用Playwright的screenshot功能\n# 2. 拍摄3种状态：normal、hover、disabled\n# 3. 将截图保存为button-normal.png / button-hover.png / button-disabled.png\n# 4. 验证3张截图都已成功生成",
     "code",{"checks":["screenshot|toHaveScreenshot","playwright|chromium","page\\.","hover|locator.*hover","normal|disabled","assert|expect"],"test_input":"","expected":""},20,None),
    (89,"visual","动态与响应式视觉测试","测试动画、过渡、加载态和响应式断点在视觉回归中的表现",
     "**传统视觉测试的盲区：**\n1. **动画和过渡**：CSS transition/animation的中间状态——截图可能拍到动画的任意一帧\n2. **加载/骨架屏**：内容加载前的骨架屏状态——截图时机不对就会把骨架屏当作Bug\n3. **响应式断点**：同一个组件在不同宽度下外观不同——320px/768px/1024px/1440px\n4. **动态内容**：日期、时间、随机推荐——每次都变，传统diff会产生大量误报\n\n**解决方案：**\n- 动画：先禁用动画( prefers-reduced-motion / 等待动画完成 )再截图\n- 骨架屏：mock数据立即返回——截图验证的是最终状态，骨架屏单独验证\n- 断点：每个组件定义3-5个关键断点，每个断点独立快照\n- 动态内容：使用固定数据(mock date/time)、使用视觉mask遮罩动态区域\n\n**视觉测试不是'截图然后diff'——是设计一个确定性环境，确保截图是可重复和可比对的。**",
     "设计一个登录页面的响应式视觉测试方案。登录页面包含：Logo(居中)、用户名输入框、密码输入框、登录按钮、忘记密码链接。请描述：①如何在3个断点(375px手机/768px平板/1440px桌面)下验证布局无重叠 ②加载态和错误态如何触发并截图 ③动态内容(如时间戳)如何处理保证测试可重复",
     "explore",{"keywords":["断点","响应式","375|768|1440","加载","骨架屏","动画","过渡","动态","mock","禁用","截图","可重复"]},20,None),
    # ===== 安全深化 (90-97) =====
    (90,"security","API安全深度：GraphQL/gRPC/WebSocket漏洞","测试现代API特有的安全漏洞——不只是REST的SQL注入",
     "**现代API带来了全新的攻击面。** 传统的Web安全测试（SQL注入/XSS）主要针对REST+HTML，但GraphQL/gRPC/WebSocket有完全不同的漏洞模式。\n\n**GraphQL特有漏洞：**\n- **内省滥用：** `__schema`查询可以导出整个API结构——攻击者的免费文档\n- **深度查询DoS：** 嵌套查询可以一次请求拉取海量数据\n- **字段级授权缺失：** REST有端点级授权，GraphQL需要字段级——容易遗漏\n- **批处理攻击：** 别名+批量查询可以绕过速率限制\n\n**gRPC特有漏洞：**\n- ProtoBuf模糊测试——畸形消息导致服务崩溃\n- 默认无超时——gRPC调用可能永久挂起\n- 反射API泄露——`grpc.reflection`暴露所有服务和方法\n\n**WebSocket特有漏洞：**\n- CSWSH(Cross-Site WebSocket Hijacking)——WebSocket没有同源策略\n- 消息注入——没有验证的消息可以触发服务端任意操作\n- 连接耗尽——打开大量WebSocket连接但不发送数据",
     None,
     "code",{"checks":["GraphQL|graphql","introspection|__schema","DoS|depth|nested","WebSocket|CSWSH","gRPC|protobuf|reflection","fuzz|fuzzing"],"test_input":"","expected":""},25,None),
    (91,"security","SAST/DAST管道集成：Semgrep+ZAP自动化","将安全测试集成到CI/CD管道——从一次性扫描到持续安全",
     "**SAST(Static Application Security Testing)**分析源代码找漏洞。**DAST(Dynamic Application Security Testing)**攻击运行中的应用找漏洞。两者互补——SAST发现代码中的SQL注入模式，DAST验证实际是否可以注入。\n\n**Semgrep：** 开源SAST工具，支持自定义规则。可以写规则检测：`pattern: db.execute(\"SELECT...\" + request.form[...])`\n\n**OWASP ZAP自动化：** 可以在CI中无头模式运行——`zap.sh -cmd -quickurl http://target`。每次部署后自动扫描。\n\n**管道设计：**\n1. PR提交→Semgrep扫描(SAST)→发现硬编码密钥/已知漏洞模式→阻止合并\n2. Staging部署→ZAP主动扫描(DAST)→发现运行时漏洞→生成报告\n3. 定期依赖扫描(Dependabot/Snyk)→发现已知CVE→自动PR更新\n\n**QA的角色：** 不只是运行扫描——更要Review扫描结果，排除误报，追踪修复。",
     "# 写一个Semgrep规则，检测Python代码中潜在的SQL注入模式\n# 规则要求：\n# 1. 检测使用字符串拼接(f-string / + / %)构建SQL查询的模式\n# 2. 输出规则ID、严重级别、匹配代码位置\n# 3. 测试规则：准备一段有SQL注入风险的代码和一段安全的参数化查询代码\n# 提示：参考Semgrep的pattern-syntax",
     "code",{"checks":["Semgrep|semgrep","pattern|rule","SQL|sql|query|db\\.execute","string|f-string|format|%","severity|ERROR|WARNING","def test"],"test_input":"","expected":""},25,None),
    (92,"security","威胁建模：STRIDE/攻击树/DREAD","在测试之前先建模——知道攻击者会怎么攻击才知道该测什么",
     "**威胁建模(Threat Modeling)**回答四个问题：①我们在构建什么？②什么可能出错？③我们该怎么办？④我们做得好吗？\n\n**STRIDE六类威胁：**\n- **S**poofing(仿冒)：攻击者伪装成合法用户\n- **T**ampering(篡改)：修改数据或代码\n- **R**epudiation(否认)：用户否认做过某个操作\n- **I**nformation Disclosure(信息泄露)：数据暴露给未授权方\n- **D**enial of Service(拒绝服务)：使系统不可用\n- **E**levation of Privilege(权限提升)：普通用户获得管理员权限\n\n**攻击树：** 以攻击者目标为根节点，分解为子目标，直到具体的攻击技术。例如：Root='窃取用户信用卡号'→Branch1='截获传输中数据'→Leaf1='中间人攻击'→Leaf2='未加密传输'\n\n**DREAD评分：** Damage(损害)+Reproducibility(可复现性)+Exploitability(可利用性)+Affected Users(影响用户)+Discoverability(可发现性)。每项1-10分，总分排序—高分的先修。",
     None,
     "analyze",{"data_block":"一个在线银行系统包含以下组件：Web前端(React)、API网关(Kong)、用户服务(Go)、账户服务(Java)、支付服务(Python)、数据库(PostgreSQL)、消息队列(Kafka)\n\n请分析以下攻击场景属于STRIDE的哪个类别：\n1. 攻击者修改HTTP请求中的user_id参数，查看其他用户的账户余额\n2. 攻击者发送10000个并发请求导致API网关CPU 100%\n3. 攻击者在用户服务日志中发现明文密码\n4. 攻击者使用SQL注入绕过登录验证\n5. 用户声称自己从未进行过某笔转账——但系统日志显示该操作来自其IP和设备","question":"将上述5个攻击场景分别映射到STRIDE类别。哪个场景的风险最高（DREAD总分），应该优先修复？","options":["A. 场景1(Tampering)风险最高——直接导致未授权数据访问","B. 场景2(Denial of Service)风险最高——影响所有用户的可用性","C. 场景3(Information Disclosure)风险最高——明文密码泄露可能影响所有用户的所有账户","D. 场景5(Repudiation)风险最高——否认攻击可能导致合规问题(如PCI-DSS)"],"correct_index":2,"explanation":"场景3(信息泄露)的DREAD分最高：D=10(明文密码可以直接登录用户账户)、R=10(每次日志都泄露——100%可复现)、E=9(只需访问日志系统——相对容易)、A=10(所有用户)、D=5(需要知道日志位置)。总分44。虽然DoS(场景2)也很严重，但通常有自动恢复机制。明文密码泄露是'安静的、持久的数据泄露'——最危险。"},25,None),
    (93,"security","容器与Kubernetes安全测试","测试容器化环境特有的安全攻击面",
     "**容器和K8s引入了全新的安全边界。** 应用安全 ≠ 容器安全——即使应用代码完美，容器配置错误仍然可以导致集群被攻破。\n\n**关键测试点：**\n\n1. **容器逃逸：** 特权容器(`--privileged`)、挂载docker.sock、capabilities过度授予——攻击者从容器内逃逸到宿主机\n2. **Pod安全：** Pod间网络通信未限制(NetworkPolicy缺失)、hostPID/hostNetwork滥用、emptyDir泄露敏感数据\n3. **RBAC滥用：** ServiceAccount权限过大——一个被攻破的Pod可以列出所有Secrets\n4. **镜像安全：** 以root运行、基础镜像有已知CVE、镜像层中包含密钥(truffleHog扫描)\n5. **etcd暴露：** etcd存储所有集群状态——如果未加密且端口暴露，攻击者可以读取所有数据\n6. **准入控制器绕过：** 修改Pod spec绕过安全策略\n\n**QA的容器安全清单：** `kubescape scan`、`trivy image`、`falco`运行时检测、`kube-hunter`、`kube-bench`",
     None,
     "scenario",{
         "question":"你的公司刚迁移到K8s。安全扫描发现以下问题：①3个Pod以root运行 ②API Server未设置速率限制 ③etcd端口对外暴露 ④ServiceAccount使用cluster-admin权限 ⑤无NetworkPolicy(所有Pod互通)。作为一个只有2人的安全QA团队，你应该优先修复哪个？",
         "options":[
             "A. 先修复etcd暴露——etcd包含所有集群机密，一旦被访问整个集群沦陷",
             "B. 先修复root运行——这是最容易修复的(改Dockerfile的USER)，也是合规审计最常发现的问题",
             "C. 先收敛ServiceAccount权限——cluster-admin权限意味着任何一个被攻破的Pod都可以完全控制集群",
             "D. 先部署NetworkPolicy——所有Pod互通意味着攻击者攻破一个Pod后可以扫描整个内网"
         ],
         "correct_index":2,
         "explanation":"C是最紧急的。cluster-admin的ServiceAccount意味着：即使你修复了etcd暴露，攻击者通过一个低权限Pod+cluster-admin SA仍然可以读取所有Secrets包括etcd凭证。修复顺序：①收敛SA权限(最高杠杆——限制攻击者能做什么) ②etcd暴露 ③root运行 ④NetworkPolicy。安全修复不是'全都要'——是'先修最能限制攻击者的'。",
         "option_analysis":[
             "etcd暴露非常严重——但如果你收敛了SA权限，即使攻击者接触到etcd，他们也需要另外的凭证才能访问。先收敛权限能降低所有后续攻击的爆炸半径。",
             "root运行是最容易修复的但不是最紧急的——攻击者要利用root权限首先需要进入容器，而当前最大的风险是'已经进入容器后能做什么'(SA权限)。修复root运行很好，但不应该是第一步。",
             "正确！权限收敛是安全加固中'杠杆率最高'的修复——它限制了攻击者在攻破任何入口后的横向移动能力。先修这个，再修其他。",
             "NetworkPolicy重要但没有SA权限紧急——即使限制了网络，如果攻击者通过cluster-admin SA可以直接用API读取数据，不需要网络扫描。"
         ]
     },30,None),
    (94,"security","云安全测试：AWS IAM/S3/Lambda","学习测试云服务配置和身份访问管理的安全性",
     "**云安全不是应用安全——是配置安全。** AWS/GCP/Azure的绝大多数安全事件不是应用Bug导致的，而是云资源配置错误。\n\n**AWS核心测试面：**\n\n1. **IAM权限升级：** 一个低权限角色可以通过`iam:PassRole`→`iam:CreatePolicyVersion`→`iam:AttachUserPolicy`链升级到Admin。QA需要验证权限边界是否有这种路径。\n\n2. **S3数据泄露：** 桶的Block Public Access是否正确配置？是否有意外公开的桶？桶策略是否允许跨账户访问？\n\n3. **Lambda注入：** Lambda函数被S3事件触发——如果S3文件名包含恶意代码(如`file'; DROP TABLE--.pdf`)，Lambda如何处理？\n\n4. **跨账户信任：** IAM Role的Trust Policy是否允许了不该信任的外部账户？\n\n5. **CloudTrail审计：** 所有操作是否被记录？日志是否被保护(不被删除)？\n\n**测试工具：** Pacu(AWS渗透测试框架)、ScoutSuite(多云安全审计)、prowler(AWS安全检查)。",
     "你负责测试一个AWS环境的安全配置。这个环境包含：3个S3桶(日志/图片/备份)、5个Lambda函数、1个EC2实例、IAM角色。请描述你的安全测试策略：①如何检查S3桶是否有数据泄露风险？②如何审计IAM权限是否有过度授权或权限升级路径？③如何测试Lambda函数的事件注入风险？④应该设置哪些CloudTrail/GuardDuty告警？",
     "explore",{"keywords":["IAM","权限","S3","公开","Lambda","注入","CloudTrail","审计","Pacu","ScoutSuite","Trust Policy","跨账户"]},25,None),
    (95,"security","移动安全测试：Frida/MobSF/证书固定","学习移动应用的逆向工程和运行时安全分析",
     "**移动安全测试有独特的工具链和攻击面。** 与Web安全不同——移动应用运行在沙箱中，但沙箱配置、数据存储、网络通信和IPC都有独特漏洞。\n\n**关键测试工具：**\n- **MobSF(Mobile Security Framework)：** 自动化APK/IPA安全分析——静态分析(Manifest权限、硬编码密钥、不安全随机数)+动态分析(运行时行为)\n- **Frida：** 动态插桩框架——在运行时Hook函数、绕过Root检测、绕过证书固定、修改返回值\n- **adb/jdwp：** Android调试桥+Java调试协议——可以附加到运行中的应用\n\n**核心测试场景：**\n1. **证书固定绕过：** 应用使用了HTTPS+证书固定——用Frida Hook `checkServerTrusted`方法——可以成功中间人攻击吗？\n2. **数据存储安全：** SharedPreferences/NSUserDefaults是否存储了敏感数据(Token/密码)？Internal Storage文件的权限是否正确？\n3. **WebView漏洞：** `setJavaScriptEnabled(true)` + `addJavascriptInterface` = 任意Java方法调用\n4. **Root/Jailbreak检测：** 检测逻辑是否可以绕过？绕过后的降级行为是否安全？",
     "# 写一个使用Frida Hook Android应用的测试脚本\n# 场景：绕过一个App的Root检测\n# 要求：\n# 1. Hook System.getProperty('ro.build.tags') 让它返回 'release-keys' 而非 'test-keys'\n# 2. 验证绕过是否成功\n# 3. 记录Hook调用日志\n# 提示：使用Java.perform + Java.use",
     "code",{"checks":["Frida|Java\\.perform","Hook|hook|implementation","System\\.getProperty|ro\\.build","test-keys|release-keys","override|bypass|绕过"],"test_input":"","expected":""},25,None),
    (96,"security","供应链安全：SBOM+依赖混淆+SLSA","测试软件供应链的完整性和安全性——2026年最关键的QA新技能",
     "**供应链攻击是2025-2026年增长最快的攻击向量。** SolarWinds、xz后门、Log4Shell——每一个都告诉我们：你引入的每一个依赖都是潜在的漏洞。\n\n**QA在供应链安全中的角色：**\n\n1. **SBOM生成与验证：** 用Syft/Grype生成软件物料清单，验证依赖树中是否有已知CVE。`syft packages dir:./app -o spdx-json`\n\n2. **依赖混淆测试：** 如果你的`requirements.txt`中有`internal-lib==1.0.0`，攻击者在PyPI上注册同名包——pip是否会安装错误的包？\n\n3. **SLSA框架审计：** SLSA(Supply-chain Levels for Software Artifacts)分4级——你的构建管道达到哪一级？源代码是否经过验证？构建是否可复现？\n\n4. **TypoSquatting检测：** `reqeusts`(拼错一个字母) vs `requests`——你的依赖中是否有拼写错误的包名？\n\n5. **镜像签名验证：** Docker镜像是否签名？拉取时是否验证签名？",
     None,
     "analyze",{"data_block":"你的项目使用以下依赖链：\n1. Flask==2.3.0 → Werkzeug==2.3.0 → (无进一步依赖)\n2. requests==2.31.0 → urllib3==2.0.0 → (无进一步依赖)\n3. internal-auth==1.5.0 → (内部私有包)\n4. numpy==1.24.0 → (纯C扩展，无Python依赖)\n\n安全扫描结果：\n- Werkzeug 2.3.0: CVE-2024-XXXX (CVSS 7.5 — DoS漏洞)\n- urllib3 2.0.0: CVE-2024-YYYY (CVSS 9.8 — RCE漏洞，已在urllib3 2.0.2修复)\n- internal-auth 1.5.0: 在PyPI上存在同名包(internal-auth 1.5.0)，但代码完全不同\n\n请问供应链的三个问题分别是什么？应该怎么处理？","question":"分析这三个供应链安全问题。哪个最紧急，应该最先处理？","options":["A. urllib3的RCE漏洞(CVSS 9.8)——立即升级到2.0.2或更高版本，RCE是最高严重性","B. internal-auth的依赖混淆风险——修改pip配置添加私有索引优先，并验证internal-auth包来源","C. Werkzeug的DoS漏洞(CVSS 7.5)——升级到最新版本，DoS虽然严重性低于RCE但仍然很重要","D. 三个问题一样重要——同时全部修复"],"correct_index":0,"explanation":"urllib3的RCE(CVSS 9.8)是最紧急的——远程代码执行意味着攻击者可以在你的服务器上运行任意代码。但依赖混淆(选项B)是'静默的最危险'——pip可能已经安装了恶意包你都不知道。修复顺序：①urllib3立即升级(已知CVE，有明确修复) ②验证internal-auth来源(可能已经中招) ③Werkzeug升级。"},25,None),
    (97,"security","高级认证攻击：JWT算法混淆/OAuth PKCE/SAML","测试现代认证协议中的高级漏洞——JWT/OAuth/SAML",
     "**认证是现代应用的第一道防线——也是攻击者最爱的目标。**\n\n**JWT高级攻击：**\n- **alg=none：** 将算法头改为`none`——服务端跳过签名验证\n- **算法混淆(RS256→HS256)：** 用公钥做HMAC密钥——服务端用RSA公钥验证HS256签名→永远通过\n- **JKU/JWK注入：** 在JWT头中注入`jku`(JWK Set URL)→服务端从攻击者控制的URL获取密钥\n- **kid注入：** `kid`可以是任意值→如果服务端用它做文件名：`../../../../../etc/passwd`\n\n**OAuth 2.0高级攻击：**\n- **PKCE绕过：** 如果没实现PKCE，Authorization Code可以被拦截\n- **redirect_uri验证绕过：** `https://legit.com%40evil.com`→解析器差异\n- **state参数缺失：** CSRF攻击——攻击者用自己的授权码登录受害者的账户\n\n**SAML攻击：**\n- **XML签名包装(XSW)：** 在SAML响应中注入第二个断言——服务端验证了第一个(无害的)，但使用了第二个(恶意的)\n- **XXE通过SAML：** 如果SAML解析器配置错误，可以通过XML实体注入读取服务器文件",
     None,
     "debug",{"checks":["alg.*none|algorithm.*none","RS256|HS256","JKU|jku|jwk","PKCE|pkce","redirect_uri|redirect_uri.*valid","XSW|signature wrapping|XML"],"test_input":"","expected":""},30,None),
    # ===== 金融测试 (98-101) =====
    (98,"fintech","支付协议测试：ISO 8583/20022消息流","学习构建和验证金融行业标准支付协议消息",
     "**金融行业使用高度结构化的消息协议。** 不同于REST API的灵活JSON，金融协议有精确的字段定义、严格的验证规则和行业通用的交换格式。\n\n**ISO 8583(银行卡交易)：** 定义了银行卡交易的报文格式。例如：MTI(Message Type Indicator)='0100'=授权请求，DE2(PAN-主账号)，DE4(交易金额)。每个字段有精确的数据类型和长度。\n\n**ISO 20022(金融业通用消息)：** 基于XML的现代标准——覆盖支付(pacs.008)、对账(camt.053)、状态(camt.054)。SWIFT正在从MT(Messaging Type)迁移到MX(ISO 20022)。\n\n**QA测试要点：**\n- 字段级验证：必填/可选、数据类型、长度限制、特殊值处理\n- 消息流：请求→响应→冲正→对账 的完整生命周期\n- 网络模拟：模拟ISO 8583网络协议响应码(00=成功，05=拒绝，91=发卡方不可用)\n- 超时和重试：支付接口的超时行为和幂等性保证\n\n**关键工具：** jPOS(Java支付框架)、SWIFT MT/MX验证器、Paragon(ISO 8583测试工具)",
     None,
     "code",{"checks":["ISO.*8583|8583","MTI|mti|Message.*Type","PAN|DE2|field.*2","response.*code|00|05|91","timeout|retry|幂等","validate|验证|pars"],"test_input":"","expected":""},25,None),
    (100,"fintech","金融计算测试：精度/四舍五入/多币种","测试金融计算中的数值精度——浮点数不能用于金钱",
     "**金融计算第一条铁律：永远不要用浮点数(float/double)表示金钱。** 浮点数是二进制的近似值——0.1+0.2不等于0.3。\n\n**正确做法：**\n- **整数(Micros)：** 以最小货币单位存储——$12.34存为1234分。Stripe、Adyen、PayPal都用这种方案\n- **Decimal(定点数)：** Python的Decimal、Java的BigDecimal——精确十进制运算\n- **Currency-Aware类型：** 不只是数字——还包含货币代码(ISO 4217)\n\n**真实世界的精度陷阱：**\n1. **货币四舍五入：** JPY(日元)是0位小数，BHD(巴林第纳尔)是3位小数。一个金额从BHD转成JPY——应该四舍五入到0位\n2. **汇率计算顺序：** (1920 BHD × 0.376) ÷ 1 → 不同顺序可能产生1日元的差异\n3. **复利边界：** 日利率=年利率/365还是/360(银行惯例)？闰年2月29日怎么算？\n4. **负利率：** 是的，有些货币现在是负利率——你的代码测试过负数利息吗？\n\n**测试策略：** 使用已知答案的测试用例——从生产系统的历史数据中提取'正确答案'，然后验证新系统计算结果匹配。",
     # 找出下面代码中的精度Bug
     "# 这段代码有一个金融精度的Bug，找出并修复它\n# 场景：计算两种货币的兑换金额\n\ndef convert_currency(amount, from_currency, to_currency):\n    rates = {'USD': 1.0, 'JPY': 110.5, 'BHD': 0.376, 'EUR': 0.92}\n    usd_amount = amount / rates[from_currency]\n    result = usd_amount * rates[to_currency]\n    return round(result, 2)\n\n# Bug提示：\n# 1. 浮点数精度问题\n# 2. JPY应该四舍五入到0位小数\n# 3. BHD应该四舍五入到3位小数\n# 测试用例：convert(100, 'BHD', 'JPY') 应该等于多少？",
     "debug",{"checks":["Decimal|from decimal","integer|int|分|cent","quantize|ROUND_HALF|round","0.*decimal|3.*decimal|JPY.*0|BHD.*3","assert|def test"],"test_input":"","expected":""},30,None),
    (101,"fintech","支付网关集成：3D Secure/幂等性/退款","作为QA Lead设计支付网关集成的完整测试策略",
     "**支付网关集成是QA的'心脏手术'级别的任务——不能出错。**\n\n**3D Secure(3DS2)流程：**\n1. 用户提交支付→网关返回3DS挑战URL→用户完成银行验证→银行回调→支付完成\n2. 每个环节都可能失败或超时——QA需要模拟：挑战超时、用户取消、银行拒绝、回调丢失\n\n**幂等性(Idempotency)：**\n- 支付请求必须幂等——同一个Idempotency-Key提交两次，只产生一次扣款\n- 测试：提交两次相同Key的支付请求→第二次应该返回第一次的结果，不重复扣款\n\n**退款/部分退款：**\n- 全额退款：`POST /refund {payment_id, amount: 100.00}`\n- 部分退款：`POST /refund {payment_id, amount: 30.00}` (只退30元)\n- 超额退款：`amount=150.00`→应该被拒绝(不能退超过原始金额)\n- 重复退款：同一笔支付两次全额退款→第二次应该被拒绝\n\n**冲正(Reversal)：**\n- 超时冲正：支付请求超时→系统自动发送冲正→确保不扣款\n- 手动冲正：客服发现错误→手动触发冲正→审核流程→执行",
     None,
     "scenario",{
         "question":"你负责测试一个新的支付网关集成。测试环境已配置好沙箱(sandbox)账户。以下是你在上线前必须验证的5个关键场景。如果时间只够测3个，应该优先测哪3个？",
         "options":[
             "A. 3DS挑战成功支付 + 幂等性重复提交 + 超时冲正——验证'钱对'的核心闭环",
             "B. 3DS挑战成功支付 + 全额退款 + UI页面显示正确——验证用户体验闭环",
             "C. 所有错误码(05/14/41/51/91)的UI展示 + 部分退款 + 汇率计算——验证边界场景",
             "D. 3DS挑战超时 + 网络重连 + 并发支付——验证异常场景的健壮性"
         ],
         "correct_index":0,
         "explanation":"A覆盖了支付网关最核心的风险：①钱能不能正确收(3DS成功支付) ②会不会重复收费(幂等性) ③扣款失败时钱会不会错(超时冲正)。这三个场景如果通过，至少保证了'钱是对的'。退款(B)重要但可以延后——如果核心支付出错，退款功能再完美也没意义。错误码展示(C)重要但不紧急。并发(D)在沙箱环境难以真实模拟——生产环境首次上线时并发量也不高。",
         "option_analysis":[
             "正确！MVP支付测试 = 正常路径(收钱)+去重保护(不重复收)+异常回滚(不错误收)。这三个场景覆盖了支付的核心风险。",
             "退款和UI展示重要——但在沙箱环境下全额退款和UI测试的价值远低于验证'钱是否正确'。退款可以在UAT阶段补测。",
             "错误码展示重要——但优先测试'正确的路径'再测试'错误的路径'。而且部分退款和汇率计算可以延后到阶段2。",
             "并发和网络异常重要——但沙箱环境无法真实模拟生产并发量。这些场景应该在性能测试和混沌工程阶段(而非功能测试阶段)验证。"
         ]
     },30,None),
    (102,"fintech","PCI-DSS合规验证：数据脱敏/加密/审计","测试支付卡行业数据安全标准(PCI-DSS)的合规性",
     "**PCI-DSS(Payment Card Industry Data Security Standard)是所有处理信用卡数据的组织必须遵守的安全标准。** 不合规可能导致巨额罚款和失去收单资格。\n\n**QA在PCI-DSS中的测试责任：**\n\n1. **PAN(主账号)脱敏：** 显示时最多前6位+后4位(如`411111******1111`)。存储时必须加密。日志中是否意外记录了完整卡号？\n\n2. **CDE(持卡人数据环境)分段：** 处理卡数据的系统必须与普通系统网络隔离。QA需要验证：普通App服务器能否直接访问Cardholder Data？\n\n3. **TLS强制：** 所有传输卡数据的通信必须使用TLS 1.2+。QA测试：能否通过HTTP(非HTTPS)访问支付端点？\n\n4. **审计追踪：** 所有对卡数据的访问必须被记录——谁、什么时候、访问了什么、做了什么。QA验证：日志是否包含所有必要字段？日志是否防篡改？\n\n5. **测试数据规则：** 开发和测试环境严禁使用真实卡号。QA必须使用PCI-DSS批准的测试卡号(如`4111111111111111`)——这是合规要求，不是建议。",
     None,
     "analyze",{"data_block":"你的公司通过了PCI-DSS SAQ-D评估，但以下是最近一次内部审计发现的问题：\n1. 应用日志中发现3条记录包含完整16位卡号(PAN)——来自一个错误日志输出\n2. 开发环境的支付测试正在使用真实卡号(一个开发者的个人信用卡)\n3. 支付微服务和用户管理微服务共享同一个数据库，用户管理服务可以直接读取支付表\n4. TLS 1.0在旧版API网关上仍被支持——虽然已配置1.2优先但1.0未完全禁用\n5. 对卡数据的数据库查询没有审计记录——只记录了API请求日志\n\n请评估这些问题按照PCI-DSS严重性排序。","question":"按照PCI-DSS合规的影响程度排序，哪个问题最严重，会直接导致审计失败？","options":["A. 日志中的完整PAN——这是明文存储敏感认证数据的直接证据，PCI-DSS审计员会在5分钟内发现并标记为关键不符合项","B. 开发环境使用真实卡号——这是PCI-DSS明确禁止的，可能导致真实卡号泄露到非安全环境","C. CDE未分段——如果用户管理服务被攻破，攻击者可以直接读取支付数据","D. TLS 1.0仍支持——虽然已配置1.2优先，但支持1.0就可以被降级攻击利用"],"correct_index":0,"explanation":"日志中的完整PAN(A)是PCI-DSS审计中最严重的违反——Req 3.4明确要求PAN在存储时必须不可读(unreadable)。这是'直接证据'——审计员不需要推理，日志里的16位数字就是事实。其他问题：B是策略违规但卡号尚未泄露，C是架构缺陷但需要攻击前提，D是配置问题但已有缓解措施。修复顺序：①立即清理日志+启用PAN掩码 ②禁止开发环境真实卡号 ③规划CDE分段 ④禁用TLS 1.0。"},25,None),
]


def seed():
    with sync_engine.begin() as conn:
        r = conn.execute(text("SELECT 1 FROM levels LIMIT 1"))
        if r.fetchone():
            return
        import os as _os
        if not _os.getenv("SEED_DB") and not _os.getenv("DATABASE_URL", "").startswith("sqlite"):
            print("SEED: Refusing to seed non-SQLite database without SEED_DB=true")
            return
        print("SEED: Seeding database with default data...")
        # Default test account
        pw = bcrypt.hashpw("qa123456".encode(), bcrypt.gensalt()).decode()
        conn.execute(User.__table__.insert().values(
            username="qatest", email="qatest@qa.local",
            hashed_password=pw, is_admin=True))
        for t in TOOL_SEED:
            conn.execute(Tool.__table__.insert().values(
                name=t[0], icon=t[1], category=t[2], stage=t[3], level=t[4],
                desc=t[5], license=t[6], url=t[7], has_tutorial=t[8]))
        for lv in LEVEL_SEED:
            conn.execute(Level.__table__.insert().values(
                order=lv[0], stage=lv[1], title=lv[2], description=lv[3],
                theory=lv[4], demo=lv[5], task_type=lv[6], task_config=lv[7],
                points=lv[8], tool_id=lv[9]))
        # Seed achievements
        from app.models.achievement import Achievement
        for a in [
            ("first", "🌟", "初出茅庐", "完成第 1 关", "completed_count", "1"),
            ("five", "🔥", "小有所成", "完成 5 关", "completed_count", "5"),
            ("ten", "⚡", "中流砥柱", "完成 10 关", "completed_count", "10"),
            ("half", "💎", "半壁江山", "完成 20 关", "completed_count", "20"),
            ("beginner", "🌱", "入门毕业", "完成全部入门关卡", "stage_done", "beginner"),
            ("web", "🌐", "Web 专家", "完成全部 Web 测试关卡", "stage_done", "web"),
            ("lab1", "🧪", "实验室新人", "使用 1 个实验室", "lab_count", "1"),
            ("lab3", "🔬", "实验达人", "使用 3 个实验室", "lab_count", "3"),
        ]:
            conn.execute(Achievement.__table__.insert().values(
                key=a[0], icon=a[1], name=a[2], desc=a[3],
                condition_type=a[4], condition_value=a[5]))
