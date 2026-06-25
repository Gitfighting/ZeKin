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

    expect(wrapper.text()).toContain('考勤助手')
    expect(wrapper.text()).toContain('智慧考勤，轻松校园生活')
    expect(wrapper.text()).toContain('注册')
    expect(wrapper.find('.status-bar').exists()).toBe(false)
    expect(wrapper.find('.capsule').exists()).toBe(false)
    expect(wrapper.find('.auth-role').exists()).toBe(false)
    expect(wrapper.find('.tips').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('欢迎回来')
    const inputs = wrapper.findAll('input')
    expect(inputs[0].attributes('placeholder')).toBe('学号/手机号')
    expect(inputs[1].attributes('placeholder')).toBe('密码')
    expect(wrapper.text()).not.toContain('首次激活')
  })

  it('logs in without asking for a student or teacher role', async () => {
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

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('teacher')
    await inputs[1].setValue('teacher123456')
    await wrapper.find('button').trigger('click')
    await Promise.resolve()

    expect(loginSpy).toHaveBeenCalledWith({
      account: 'teacher',
      password: 'teacher123456',
    })
    expect(uni.reLaunch).toHaveBeenCalledWith({ url: '/pages/teacher/home' })
  })

  it('switches to registration and registers a student account', async () => {
    const registerSpy = vi.spyOn(authService, 'activateStudent').mockResolvedValue({
      accessToken: 'student-token',
      user: {
        id: 10,
        userType: 'student',
        displayName: '张三',
        activated: true,
      },
    })
    const wrapper = mount(LoginPage)

    await wrapper.findAll('.tab-btn')[1].trigger('click')
    expect(wrapper.find('.tips').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('欢迎加入')
    expect(wrapper.text()).not.toContain('班级')
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('张三')
    await inputs[1].setValue('20260001')
    await inputs[2].setValue('13800000001')
    await inputs[3].setValue('000000')
    await inputs[4].setValue('student123456')
    await inputs[5].setValue('student123456')
    await wrapper.find('button.primary-btn').trigger('click')
    await Promise.resolve()

    expect(registerSpy).toHaveBeenCalledWith({
      name: '张三',
      studentNo: '20260001',
      phone: '13800000001',
      code: '000000',
      password: 'student123456',
      confirmPassword: 'student123456',
    })
    expect(uni.switchTab).toHaveBeenCalledWith({ url: '/pages/student/home' })
  })

  it('uses visual icons instead of text characters in form fields', async () => {
    const wrapper = mount(LoginPage)

    expect(wrapper.findAll('.field-icon').every((icon) => icon.text() === '')).toBe(true)

    await wrapper.findAll('.tab-btn')[1].trigger('click')

    expect(wrapper.findAll('.field-icon').every((icon) => icon.text() === '')).toBe(true)
  })

  it('keeps the user on login and shows an error when authentication fails', async () => {
    vi.spyOn(authService, 'login').mockRejectedValue(new Error('账号或密码错误'))
    const persistSpy = vi.spyOn(authService, 'persistAuthSession')
    const wrapper = mount(LoginPage)

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('student')
    await inputs[1].setValue('bad-password')
    await wrapper.find('button').trigger('click')
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
