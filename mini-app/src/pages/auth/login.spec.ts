// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import LoginPage from './login.vue'
import * as authService from '@/services/auth'

describe('login page', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.stubGlobal('uni', {
      navigateTo: vi.fn(),
      reLaunch: vi.fn(),
      setStorageSync: vi.fn(),
      switchTab: vi.fn(),
      showToast: vi.fn(),
    })
  })

  it('renders the student login shell copy', () => {
    const wrapper = mount(LoginPage)

    expect(wrapper.text()).toContain('智慧考勤')
    expect(wrapper.text()).toContain('学号/手机号')
    expect(wrapper.text()).toContain('密码')
    expect(wrapper.text()).toContain('首次激活')
  })

  it('sends the selected teacher role and relaunches into the teacher home page', async () => {
    const loginSpy = vi.spyOn(authService, 'login').mockResolvedValue({
      accessToken: 'teacher-token',
      user: {
        id: 2,
        userType: 'teacher',
        displayName: '李老师',
        activated: true,
      },
    })
    const wrapper = mount(LoginPage)

    await wrapper.findAll('.auth-role__item')[1].trigger('click')
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('teacher')
    await inputs[1].setValue('teacher123456')
    await wrapper.find('button').trigger('click')
    await Promise.resolve()

    expect(loginSpy).toHaveBeenCalledWith({
      account: 'teacher',
      password: 'teacher123456',
      userType: 'teacher',
    })
    expect(uni.reLaunch).toHaveBeenCalledWith({ url: '/pages/teacher/home' })
  })
})
