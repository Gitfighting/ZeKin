import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { describe, expect, it, vi } from 'vitest'

import TeachersView from './TeachersView.vue'
import { getTeachers } from '../../api/admin'

vi.mock('../../api/admin', () => ({
  getTeachers: vi.fn(),
}))

describe('TeachersView', () => {
  it('uses teacher groups from the backend instead of local checkbox examples', async () => {
    vi.mocked(getTeachers).mockResolvedValue({
      total: 1,
      items: [{
        id: 1,
        account: 'teacher',
        name: '李老师',
        teacherNo: 'T2026001',
        department: '软件学院',
        phone: '13800000002',
        groups: ['软件2601'],
      }],
    })

    const wrapper = mount(TeachersView, {
      global: {
        plugins: [ElementPlus],
      },
    })
    await flushPromises()
    await wrapper.findAll('button').find((button) => button.text() === '关联分组')?.trigger('click')

    expect(wrapper.text()).toContain('软件2601')
    expect(wrapper.text()).not.toContain('软工 1 班')
    expect(wrapper.text()).not.toContain('晚自习专项组')
  })
})
