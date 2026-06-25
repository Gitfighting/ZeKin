import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import TeacherProfilePage from './profile.vue'

describe('teacher profile page', () => {
  beforeEach(() => {
    vi.stubGlobal('uni', {
      getStorageSync: vi.fn(),
      removeStorageSync: vi.fn(),
      request: undefined,
      showModal: vi.fn(({ success }) => success?.({ confirm: true })),
      reLaunch: vi.fn(),
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('clears the session and returns to login when logging out', async () => {
    const wrapper = mount(TeacherProfilePage)

    await wrapper.find('.logout-button').trigger('click')

    expect(uni.removeStorageSync).toHaveBeenCalledWith('access_token')
    expect(uni.removeStorageSync).toHaveBeenCalledWith('student_auth_user')
    expect(uni.removeStorageSync).toHaveBeenCalledWith('student_profile')
    expect(uni.removeStorageSync).toHaveBeenCalledWith('user_profile')
    expect(uni.reLaunch).toHaveBeenCalledWith({ url: '/pages/auth/login' })
  })
})
