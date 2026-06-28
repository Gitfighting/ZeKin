<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, nextTick, reactive, ref } from 'vue'

import CaptchaImage from '@/components/CaptchaImage.vue'
import IconFont from '@/components/IconFont.vue'
import VectorIcon from '@/components/VectorIcon.vue'
import { UI_ICONS } from '@/constants/ui-icons'
import { login, loadLoginDraft, redirectToHome, registerAccount, saveLoginDraft, type LoginPayload, type RegisterPayload } from '@/services/auth'
import { logInfo, logError, showError } from '@/services/feedback'
import type { UserType } from '@/services/types'

type AuthTab = 'login' | 'register'

/** 开发阶段预填账号密码与验证码，上线前改为 false */
const DEV_PREFILL_LOGIN = true

const DEV_LOGIN_DEFAULTS = {
  account: '20260001',
  password: '123456',
} as const

const activeTab = ref<AuthTab>('login')
const submitting = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const rememberLogin = ref(true)
const captchaCode = ref('')
const captchaInput = ref('')

const loginForm = reactive<LoginPayload>({
  account: '',
  password: '',
})

const registerForm = reactive<RegisterPayload>({
  phone: '',
  account: '',
  password: '',
  confirmPassword: '',
})

const isLoginTab = computed(() => activeTab.value === 'login')

const welcomeText = computed(() =>
  isLoginTab.value
    ? '欢迎回来！请登录您的账号继续使用'
    : '填写手机号、学号/工号与密码即可完成注册',
)

const policyText = computed(() =>
  isLoginTab.value ? '登录即表示同意《用户协议》《隐私政策》' : '注册即表示同意《用户协议》《隐私政策》',
)

function switchTab(tab: AuthTab) {
  activeTab.value = tab
}

function toggleRememberLogin() {
  rememberLogin.value = !rememberLogin.value
  if (!rememberLogin.value) {
    saveLoginDraft(loginForm, false)
  }
}

function onCaptchaChange(code: string) {
  console.info('[captcha] 图片验证码刷新', { code, previousInput: captchaInput.value })
  captchaCode.value = code
  captchaInput.value = DEV_PREFILL_LOGIN ? code : ''
}

function handleCaptchaInput(event: { detail?: { value?: string } }) {
  captchaInput.value = event.detail?.value ?? ''
  console.info('[captcha] 输入框同步', {
    value: captchaInput.value,
    length: captchaInput.value.length,
  })
}

function refreshCaptcha() {
  captchaRef.value?.refresh()
}

const captchaRef = ref<InstanceType<typeof CaptchaImage> | null>(null)

function enterHome(userType: UserType) {
  redirectToHome(userType)
}

async function handleLogin() {
  await nextTick()

  const typedCaptcha = captchaInput.value.trim()
  console.info('[captcha] 登录校验开始', {
    captchaInput: captchaInput.value,
    typedCaptcha,
    captchaCode: captchaCode.value,
    account: loginForm.account,
    hasPassword: Boolean(loginForm.password),
  })

  if (!loginForm.account || !loginForm.password) {
    uni.showToast({ title: '请完整填写登录信息', icon: 'none' })
    return
  }

  if (!typedCaptcha) {
    console.warn('[captcha] 校验失败: 输入为空', { captchaInput: captchaInput.value })
    uni.showToast({ title: '请输入验证码', icon: 'none' })
    return
  }

  if (typedCaptcha.toUpperCase() !== captchaCode.value.toUpperCase()) {
    console.warn('[captcha] 校验失败: 不匹配', {
      typedCaptcha,
      captchaCode: captchaCode.value,
    })
    uni.showToast({ title: '验证码错误，请重试', icon: 'none' })
    refreshCaptcha()
    return
  }

  console.info('[captcha] 校验通过')

  submitting.value = true

  try {
    const session = await login(loginForm)
    saveLoginDraft(loginForm, rememberLogin.value)
    logInfo('登录成功', {
      account: loginForm.account,
      userType: session.user.userType,
    })
    enterHome(session.user.userType)
  } catch (error) {
    showError(error, '登录失败，请检查学号/账号和密码')
    refreshCaptcha()
  } finally {
    submitting.value = false
  }
}

async function handleRegister() {
  if (!registerForm.phone || !registerForm.account || !registerForm.password || !registerForm.confirmPassword) {
    uni.showToast({ title: '请完整填写注册信息', icon: 'none' })
    return
  }

  if (registerForm.password.length < 6) {
    uni.showToast({ title: '密码至少 6 位', icon: 'none' })
    return
  }

  if (registerForm.password !== registerForm.confirmPassword) {
    uni.showToast({ title: '两次密码输入不一致', icon: 'none' })
    return
  }

  submitting.value = true

  try {
    const session = await registerAccount(registerForm)
    logInfo('注册成功', {
      account: registerForm.account,
      userType: session.user.userType,
    })
    enterHome(session.user.userType)
  } catch (error) {
    logError('[register-flow] 注册失败', error)
    showError(error, '注册失败，请检查填写信息或更换学号/手机号')
  } finally {
    submitting.value = false
  }
}

onLoad((options) => {
  if (options?.tab === 'register') {
    activeTab.value = 'register'
  }

  if (DEV_PREFILL_LOGIN) {
    loginForm.account = DEV_LOGIN_DEFAULTS.account
    loginForm.password = DEV_LOGIN_DEFAULTS.password
    return
  }

  const draft = loadLoginDraft()
  rememberLogin.value = draft.remember || rememberLogin.value
  if (draft.account) {
    loginForm.account = draft.account
  }
  if (draft.password) {
    loginForm.password = draft.password
  }
})
</script>

