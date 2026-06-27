import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import TaskCreatePage from './task-create.vue'

describe('teacher task create page', () => {
  it('renders the wizard creation steps', () => {
    const wrapper = mount(TaskCreatePage)

    expect(wrapper.text()).toContain('创建考勤任务')
    expect(wrapper.text()).toContain('任务设置')
    expect(wrapper.text()).toContain('规则设置')
    expect(wrapper.text()).toContain('确认发布')
    expect(wrapper.text()).toContain('发布对象')
    expect(wrapper.text()).toContain('下一步')
  })

  it('does not preselect local demo task data before backend groups load', () => {
    const wrapper = mount(TaskCreatePage)

    expect(wrapper.text()).not.toContain('课堂考勤模板')
    expect(wrapper.text()).not.toContain('2026-06-24')
    expect(wrapper.text()).toContain('选择班级/学生')
  })
})
