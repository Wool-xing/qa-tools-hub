const BASE = ''

function token() { return localStorage.getItem('qa-pro-token') || '' }

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS'])

async function api(method, path, body) {
  const headers = { 'Content-Type': 'application/json' }
  if (token()) headers['Authorization'] = `Bearer ${token()}`
  const opts = { method, headers }
  if (body) opts.body = JSON.stringify(body)
  const maxRetries = SAFE_METHODS.has(method) ? 3 : 1
  let res
  let lastErr
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      res = await fetch(BASE + path, opts)
      break
    } catch (e) {
      lastErr = e
      if (attempt < maxRetries - 1) await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt)))
    }
  }
  if (!res) throw new ApiError('无法连接服务器，请检查网络或后端是否启动', 0)
  if (res.status === 401) {
    localStorage.removeItem('qa-pro-token')
    const current = window.location.pathname
    if (current !== '/login') window.location.href = '/login?redirect=' + encodeURIComponent(current)
    throw new ApiError('登录已过期，请重新登录', 401)
  }
  let data
  try {
    data = await res.json()
  } catch {
    throw new ApiError(`服务器返回异常 (${res.status})`, res.status)
  }
  if (!res.ok) {
    const msg = data.detail || `请求失败 (${res.status})`
    throw new ApiError(msg, res.status)
  }
  return data
}

export const auth = {
  login: (u, p) => api('POST', '/api/auth/login', { username: u, password: p }),
  register: (u, e, p) => api('POST', '/api/auth/register', { username: u, email: e, password: p }),
  me: () => api('GET', '/api/auth/me'),
}

export const levels = {
  list: () => api('GET', '/api/levels'),
  get: (id) => api('GET', '/api/levels/' + id),
  submit: (levelId, answer) => api('POST', '/api/levels/submit', { level_id: levelId, answer }),
  runCode: (levelId, code) => api('POST', '/api/levels/' + levelId + '/run', { level_id: levelId, answer: { code } }),
}

export const labs = {
  sql: (sql, levelId) => api('POST', '/api/labs/sql/execute', { sql, level_id: levelId || 0 }),
  cmd: (cmd, levelId) => api('POST', '/api/labs/cmd/execute', { cmd, level_id: levelId || 0 }),
  performance: (script, vus, duration) => api('POST', '/api/labs/performance/simulate', { script, vus, duration }),
  mock: {
    create: (data) => api('POST', '/api/labs/mock/create', data),
    reset: () => api('POST', '/api/labs/mock/reset'),
    stats: () => api('GET', '/api/labs/mock/stats'),
  },
}

export const analytics = {
  timeline: (days = 90) => api('GET', `/api/analytics/progress-timeline?days=${days}`),
  skillGaps: () => api('GET', '/api/analytics/skill-gaps'),
  achievements: () => api('GET', '/api/analytics/achievements'),
  leaderboard: (period = 'weekly') => api('GET', `/api/analytics/leaderboard?period=${period}`),
}

export const teams = {
  create: (name) => api('POST', '/api/teams', { name }),
  join: (invite_code) => api('POST', '/api/teams/join', { invite_code }),
  mine: () => api('GET', '/api/teams/mine'),
  members: (id) => api('GET', `/api/teams/${id}/members`),
  dashboard: (id) => api('GET', `/api/teams/${id}/dashboard`),
}
