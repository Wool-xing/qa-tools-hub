import { defineStore } from 'pinia'
import { levels as api } from '../api'

export const useLevelsStore = defineStore('levels', {
  state: () => ({ levels: [], stages: {}, progress: {}, current: null, result: null }),
  actions: {
    async fetchList() {
      const d = await api.list()
      this.levels = d.levels; this.stages = d.stages; this.progress = d.progress
    },
    async fetchLevel(id) {
      this.current = await api.get(id)
      this.result = null
    },
    async submit(levelId, answer) {
      this.result = await api.submit(levelId, answer)
      return this.result
    },
    resetResult() { this.result = null },
  }
})
