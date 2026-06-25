import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { describe, expect, it, vi } from 'vitest'

import CheckinTypesView from './CheckinTypesView.vue'
import { getCheckinTypes } from '../../api/admin'

vi.mock('../../api/admin', () => ({
  getCheckinTypes: vi.fn(),
}))

describe('CheckinTypesView', () => {
  it('does not render local check-in type examples when loading fails', async () => {
    vi.mocked(getCheckinTypes).mockRejectedValue(new Error('network down'))

    const wrapper = mount(CheckinTypesView, {
      global: {
        plugins: [ElementPlus],
      },
    })
    await flushPromises()

    expect(wrapper.text()).not.toContain('晨读签到')
    expect(wrapper.text()).not.toContain('TEMP_EVENT')
    expect(wrapper.text()).toContain('暂无数据')
  })
})
