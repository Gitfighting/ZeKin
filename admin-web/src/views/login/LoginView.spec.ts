import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { createPinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import LoginView from './LoginView.vue'
import { useAuthStore } from '../../stores/auth'

describe('LoginView', () => {
  it('renders the login copy for administrators', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: LoginView }],
    })

    await router.push('/')
    await router.isReady()

    const wrapper = mount(LoginView, {
      global: {
        plugins: [createPinia(), ElementPlus, router],
      },
    })

    expect(wrapper.text()).toContain('AI思政辅助平台')
    expect(wrapper.text()).toContain('账号')
    expect(wrapper.text()).toContain('密码')
    expect(wrapper.text()).toContain('登录')
  })

  it('authenticates against the backend admin role', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'login', component: LoginView },
        { path: '/dashboard', name: 'dashboard', component: { template: '<div />' } },
      ],
    })
    const pinia = createPinia()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(LoginView, {
      global: {
        plugins: [pinia, ElementPlus, router],
      },
    })
    const authStore = useAuthStore()
    const loginSpy = vi.spyOn(authStore, 'login').mockResolvedValue()

    await wrapper.find('input[placeholder="请输入账号"]').setValue('admin')
    await wrapper.find('input[placeholder="请输入密码"]').setValue('admin123456')
    await wrapper.find('.login-view__submit').trigger('click')

    expect(loginSpy).toHaveBeenCalledWith('admin', 'admin123456')
  })
})
