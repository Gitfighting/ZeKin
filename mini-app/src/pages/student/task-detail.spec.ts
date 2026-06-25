// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@dcloudio/uni-app', () => ({
  onLoad: vi.fn(),
}))

import TaskDetailPage from './task-detail.vue'

describe('student task detail page', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.stubGlobal('uni', {
      navigateBack: vi.fn(),
      navigateTo: vi.fn(),
      switchTab: vi.fn(),
      showToast: vi.fn(),
    })
  })

  it('returns to the student task tab instead of the login page when login is behind it', async () => {
    vi.stubGlobal('getCurrentPages', () => [
      { route: 'pages/auth/login' },
      { route: 'pages/student/task-detail' },
    ])
    const wrapper = mount(TaskDetailPage)

    await wrapper.find('.detail-page__back').trigger('click')

    expect(uni.navigateBack).not.toHaveBeenCalled()
    expect(uni.switchTab).toHaveBeenCalledWith({ url: '/pages/student/tasks' })
  })

  it('uses normal navigateBack when the previous page is not login', async () => {
    vi.stubGlobal('getCurrentPages', () => [
      { route: 'pages/student/tasks' },
      { route: 'pages/student/task-detail' },
    ])
    const wrapper = mount(TaskDetailPage)

    await wrapper.find('.detail-page__back').trigger('click')

    expect(uni.navigateBack).toHaveBeenCalledWith({ delta: 1 })
    expect(uni.switchTab).not.toHaveBeenCalled()
  })
})
