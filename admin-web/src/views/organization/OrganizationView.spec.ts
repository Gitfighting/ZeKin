import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { describe, expect, it, vi } from 'vitest'

import OrganizationView from './OrganizationView.vue'
import { getOrgTree } from '../../api/admin'

vi.mock('../../api/admin', () => ({
  getOrgTree: vi.fn(),
}))

describe('OrganizationView', () => {
  it('does not render local organization examples when loading fails', async () => {
    vi.mocked(getOrgTree).mockRejectedValue(new Error('network down'))

    const wrapper = mount(OrganizationView, {
      global: {
        plugins: [ElementPlus],
      },
    })
    await flushPromises()

    expect(wrapper.text()).not.toContain('软工 1 班')
    expect(wrapper.text()).not.toContain('张老师')
    expect(wrapper.text()).toContain('暂无组织数据')
  })
})