<template>
  <view class="auth-page">
    <view class="hero">
      <view class="hero-copy">
        <text class="app-title">知勤</text>
        <text class="app-subtitle">智慧考勤，轻松校园生活</text>
      </view>
      <view class="cloud cloud-a"></view>
      <view class="cloud cloud-b"></view>
      <view class="campus-scene" aria-hidden="true">
        <view class="building building-left"></view>
        <view class="tower"><view class="clock"></view></view>
        <view class="building building-right"></view>
        <view class="tree tree-one"></view>
        <view class="tree tree-two"></view>
      </view>
    </view>

    <view class="auth-body auth-body--login">
      <view class="auth-card">
        <view class="tabs">
          <view
            class="tab-btn"
            :class="{ active: isLoginTab, 'tab-btn--plain': !isLoginTab }"
            @click="switchTab('login')"
          >
            登录
          </view>
          <view
            class="tab-btn"
            :class="{ active: !isLoginTab, 'tab-btn--plain': isLoginTab }"
            @click="switchTab('register')"
          >
            注册
          </view>
        </view>

        <view class="welcome-banner">
          <IconFont name="anquan" class="welcome-icon" size="36rpx" />
          <text>{{ welcomeText }}</text>
        </view>

        <view v-if="isLoginTab" class="auth-panel">
          <view class="field">
            <IconFont name="yonghu" class="field-icon" color="#b0b8c4" />
            <input
              v-model="loginForm.account"
              placeholder="学号/工号"
              placeholder-class="field-placeholder"
            />
          </view>

          <view class="field field--password">
            <IconFont name="mima" class="field-icon" color="#b0b8c4" />
            <input
              v-model="loginForm.password"
              :password="!showPassword"
              placeholder="密码"
              placeholder-class="field-placeholder"
            />
            <view class="eye-btn" @click="showPassword = !showPassword">
              <IconFont
                :name="showPassword ? 'yanjing-biyan' : 'yanjing'"
                size="40rpx"
                color="#b0b8c4"
              />
            </view>
          </view>

          <view class="field field--code">
            <IconFont name="yanzhengma" class="field-icon" color="#b0b8c4" />
            <view class="field-code-row">
              <input
                :value="captchaInput"
                class="field-code-input"
                type="text"
                placeholder="验证码"
                placeholder-class="field-placeholder"
                maxlength="4"
                confirm-type="done"
                adjust-position
                @input="handleCaptchaInput"
                @blur="handleCaptchaInput"
              />
              <CaptchaImage ref="captchaRef" width="200rpx" height="52rpx" @change="onCaptchaChange" />
            </view>
          </view>

          <view class="options-row">
            <view class="remember" @click="toggleRememberLogin">
              <view class="checkbox" :class="{ 'checkbox--checked': rememberLogin }">
                <VectorIcon v-if="rememberLogin" :src="UI_ICONS.check" size="22rpx" />
              </view>
              <text>记住登录</text>
            </view>
            <text class="forgot-link">忘记密码？</text>
          </view>

          <view
            class="primary-btn"
            :class="{ 'primary-btn--loading': submitting }"
            @tap="handleLogin"
          >
            <text>{{ submitting ? '登录中...' : '立即登录' }}</text>
          </view>
        </view>

        <view v-else class="auth-panel">
          <view class="field">
            <IconFont name="anquan" class="field-icon" color="#b0b8c4" />
            <input
              v-model="registerForm.phone"
              type="number"
              maxlength="11"
              placeholder="手机号"
              placeholder-class="field-placeholder"
            />
          </view>

          <view class="field">
            <IconFont name="yonghu" class="field-icon" color="#b0b8c4" />
            <input
              v-model="registerForm.account"
              placeholder="学号/工号"
              placeholder-class="field-placeholder"
            />
          </view>

          <view class="field field--password">
            <IconFont name="mima" class="field-icon" color="#b0b8c4" />
            <input
              v-model="registerForm.password"
              :password="!showPassword"
              placeholder="密码（不少于 6 位）"
              placeholder-class="field-placeholder"
            />
            <view class="eye-btn" @click="showPassword = !showPassword">
              <IconFont
                :name="showPassword ? 'yanjing-biyan' : 'yanjing'"
                size="40rpx"
                color="#b0b8c4"
              />
            </view>
          </view>

          <view class="field field--password">
            <IconFont name="mima" class="field-icon" color="#b0b8c4" />
            <input
              v-model="registerForm.confirmPassword"
              :password="!showConfirmPassword"
              placeholder="确认密码"
              placeholder-class="field-placeholder"
            />
            <view class="eye-btn" @click="showConfirmPassword = !showConfirmPassword">
              <IconFont
                :name="showConfirmPassword ? 'yanjing-biyan' : 'yanjing'"
                size="40rpx"
                color="#b0b8c4"
              />
            </view>
          </view>

          <button class="primary-btn" type="primary" :loading="submitting" @click="handleRegister">
            {{ submitting ? '注册中...' : '立即注册' }}
          </button>
        </view>
      </view>

      <view class="policy">
        <text>{{ policyText }}</text>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use './login-shell.scss';

.auth-body--login .auth-card {
  margin-top: 100px;
}
</style>
