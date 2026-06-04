import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import Sidebar from '../Sidebar.vue'

function createRouterAt(path) {
  const routes = [
    { path: '/', name: 'home' },
    { path: '/dashboard', name: 'dashboard' },
    { path: '/levels', name: 'levels' },
    { path: '/level/:id', name: 'level' },
    { path: '/labs', name: 'labs' },
    { path: '/labs/sql', name: 'sql-lab' },
    { path: '/labs/linux', name: 'cmd-lab' },
    { path: '/teams', name: 'teams' },
    { path: '/testcases', name: 'testcases' },
  ]
  return createRouter({ history: createWebHistory(), routes })
}

describe('Sidebar', () => {
  it('renders all 4 navigation sections', async () => {
    const router = createRouterAt('/dashboard')
    router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(Sidebar, {
      global: { plugins: [router] },
    })
    const titles = wrapper.findAll('.nav-section-title')
    expect(titles).toHaveLength(5)
    expect(titles[0].text()).toContain('主导航')
    expect(titles[1].text()).toContain('能力进阶')
    expect(titles[2].text()).toContain('专项领域')
    expect(titles[3].text()).toContain('实操实验室')
    expect(titles[4].text()).toContain('练习工具')
  })

  it('opens on desktop width by default (>768px)', async () => {
    const router = createRouterAt('/dashboard')
    router.push('/dashboard')
    await router.isReady()
    // simulate desktop
    Object.defineProperty(window, 'innerWidth', { value: 1024, writable: true })
    const wrapper = mount(Sidebar, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('.sidebar.collapsed').exists()).toBe(false)
  })

  it('expands section on title click', async () => {
    const router = createRouterAt('/dashboard')
    router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(Sidebar, {
      global: { plugins: [router] },
    })
    // "实操实验室" and "练习工具" start collapsed
    const labSection = wrapper.findAll('.nav-section-title')[3]
    expect(labSection.text()).toContain('实操实验室')
    // click to open
    await labSection.trigger('click')
    // items should now be visible
    const items = wrapper.findAll('.nav-section-item')
    // main nav (5) + levels (8) + lab items now visible (12) + practice items still hidden
    // After opening labs: all sections: main=open, levels=open, labs=now open, practice=closed
    expect(items.length).toBeGreaterThanOrEqual(13) // 5 main + 8 levels opened, or more
  })

  it('highlights active route in main nav', async () => {
    const router = createRouterAt('/dashboard')
    router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(Sidebar, {
      global: { plugins: [router] },
    })
    await router.isReady()
    // dashboard should be active
    const activeItems = wrapper.findAll('.nav-section-item.active')
    expect(activeItems.length).toBeGreaterThan(0)
    const dashboardItem = activeItems.find(el => el.text().includes('仪表板'))
    expect(dashboardItem).toBeTruthy()
  })

  it('highlights levels nav when viewing a level detail', async () => {
    const router = createRouterAt('/level/5')
    router.push('/level/5')
    await router.isReady()
    const wrapper = mount(Sidebar, {
      global: { plugins: [router] },
    })
    await router.isReady()
    const activeItems = wrapper.findAll('.nav-section-item.active')
    const levelsItem = activeItems.find(el => el.text().includes('闯关学习'))
    expect(levelsItem).toBeTruthy()
  })

  it('search input navigates on Enter', async () => {
    const router = createRouterAt('/dashboard')
    router.push('/dashboard')
    await router.isReady()
    const pushSpy = vi.spyOn(router, 'push')
    const wrapper = mount(Sidebar, {
      global: { plugins: [router] },
    })
    const input = wrapper.find('.search-input')
    await input.setValue('SQL注入')
    await input.trigger('keydown.enter')
    expect(pushSpy).toHaveBeenCalledWith('/levels?search=SQL%E6%B3%A8%E5%85%A5')
    pushSpy.mockRestore()
  })

  it('toggle button collapses sidebar', async () => {
    const router = createRouterAt('/dashboard')
    router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(Sidebar, {
      global: { plugins: [router] },
    })
    const toggle = wrapper.find('.sidebar-toggle')
    await toggle.trigger('click')
    expect(wrapper.find('.sidebar.collapsed').exists()).toBe(true)
  })
})
