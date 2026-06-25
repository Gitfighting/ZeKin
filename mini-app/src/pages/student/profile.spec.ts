import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@dcloudio/uni-app', () => ({
  onShow: vi.fn(),
}))

import StudentProfilePage from './profile.vue'

describe('student profile page', () => {
  beforeEach(() => {
    vi.stubGlobal('uni', {
      getStorageSync: vi.fn(),
      removeStorageSync: vi.fn(),
      showModal: vi.fn(({ success }) => success?.({ confirm: true })),
      reLaunch: vi.fn(),
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('clears the session and returns to login when logging out', async () => {
    const wrapper = mount(StudentProfilePage)

    await wrapper.find('.profile-page__logout').trigger('click')

    expect(uni.removeStorageSync).toHaveBeenCalledWith('access_token')
    expect(uni.removeStorageSync).toHaveBeenCalledWith('student_auth_user')
    expect(uni.removeStorageSync).toHaveBeenCalledWith('student_profile')
    expect(uni.removeStorageSync).toHaveBeenCalledWith('user_profile')
    expect(uni.reLaunch).toHaveBeenCalledWith({ url: '/pages/auth/login' })
  })
})
