import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { describe, expect, it, vi } from 'vitest'

import RuleTemplatesView from './RuleTemplatesView.vue'
import { getRuleTemplates } from '../../api/admin'

vi.mock('../../api/admin', () => ({
  getRuleTemplates: vi.fn(),
}))

describe('RuleTemplatesView', () => {
  it('does not render local rule examples when loading fails', async () => {
    vi.mocked(getRuleTemplates).mockRejectedValue(new Error('network down'))

    const wrapper = mount(RuleTemplatesView, {
      global: {
        plugins: [ElementPlus],
      },
    })
    await flushPromises()

    expect(wrapper.text()).not.toContain('工作日 06:40-07:20')
    expect(wrapper.text()).not.toContain('定位、设备与人脸三项')
    expect(wrapper.text()).toContain('暂无数据')
  })
})
