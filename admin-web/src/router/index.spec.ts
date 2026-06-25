import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import router from './index'

describe('admin router auth boundary', () => {
  beforeEach(async () => {
    localStorage.clear()
    setActivePinia(createPinia())
    await router.push('/login')
  })

  it('redirects unauthenticated admin routes to login', async () => {
    await router.push('/students')

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/students')
  })

  it('does not crash when stored admin user JSON is malformed', async () => {
    localStorage.setItem('admin_user', '{')

    await expect(router.push('/students')).resolves.toBeUndefined()
    expect(router.currentRoute.value.name).toBe('login')
  })
})
