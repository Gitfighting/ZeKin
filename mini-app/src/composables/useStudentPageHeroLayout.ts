import { onMounted, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

export function useStudentPageHeroLayout() {
  const brandBarStyle = ref<Record<string, string>>({
    top: '48px',
    height: '32px',
  })
  const heroContentStyle = ref<Record<string, string>>({
    paddingTop: '112rpx',
    paddingLeft: '32rpx',
    paddingRight: '32rpx',
  })
  const backButtonStyle = ref<Record<string, string>>({
    width: '32px',
    height: '32px',
  })
  const navRightStyle = ref<Record<string, string>>({
    width: '96px',
    height: '32px',
  })

  function syncHeroLayout() {
    if (typeof uni === 'undefined') {
      return
    }

    try {
      const menuButton = uni.getMenuButtonBoundingClientRect()
      const systemInfo = uni.getSystemInfoSync()
      brandBarStyle.value = {
        top: `${menuButton.top}px`,
        height: `${menuButton.height}px`,
      }
      heroContentStyle.value = {
        paddingTop: `${menuButton.bottom + 12}px`,
        paddingLeft: '32rpx',
        paddingRight: '32rpx',
      }
      backButtonStyle.value = {
        width: `${menuButton.height}px`,
        height: `${menuButton.height}px`,
      }
      navRightStyle.value = {
        width: `${(systemInfo.windowWidth ?? 375) - menuButton.left}px`,
        height: `${menuButton.height}px`,
      }
    } catch {
      // 非小程序环境保留默认占位
    }
  }

  onMounted(syncHeroLayout)
  onShow(syncHeroLayout)

  return {
    brandBarStyle,
    heroContentStyle,
    backButtonStyle,
    navRightStyle,
    syncHeroLayout,
  }
}
