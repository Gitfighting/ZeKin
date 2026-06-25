// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { getCurrentLocation } from './location'

function resolveGetLocation(longitude = 120.01, latitude = 30.02) {
  vi.mocked(uni.getLocation).mockImplementation((options) => {
    options.success?.({ longitude, latitude } as UniApp.GetLocationSuccess)
  })
}

describe('location service', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.stubGlobal('uni', {
      authorize: vi.fn(),
      getLocation: vi.fn(),
      getSetting: vi.fn(),
      openSetting: vi.fn(),
      showModal: vi.fn(),
    })
  })

  it('gets location immediately when location permission is already granted', async () => {
    vi.mocked(uni.getSetting).mockImplementation((options) => {
      options.success?.({
        authSetting: {
          'scope.userLocation': true,
        },
      } as UniApp.GetSettingSuccessResult)
    })
    resolveGetLocation()

    await expect(getCurrentLocation()).resolves.toEqual({
      longitude: 120.01,
      latitude: 30.02,
    })

    expect(uni.authorize).not.toHaveBeenCalled()
    expect(uni.openSetting).not.toHaveBeenCalled()
  })

  it('requests location permission before the first location lookup', async () => {
    vi.mocked(uni.getSetting).mockImplementation((options) => {
      options.success?.({ authSetting: {} } as UniApp.GetSettingSuccessResult)
    })
    vi.mocked(uni.authorize).mockImplementation((options) => {
      options.success?.({ errMsg: 'authorize:ok' } as UniApp.GeneralCallbackResult)
    })
    resolveGetLocation()

    await getCurrentLocation()

    expect(uni.authorize).toHaveBeenCalledWith(
      expect.objectContaining({
        scope: 'scope.userLocation',
      }),
    )
    expect(uni.getLocation).toHaveBeenCalled()
  })

  it('opens settings after a previous location denial and then gets location', async () => {
    vi.mocked(uni.getSetting).mockImplementation((options) => {
      options.success?.({
        authSetting: {
          'scope.userLocation': false,
        },
      } as UniApp.GetSettingSuccessResult)
    })
    vi.mocked(uni.showModal).mockImplementation((options) => {
      options.success?.({ confirm: true, cancel: false } as UniApp.ShowModalRes)
    })
    vi.mocked(uni.openSetting).mockImplementation((options) => {
      options.success?.({
        authSetting: {
          'scope.userLocation': true,
        },
      } as UniApp.OpenSettingSuccessResult)
    })
    resolveGetLocation()

    await getCurrentLocation()

    expect(uni.showModal).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '需要定位权限',
        confirmText: '去设置',
      }),
    )
    expect(uni.openSetting).toHaveBeenCalled()
    expect(uni.getLocation).toHaveBeenCalled()
  })

  it('rejects with a clear message when the user keeps location disabled', async () => {
    vi.mocked(uni.getSetting).mockImplementation((options) => {
      options.success?.({
        authSetting: {
          'scope.userLocation': false,
        },
      } as UniApp.GetSettingSuccessResult)
    })
    vi.mocked(uni.showModal).mockImplementation((options) => {
      options.success?.({ confirm: false, cancel: true } as UniApp.ShowModalRes)
    })

    await expect(getCurrentLocation()).rejects.toThrow('定位权限未开启')

    expect(uni.getLocation).not.toHaveBeenCalled()
  })
})
