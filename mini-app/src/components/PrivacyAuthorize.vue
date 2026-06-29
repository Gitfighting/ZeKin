<script setup lang="ts">
import { onMounted, ref } from 'vue'

const visible = ref(false)
const contractName = ref('《用户隐私保护指引》')

let pendingResolve: ((detail: { event: string; buttonId: string }) => void) | null = null

function close() {
  visible.value = false
  pendingResolve = null
}

function onAgree(e: { detail?: { errMsg?: string } }) {
  if (e.detail?.errMsg !== 'agreePrivacyAuthorization:ok') return
  pendingResolve?.({ event: 'agree', buttonId: 'privacy-agree-btn' })
  close()
}

function onReject() {
  uni.showToast({ title: '需同意隐私政策后才能使用定位等功能', icon: 'none' })
  close()
}

function openContract() {
  // #ifdef MP-WEIXIN
  uni.openPrivacyContract({})
  // #endif
}

onMounted(() => {
  // #ifdef MP-WEIXIN
  if (typeof wx === 'undefined') return

  if (wx.onNeedPrivacyAuthorization) {
    wx.onNeedPrivacyAuthorization((resolve) => {
      pendingResolve = resolve
      visible.value = true
    })
  }

  if (uni.getPrivacySetting) {
    uni.getPrivacySetting({
      success: (res) => {
        if (res.privacyContractName) {
          contractName.value = res.privacyContractName
        }
      },
    })
  }
  // #endif
})
</script>

<template>
  <!-- #ifdef MP-WEIXIN -->
  <view v-if="visible" class="privacy-mask">
    <view class="privacy-panel">
      <text class="privacy-title">隐私保护提示</text>
      <text class="privacy-desc">
        打卡功能需要使用您的位置信息。请阅读并同意
        <text class="privacy-link" @tap="openContract">{{ contractName }}</text>
        后继续。
      </text>
      <view class="privacy-actions">
        <button class="privacy-btn ghost" @tap="onReject">暂不使用</button>
        <button
          id="privacy-agree-btn"
          class="privacy-btn primary"
          open-type="agreePrivacyAuthorization"
          @agreeprivacyauthorization="onAgree"
        >
          同意并继续
        </button>
      </view>
    </view>
  </view>
  <!-- #endif -->
</template>

<style scoped lang="scss">
.privacy-mask {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48rpx;
}

.privacy-panel {
  width: 100%;
  max-width: 620rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx 36rpx 32rpx;
  box-shadow: 0 24rpx 48rpx rgba(15, 23, 42, 0.12);
}

.privacy-title {
  display: block;
  font-size: 34rpx;
  font-weight: 600;
  color: #101828;
  margin-bottom: 20rpx;
}

.privacy-desc {
  display: block;
  font-size: 28rpx;
  line-height: 1.6;
  color: #475467;
}

.privacy-link {
  color: #1677ff;
}

.privacy-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 36rpx;
}

.privacy-btn {
  flex: 1;
  height: 80rpx;
  line-height: 80rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
  margin: 0;
  padding: 0;

  &::after {
    border: none;
  }

  &.ghost {
    background: #f2f4f7;
    color: #344054;
  }

  &.primary {
    background: #1677ff;
    color: #fff;
  }
}
</style>
