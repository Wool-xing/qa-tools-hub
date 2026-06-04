import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { h } from 'vue'
import Breadcrumb from '../Breadcrumb.vue'

const Dummy = { render: () => h('div') }

async function mountAt(path) {
  const routes = [
    { path: '/', name: 'home', component: Dummy },
    { path: '/dashboard', name: 'dashboard', component: Dummy },
    { path: '/levels', name: 'levels', component: Dummy },
    { path: '/level/:id', name: 'level', component: Dummy },
    { path: '/labs', name: 'labs', component: Dummy },
    { path: '/labs/sql', name: 'sql-lab', component: Dummy },
    { path: '/labs/linux', name: 'cmd-lab', component: Dummy },
    { path: '/teams', name: 'teams', component: Dummy },
    { path: '/testcases', name: 'testcases', component: Dummy },
  ]
  const router = createRouter({ history: createWebHistory(), routes })
  await router.push(path)
  await router.isReady()
  return mount(Breadcrumb, { global: { plugins: [router] } })
}

describe('Breadcrumb', () => {
  it('renders home link on all pages', async () => {
    const wrapper = await mountAt('/dashboard')
    expect(wrapper.text()).toContain('首页')
  })

  it('shows dashboard label on /dashboard', async () => {
    const wrapper = await mountAt('/dashboard')
    expect(wrapper.text()).toContain('仪表板')
  })

  it('shows level breadcrumb on /level/:id', async () => {
    const wrapper = await mountAt('/level/5')
    expect(wrapper.text()).toContain('闯关学习')
    expect(wrapper.text()).toContain('关卡 #5')
  })

  it('shows lab breadcrumb on /labs/sql', async () => {
    const wrapper = await mountAt('/labs/sql')
    expect(wrapper.text()).toContain('实验室')
    expect(wrapper.text()).toContain('SQL 练习场')
  })

  it('shows no extra crumbs on home page', async () => {
    const wrapper = await mountAt('/')
    const crumbs = wrapper.findAll('.crumb')
    expect(crumbs).toHaveLength(1)
  })

  it('falls back to route name for unknown lab', async () => {
    const router = createRouter({ history: createWebHistory(), routes: [
      { path: '/', name: 'home', component: Dummy },
      { path: '/labs/unknown-lab', name: 'unknown-lab', component: Dummy },
    ]})
    await router.push('/labs/unknown-lab')
    await router.isReady()
    const wrapper = mount(Breadcrumb, { global: { plugins: [router] } })
    expect(wrapper.text()).toContain('实验室')
    expect(wrapper.text()).toContain('unknown-lab')
  })
})
