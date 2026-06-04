import { defineStore } from 'pinia'
import { auth as api } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null, token: localStorage.getItem('qa-pro-token') || '' }),
  getters: { isLoggedIn: (s) => !!s.token },
  actions: {
    async restore() {
      if (!this.token) return
      try { this.user = await api.me(); localStorage.setItem('qa-pro-is-admin', this.user?.is_admin ? '1' : '0') }
      catch { this.token = ''; localStorage.removeItem('qa-pro-token') }
    },
    async login(username, password) {
      const d = await api.login(username, password)
      this.token = d.access_token
      localStorage.setItem('qa-pro-token', d.access_token)
      try { this.user = await api.me(); localStorage.setItem('qa-pro-is-admin', this.user?.is_admin ? '1' : '0') } catch { this.user = { id: d.user_id, username: d.username } }
    },
    async register(username, email, password) {
      const d = await api.register(username, email, password)
      this.token = d.access_token
      localStorage.setItem('qa-pro-token', d.access_token)
      try { this.user = await api.me(); localStorage.setItem('qa-pro-is-admin', this.user?.is_admin ? '1' : '0') } catch { this.user = { id: d.user_id, username: d.username } }
    },
    logout() { this.token = ''; this.user = null; localStorage.removeItem('qa-pro-token'); localStorage.removeItem('qa-pro-is-admin') },
  }
})
