import urllib.request as R, json as J, sqlite3 as S, time, sys

BASE = 'http://127.0.0.1:8005'
ok = 0; fail = 0

def api(m, p, b=None, t=None):
    u = f'{BASE}{p}'; d = J.dumps(b).encode() if b else None
    h = {'Content-Type':'application/json'}
    if t: h['Authorization'] = f'Bearer {t}'
    req = R.Request(u, data=d, headers=h, method=m)
    try:
        with R.urlopen(req, timeout=20) as r:
            return r.status, J.loads(r.read())
    except R.HTTPError as e: return e.code, J.loads(e.read())

def get(p, t):
    try:
        with R.urlopen(R.Request(f'{BASE}{p}', headers={'Authorization':f'Bearer {t}'}), timeout=20) as r:
            return r.status, J.loads(r.read())
    except R.HTTPError as e: return e.code, J.loads(e.read())

def check(desc, condition):
    global ok, fail
    if condition:
        print(f'  PASS: {desc}'); ok += 1
    else:
        print(f'  FAIL: {desc}'); fail += 1

# ========== AUTH ==========
print('=== AUTH ===')
s, r = api('POST', '/api/auth/register', {'username':'e2e_main','email':'e2e@t.com','password':'pass1234'})
check('register returns 200', s == 200)
T = r['access_token']

s, r = api('POST', '/api/auth/login', {'username':'e2e_main','password':'pass1234'})
check('login returns 200', s == 200)

s, r = api('POST', '/api/auth/login', {'username':'e2e_main','password':'wrong'})
check('wrong password returns 401', s == 401)

s, r = get('/api/auth/me', T)
check('me returns user data', s == 200 and r.get('username') == 'e2e_main')

# Admin login
s, r = api('POST', '/api/auth/login', {'username':'qatest','password':'qa123456'})
AT = r['access_token']
check('admin login works', s == 200)

# ========== ADMIN ==========
print('\n=== ADMIN ===')
s, r = api('GET', '/api/admin/stats', t=AT)
check('admin stats returns user/level counts', s == 200 and 'users' in r)

s, r = api('GET', '/api/admin/users', t=AT)
check('admin user list works', s == 200 and 'users' in r)

s, r = api('GET', '/api/admin/levels', t=AT)
check('admin level list works', s == 200 and len(r['levels']) > 0)

s, r = api('POST', '/api/admin/levels', {
    'title':'E2E TEST','stage':'beginner','task_type':'quiz','points':5,
    'description':'test','theory':'t','task_config':{'question':'Q?',
    'options':['A','B'],'correct_index':0,'explanation':'x'}
}, t=AT)
check('admin create level', s == 200)

s, r = api('PUT', '/api/admin/levels/reorder', {'items':[{'id':1,'order':1}]}, t=AT)
check('admin reorder levels', s == 200)

s, r = api('DELETE', '/api/admin/levels/103', t=AT)
check('admin delete level', s == 200)

s, r = api('GET', '/api/admin/stats', t=T)
check('non-admin blocked from admin', s == 403)

# ========== UNLOCK ALL LEVELS ==========
print('\n=== UNLOCK ===')
uid = r2 = None
s, r2 = api('POST', '/api/auth/register', {'username':'e2e_full','email':'ef@t.com','password':'pass1234'})
FT = r2['access_token']; uid = r2['user_id']
db = S.connect('data/qa_tools.db')
for (lid,) in db.execute('SELECT id FROM levels WHERE id <= 102').fetchall():
    db.execute("INSERT INTO user_level_progress(user_id,level_id,status,score,attempts) VALUES(?,?,?,0,0) ON CONFLICT DO UPDATE SET status=?", (uid,lid,'unlocked','unlocked'))
db.commit(); db.close()
s, lv = get('/api/levels', FT)
u = sum(1 for l in lv['levels'] if l['status'] != 'locked')
check(f'unlocked {u}/102', u >= 100)

# ========== ALL 6 TASK TYPES ==========
print('\n=== TASK TYPES ===')

s, r = api('POST', '/api/levels/submit', {'level_id':1,'answer':{'choice':1}}, t=FT)
check('QUIZ: correct answer scores 100', r['score'] == 100 and r['correct'])

s, r = api('POST', '/api/levels/submit', {'level_id':3,'answer':{'text':'需求 评审 尽早 早期 成本 shift left 静态测试 缺陷 策略 质量'}}, t=FT)
check('EXPLORE: keywords match scores >= 60', r['score'] >= 60)

