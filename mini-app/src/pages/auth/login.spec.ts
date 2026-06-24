// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import LoginPage from './login.vue'

describe('login page', () => {
  it('renders the student login shell copy', () => {
    const wrapper = mount(LoginPage)

    expect(wrapper.text()).toContain('智慧考勤')
    expect(wrapper.text()).toContain('学号/手机号')
    expect(wrapper.text()).toContain('密码')
    expect(wrapper.text()).toContain('首次激活')
  })
})
