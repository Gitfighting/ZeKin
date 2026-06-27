import { mount } from '@vue/test-utils'
import ElementPlus, { ElMessage } from 'element-plus'
import { createPinia } from 'pinia'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import LoginView from './LoginView.vue'
import { useAuthStore } from '../../stores/auth'

describe('LoginView', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

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

    expect(wrapper.text()).toContain('知勤')
    expect(wrapper.text()).toContain('管理员登录')
    expect(wrapper.text()).toContain('立即登录')

    const placeholders = wrapper.findAll('.el-input__inner').map((input) => input.attributes('placeholder'))
    expect(placeholders).toContain('请输入账号')
    expect(placeholders).toContain('请输入密码')
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

    const inputs = wrapper.findAll('.el-input__inner')
    await inputs[0].setValue('admin')
    await inputs[1].setValue('123456')

    const captchaComponent = wrapper.findComponent({ name: 'CaptchaImage' })
    const captchaCode = captchaComponent.emitted('change')?.[0]?.[0] as string
    await inputs[2].setValue(captchaCode)

    await wrapper.find('.login-view__submit').trigger('click')

    expect(loginSpy).toHaveBeenCalledWith('admin', '123456')
  })

  it('requires an explicit account instead of falling back to admin', async () => {
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
    const messageSpy = vi.spyOn(ElMessage, 'error').mockImplementation(() => undefined as never)

    const inputs = wrapper.findAll('.el-input__inner')
    await inputs[1].setValue('123456')
    await wrapper.find('.login-view__submit').trigger('click')

    expect(loginSpy).not.toHaveBeenCalled()
    expect(messageSpy).toHaveBeenCalledWith('请输入账号和密码')
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('shows the backend login failure reason', async () => {
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
    vi.spyOn(authStore, 'login').mockRejectedValue(new Error('账号或密码错误'))
    const messageSpy = vi.spyOn(ElMessage, 'error').mockImplementation(() => undefined as never)

    const inputs = wrapper.findAll('.el-input__inner')
    await inputs[0].setValue('admin')
    await inputs[1].setValue('bad-password')

    const captchaComponent = wrapper.findComponent({ name: 'CaptchaImage' })
    const captchaCode = captchaComponent.emitted('change')?.[0]?.[0] as string
    await inputs[2].setValue(captchaCode)

    await wrapper.find('.login-view__submit').trigger('click')

    expect(messageSpy).toHaveBeenCalledWith('账号或密码错误')
    expect(router.currentRoute.value.name).toBe('login')
  })
})