code = 'def add(a,b): return a+b\ndef test_add():\n    assert add(1,2)==3\n    assert add(-1,1)==0\n    assert add(0,0)==0\nprint("ok")'
s, r = api('POST', '/api/levels/submit', {'level_id':15,'answer':{'code':code}}, t=FT)
check('CODE: clean exit scores >= 80', r.get('score', 0) >= 80 and r.get('correct'))

dbg = 'def login(u,p):\n    users={"admin":"pass123","alice":"password123"}\n    if u in users:\n        if users[u]==p:\n            return "Login OK"\n    return "Invalid credentials"\nprint(login("admin","password123"))'
s, r = api('POST', '/api/levels/submit', {'level_id':44,'answer':{'code':dbg}}, t=FT)
check('DEBUG: fix == bug scores 100', r.get('score') == 100 and r.get('correct'))

s, r = api('POST', '/api/levels/submit', {'level_id':46,'answer':{'choice':1}}, t=FT)
check('SCENARIO: correct choice scores 100', r.get('score') == 100 and r.get('correct'))

s, lv2 = get('/api/levels', FT)
al = [l for l in lv2['levels'] if l['task_type'] == 'analyze']
s, r = api('POST', '/api/levels/submit', {'level_id':al[0]['id'],'answer':{'choice':0}}, t=FT)
check('ANALYZE: grading works', r.get('score') is not None)

# ========== LABS ==========
print('\n=== LABS ===')
s, r = api('POST', '/api/labs/sql/execute', {'sql':"SELECT severity, COUNT(*) as cnt FROM bugs WHERE module='login' GROUP BY severity",'level_id':38}, t=FT)
check('SQL lab with scenario data', s == 200 and r['ok'])

s, r = api('POST', '/api/labs/cmd/execute', {'cmd':'grep -c ERROR /var/log/app.log', 'level_id':0}, t=FT)
check('CMD lab grep count', s == 200 and r['ok'])

s, r = api('POST', '/api/labs/security/xss', {'payload':'<script>alert(1)</script>'}, t=FT)
check('Security XSS detection', s == 200 and r['script_executed'])

s, r = api('POST', '/api/labs/security/sqli', {'username':"admin' OR 1=1 --",'password':'x'}, t=FT)
check('Security SQLi detection', s == 200 and r['auth_bypassed'])

s, r = api('POST', '/api/labs/performance/simulate', {'script':'import http from "k6/http";\nexport default function(){http.get("http://test.k6.io");}','vus':5,'duration':10}, t=FT)
check('K6 simulation', s == 200 and r['ok'])

# ========== TESTCASES + TEAMS + MOCK ==========
print('\n=== TESTCASES+TEAMS+MOCK ===')
s, r = api('POST', '/api/testcases', {'title':'E2E Test','steps':'1. Test','expected_result':'Pass','priority':'P0','status':'ready'}, t=FT)
check('testcase create', s == 200)
s, r = api('GET', '/api/testcases', t=FT)
check('testcase list', s == 200 and r['total'] > 0)

s, r = api('POST', '/api/teams', {'name':'E2E Team'}, t=FT)
check('team create', s == 200)
s, r = api('GET', '/api/teams/mine', t=FT)
check('team list mine', s == 200 and len(r['teams']) > 0)

s, r = api('POST', '/api/labs/mock/create', {'method':'GET','path':'api/e2e','status_code':200,'response_body':'{"ok":true}'}, t=FT)
check('mock create', s == 200)
s, r = api('GET', '/mock/api/e2e', t=FT)
check('mock response', s == 200 and r.get('ok'))

# ========== PASSWORD FLOW ==========
print('\n=== PASSWORD ===')
s, r = api('POST', '/api/auth/forgot-password', {'email':'ef@t.com'})
check('forgot password', s == 200)

s, r = api('PATCH', '/api/auth/me', {'current_password':'pass1234','new_password':'newpass88'}, t=FT)
check('change password', s == 200)
s, r = get('/api/auth/me', FT)
check('old token revoked after pw change', s == 401)

# ========== SPA / STATIC ==========
print('\n=== STATIC ===')
try:
    with R.urlopen(R.Request(f'{BASE}/'), timeout=10) as resp:
        check('SPA index returns HTML', resp.status == 200 and b'<!DOCTYPE' in resp.read())
except: check('SPA index returns HTML', False)

try:
    with R.urlopen(R.Request(f'{BASE}/health'), timeout=10) as resp:
        d = J.loads(resp.read())
        check('health check ok', d['status'] == 'ok')
except: check('health check ok', False)

print(f'\n===== {ok} PASSED, {fail} FAILED =====')
sys.exit(0 if fail == 0 else 1)
