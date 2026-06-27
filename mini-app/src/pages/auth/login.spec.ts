// @vitest-environment jsdom
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import LoginPage from './login.vue'
import * as authService from '@/services/auth'

vi.mock('@/utils/captcha', () => ({
  createCaptchaCode: () => 'A2B3',
  buildCaptchaDisplay: (code: string) =>
    code.split('').map((char, index) => ({
      char,
      color: '#0877f2',
      rotate: 0,
      fontSize: 24,
      offsetY: 0,
    })),
}))

describe('login page', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.restoreAllMocks()
    vi.stubGlobal('uni', {
      navigateTo: vi.fn(),
      redirectTo: vi.fn(),
      reLaunch: vi.fn(),
      setStorageSync: vi.fn(),
      switchTab: vi.fn(),
      showToast: vi.fn(),
      loadFontFace: vi.fn(({ success }: { success?: () => void }) => success?.()),
    })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  async function mountLoginPage() {
    const wrapper = mount(LoginPage)
    await vi.advanceTimersByTimeAsync(300)
    await flushPromises()
    return wrapper
  }

  it('renders the login template shell', async () => {
    const wrapper = await mountLoginPage()

    expect(wrapper.text()).toContain('知勤')
    expect(wrapper.text()).toContain('欢迎回来')
    expect(wrapper.text()).toContain('登录')
    expect(wrapper.text()).toContain('记住登录')
    expect(wrapper.text()).not.toContain('考勤助手')
    expect(wrapper.text()).toContain('注册')
    expect(wrapper.text()).not.toContain('获取验证码')
    const inputs = wrapper.findAll('input')
    expect(inputs[2].attributes('placeholder')).toBe('验证码')
    expect(wrapper.findAll('.captcha-char')).toHaveLength(4)
  })

  it('logs in after entering the correct captcha', async () => {
    const loginSpy = vi.spyOn(authService, 'login').mockResolvedValue({
      accessToken: 'teacher-token',
      user: {
        id: 2,
        userType: 'teacher',
        displayName: '李老师',
        activated: true,
      },
    })
    const wrapper = await mountLoginPage()

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('20261001')
    await inputs[1].setValue('123456')
    await inputs[2].setValue('A2B3')
    await wrapper.find('.primary-btn').trigger('click')
    await Promise.resolve()

    expect(loginSpy).toHaveBeenCalledWith({
      account: '20261001',
      password: '123456',
    })
    expect(uni.reLaunch).toHaveBeenCalledWith({ url: '/pages/teacher/home' })
  })

  it('blocks login when captcha is wrong', async () => {
    const loginSpy = vi.spyOn(authService, 'login').mockResolvedValue({
      accessToken: 'token',
      user: {
        id: 1,
        userType: 'student',
        displayName: '张三',
        activated: true,
      },
    })
    const wrapper = await mountLoginPage()

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('20260001')
    await inputs[1].setValue('123456')
    await inputs[2].setValue('0000')
    await wrapper.find('.primary-btn').trigger('click')
    await Promise.resolve()

    expect(loginSpy).not.toHaveBeenCalled()
    expect(uni.showToast).toHaveBeenCalledWith({
      title: '验证码错误，请重试',
      icon: 'none',
    })
  })

  it('keeps the user on login and shows an error when authentication fails', async () => {
    vi.spyOn(authService, 'login').mockRejectedValue(new Error('账号或密码错误'))
    const persistSpy = vi.spyOn(authService, 'persistAuthSession')
    const wrapper = await mountLoginPage()

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('20260001')
    await inputs[1].setValue('bad-password')
    await inputs[2].setValue('A2B3')
    await wrapper.find('.primary-btn').trigger('click')
    await Promise.resolve()

    expect(persistSpy).not.toHaveBeenCalled()
    expect(uni.switchTab).not.toHaveBeenCalled()
    expect(uni.reLaunch).not.toHaveBeenCalled()
    expect(uni.showToast).toHaveBeenCalledWith({
      title: '账号或密码错误',
      icon: 'none',
    })
  })
})
