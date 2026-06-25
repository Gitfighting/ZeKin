import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import TaskCreatePage from './task-create.vue'

describe('teacher task create page', () => {
  it('renders the template-first creation steps', () => {
    const wrapper = mount(TaskCreatePage)

    expect(wrapper.text()).toContain('基础信息')
    expect(wrapper.text()).toContain('选择分组')
    expect(wrapper.text()).toContain('选择模板')
    expect(wrapper.text()).toContain('确认发布')
  })

  it('does not preselect local demo task data before backend groups load', () => {
    const wrapper = mount(TaskCreatePage)

    expect(wrapper.text()).not.toContain('课堂考勤模板')
    expect(wrapper.text()).not.toContain('2026-06-24')
    expect(wrapper.text()).toContain('暂无可选分组')
  })
})
