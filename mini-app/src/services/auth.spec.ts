// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { login } from './auth'

describe('auth service', () => {
  beforeEach(() => {
    vi.stubGlobal('uni', {
      getStorageSync: vi.fn(),
      request: vi.fn(),
      setStorageSync: vi.fn(),
    })
  })

  it('passes the selected user type to the backend login endpoint', async () => {
    vi.mocked(uni.request).mockImplementation((options) => {
      options.success?.({
        statusCode: 200,
        data: {
          data: {
            access_token: 'teacher-token',
            token_type: 'bearer',
            user: {
              id: 2,
              user_type: 'teacher',
              display_name: '李老师',
            },
          },
          message: 'ok',
        },
      } as UniApp.RequestSuccessCallbackResult)
      return {} as UniApp.RequestTask
    })

    await login({
      account: 'teacher',
      password: 'teacher123456',
      userType: 'teacher',
    })

    expect(uni.request).toHaveBeenCalledWith(
      expect.objectContaining({
        url: 'http://localhost:8000/api/auth/login',
        method: 'POST',
        data: expect.objectContaining({
          account: 'teacher',
          password: 'teacher123456',
          user_type: 'teacher',
        }),
      }),
    )
    expect(uni.setStorageSync).toHaveBeenCalledWith('access_token', 'teacher-token')
  })
})
