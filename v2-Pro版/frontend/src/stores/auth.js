import { defineStore } from 'pinia'
import { auth as api } from '../api'
import { LS_TOKEN, LS_IS_ADMIN } from '../constants'

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null, token: localStorage.getItem(LS_TOKEN) || '' }),
  getters: { isLoggedIn: (s) => !!s.token },
  actions: {
    async restore() {
      if (!this.token) return
      try { this.user = await api.me(); localStorage.setItem(LS_IS_ADMIN, this.user?.is_admin ? '1' : '0') }
      catch { this.token = ''; localStorage.removeItem(LS_TOKEN) }
    },
    async login(username, password) {
      const d = await api.login(username, password)
      this.token = d.access_token
      localStorage.setItem(LS_TOKEN, d.access_token)
      try { this.user = await api.me(); localStorage.setItem(LS_IS_ADMIN, this.user?.is_admin ? '1' : '0') } catch { this.user = { id: d.user_id, username: d.username } }
    },
    async register(username, email, password) {
      const d = await api.register(username, email, password)
      this.token = d.access_token
      localStorage.setItem(LS_TOKEN, d.access_token)
      try { this.user = await api.me(); localStorage.setItem(LS_IS_ADMIN, this.user?.is_admin ? '1' : '0') } catch { this.user = { id: d.user_id, username: d.username } }
    },
    logout() { this.token = ''; this.user = null; localStorage.removeItem(LS_TOKEN); localStorage.removeItem(LS_IS_ADMIN) },
  }
})
