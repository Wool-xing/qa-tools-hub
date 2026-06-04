import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BackToTop from '../BackToTop.vue'

describe('BackToTop', () => {
  let addEventListenerSpy, removeEventListenerSpy

  beforeEach(() => {
    addEventListenerSpy = vi.spyOn(window, 'addEventListener')
    removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')
  })

  afterEach(() => {
    addEventListenerSpy.mockRestore()
    removeEventListenerSpy.mockRestore()
  })

  it('registers scroll listener on mount', () => {
    mount(BackToTop)
    expect(addEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function), { passive: true })
  })

  it('removes scroll listener on unmount', () => {
    const wrapper = mount(BackToTop)
    const handler = addEventListenerSpy.mock.calls[0][1]
    wrapper.unmount()
    expect(removeEventListenerSpy).toHaveBeenCalledWith('scroll', handler)
  })

  it('button hidden when scrollY <= 400', () => {
    window.scrollY = 0
    const wrapper = mount(BackToTop)
    expect(wrapper.find('button').isVisible()).toBe(false)
  })

  it('button visible when scrollY > 400', async () => {
    const wrapper = mount(BackToTop)
    window.scrollY = 500
    // trigger the scroll handler
    const handler = addEventListenerSpy.mock.calls[0][1]
    handler()
    await wrapper.vm.$nextTick()
    expect(wrapper.find('button').isVisible()).toBe(true)
  })

  it('calls window.scrollTo on click', async () => {
    const scrollToSpy = vi.spyOn(window, 'scrollTo').mockImplementation(() => {})
    const wrapper = mount(BackToTop)
    window.scrollY = 500
    const handler = addEventListenerSpy.mock.calls[0][1]
    handler()
    await wrapper.vm.$nextTick()
    await wrapper.find('button').trigger('click')
    expect(scrollToSpy).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' })
    scrollToSpy.mockRestore()
  })

  it('has aria-label for accessibility', () => {
    const wrapper = mount(BackToTop)
    expect(wrapper.find('button').attributes('aria-label')).toBe('回到顶部')
  })
})
