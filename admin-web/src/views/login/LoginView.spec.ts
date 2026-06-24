import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import LoginView from './LoginView.vue'

describe('LoginView', () => {
  it('renders the login copy for administrators', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: LoginView }],
    })

    await router.push('/')
    await router.isReady()

    const wrapper = mount(LoginView, {
      global: {
        plugins: [createPinia(), ElementPlus, router],
      },
    })

    expect(wrapper.text()).toContain('AI思政辅助平台')
    expect(wrapper.text()).toContain('账号')
    expect(wrapper.text()).toContain('密码')
    expect(wrapper.text()).toContain('登录')
  })
})
