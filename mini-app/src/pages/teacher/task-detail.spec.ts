// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import TaskDetailPage from './task-detail.vue'
import * as teacherService from '@/services/teacher'

describe('teacher task detail page', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.stubGlobal('uni', {
      navigateTo: vi.fn(),
      request: vi.fn(),
      showToast: vi.fn(),
    })
    vi.stubGlobal('getCurrentPages', () => [{ options: { id: '8' } }])
  })

  it('does not render demo students when task detail loading fails', async () => {
    vi.spyOn(teacherService, 'getTeacherTaskDetail').mockRejectedValue(new Error('network down'))

    const wrapper = mount(TaskDetailPage)
    await Promise.resolve()
    await Promise.resolve()

    expect(wrapper.text()).not.toContain('李明')
    expect(wrapper.text()).not.toContain('张悦')
    expect(wrapper.text()).not.toContain('王辰')
    expect(uni.showToast).toHaveBeenCalledWith({
      title: 'network down',
      icon: 'none',
    })
  })
})
