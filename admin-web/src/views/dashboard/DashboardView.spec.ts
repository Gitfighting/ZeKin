import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { describe, expect, it, vi } from 'vitest'

import DashboardView from './DashboardView.vue'
import { getDashboard } from '../../api/admin'

vi.mock('../../api/admin', () => ({
  getDashboard: vi.fn(),
}))

describe('DashboardView', () => {
  it('does not render local placeholder metrics when dashboard loading fails', async () => {
    vi.mocked(getDashboard).mockRejectedValue(new Error('network down'))

    const wrapper = mount(DashboardView, {
      global: {
        plugins: [ElementPlus],
      },
    })
    await flushPromises()

    expect(wrapper.text()).not.toContain('晚间任务未确认')
    expect(wrapper.text()).not.toContain('学生侧异常聚类')
    expect(wrapper.text()).not.toContain('自动判定中出现 5 条定位例外')
    expect(wrapper.text()).toContain('暂无监管提醒')
    expect(wrapper.text()).toContain('暂无重点指标')
  })
})
