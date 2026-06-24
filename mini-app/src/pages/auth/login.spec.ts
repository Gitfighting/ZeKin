import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import LoginPage from './login.vue'

describe('login page', () => {
  it('shows the student auth entry copy', () => {
    const wrapper = mount(LoginPage)

    expect(wrapper.text()).toContain('智慧考勤')
    expect(wrapper.text()).toContain('学号/手机号')
    expect(wrapper.text()).toContain('密码')
    expect(wrapper.text()).toContain('首次激活')
  })
})
