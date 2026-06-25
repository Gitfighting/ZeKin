// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { request } from './request'

describe('request auth guard', () => {
  beforeEach(() => {
    vi.stubGlobal('uni', {
      getStorageSync: vi.fn(),
      removeStorageSync: vi.fn(),
      request: vi.fn(),
      reLaunch: vi.fn(),
    })
  })

  it('redirects to login without sending protected requests when there is no token', async () => {
    vi.mocked(uni.getStorageSync).mockReturnValue('')
    vi.mocked(uni.request).mockImplementation((options) => {
      options.fail?.({ errMsg: 'request should not be sent without auth' } as UniApp.GeneralCallbackResult)
      return {} as UniApp.RequestTask
    })

    await expect(request({ url: '/student/tasks', method: 'GET' })).rejects.toMatchObject({
      name: 'AuthRequiredError',
    })

    expect(uni.request).not.toHaveBeenCalled()
    expect(uni.removeStorageSync).toHaveBeenCalledWith('access_token')
    expect(uni.removeStorageSync).toHaveBeenCalledWith('student_auth_user')
    expect(uni.reLaunch).toHaveBeenCalledWith({ url: '/pages/auth/login' })
  })

  it('clears the session and redirects to login when the backend rejects auth', async () => {
    vi.mocked(uni.getStorageSync).mockReturnValue('expired-token')
    vi.mocked(uni.request).mockImplementation((options) => {
      options.success?.({
        statusCode: 401,
        data: { detail: '未登录' },
      } as UniApp.RequestSuccessCallbackResult)
      return {} as UniApp.RequestTask
    })

    await expect(request({ url: '/student/tasks', method: 'GET' })).rejects.toMatchObject({
      name: 'AuthRequiredError',
    })

    expect(uni.removeStorageSync).toHaveBeenCalledWith('access_token')
    expect(uni.reLaunch).toHaveBeenCalledWith({ url: '/pages/auth/login' })
  })
})
