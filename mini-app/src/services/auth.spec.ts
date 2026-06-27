// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activateStudent, login } from './auth'

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
      account: '20261001',
      password: '123456',
      userType: 'teacher',
    })

    expect(uni.request).toHaveBeenCalledWith(
      expect.objectContaining({
        url: 'http://192.168.165.19:8000/api/auth/login',
        method: 'POST',
        data: expect.objectContaining({
          account: '20261001',
          password: '123456',
          user_type: 'teacher',
        }),
      }),
    )
    expect(uni.setStorageSync).toHaveBeenCalledWith('access_token', 'teacher-token')
  })

  it('omits the user type when the mini app login lets the backend resolve the role', async () => {
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
      account: '20261001',
      password: '123456',
    })

    const requestOptions = vi.mocked(uni.request).mock.calls[0][0]
    expect(requestOptions.data).toEqual({
      account: '20261001',
      username: 'teacher',
      password: '123456',
    })
  })

  it('registers a student through the backend student activation endpoint', async () => {
    vi.mocked(uni.request).mockImplementation((options) => {
      options.success?.({
        statusCode: 200,
        data: {
          data: {
            access_token: 'student-token',
            token_type: 'bearer',
            user: {
              id: 10,
              user_type: 'student',
              display_name: '张三',
            },
          },
          message: 'ok',
        },
      } as UniApp.RequestSuccessCallbackResult)
      return {} as UniApp.RequestTask
    })

    await activateStudent({
      name: '张三',
      studentNo: '20260001',
      phone: '13800000001',
      code: '000000',
      password: '123456',
      confirmPassword: '123456',
    })

    expect(uni.request).toHaveBeenCalledWith(
      expect.objectContaining({
        url: 'http://192.168.165.19:8000/api/auth/student/activate',
        method: 'POST',
        data: {
          name: '张三',
          student_no: '20260001',
          phone: '13800000001',
          code: '000000',
          password: '123456',
        },
      }),
    )
    expect(uni.setStorageSync).toHaveBeenCalledWith('access_token', 'student-token')
  })
})
