<script setup lang="ts">
import { CircleCheck, Lock, QuestionFilled, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import CaptchaImage from '../../components/CaptchaImage.vue'
import heroIllustration from '../../assets/login/hero-illustration.png'
import { useAuthStore } from '../../stores/auth'
import { logInfo, showError } from '../../utils/feedback'

const REMEMBER_KEY = 'admin_remember_account'

const router = useRouter()
const authStore = useAuthStore()
const captchaRef = ref<InstanceType<typeof CaptchaImage> | null>(null)

const form = reactive({
  account: '',
  password: '',
  captcha: '',
  remember: false,
})

const captchaCode = ref('')
const submitting = ref(false)

const handleCaptchaChange = (code: string) => {
  captchaCode.value = code
}

const handleSubmit = async () => {
  const account = form.account.trim()
  const password = form.password.trim()
  const captcha = form.captcha.trim()

  if (!account || !password) {
    ElMessage.error('请输入账号和密码')
    return
  }

  if (!captcha) {
    ElMessage.error('请输入验证码')
    return
  }

  if (captcha.toUpperCase() !== captchaCode.value.toUpperCase()) {
    ElMessage.error('验证码错误')
    form.captcha = ''
    captchaRef.value?.refresh()
    return
  }

  submitting.value = true
  try {
    await authStore.login(account, password)
    if (form.remember) {
      localStorage.setItem(REMEMBER_KEY, account)
    } else {
      localStorage.removeItem(REMEMBER_KEY)
    }
    logInfo('管理员登录成功', { account })
    await router.push({ name: 'dashboard' })
  } catch (error) {
    showError(error, '登录失败，请检查账号或密码')
    form.captcha = ''
    captchaRef.value?.refresh()
  } finally {
    submitting.value = false
  }
}

const handleForgotPassword = () => {
  ElMessage.info('请联系系统管理员重置密码')
}

const handleSsoLogin = () => {
  ElMessage.info('SSO 单点登录功能开发中')
}

onMounted(() => {
  const remembered = localStorage.getItem(REMEMBER_KEY)
  if (remembered) {
    form.account = remembered
    form.remember = true
  }
})
</script>

<template>
  <div class="login-page">
    <div class="login-page__bg" aria-hidden="true">
      <span class="login-page__orb login-page__orb--a"></span>
      <span class="login-page__orb login-page__orb--b"></span>
      <span class="login-page__grid"></span>
    </div>

    <header class="login-page__header">
      <div class="login-page__brand">
        <div class="login-page__logo" aria-hidden="true">
          <svg viewBox="0 0 40 40" fill="none">
            <path
              d="M20 2L36 11V29L20 38L4 29V11L20 2Z"
              fill="url(#logo-gradient)"
            />
            <path
              d="M14 21L18.5 25.5L27 15"
              stroke="#fff"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <defs>
              <linearGradient id="logo-gradient" x1="4" y1="2" x2="36" y2="38">
                <stop stop-color="#1d7cff" />
                <stop offset="1" stop-color="#0052d9" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="login-page__brand-text">
          <div class="login-page__brand-title">
            <strong>知勤</strong>
            <span class="login-page__brand-tag">管理员端</span>
          </div>
        </div>
      </div>
      <button type="button" class="login-page__help" @click="handleForgotPassword">
        <el-icon><QuestionFilled /></el-icon>
        使用帮助
      </button>
    </header>

    <main class="login-page__main">
      <section class="login-page__hero">
        <div class="login-page__hero-copy">
          <h1>让考勤管理更智能<br />让校园管理更高效</h1>
          <p>数据驱动 · 智能预警 · 高效协同 · 安全可靠</p>
        </div>
        <img
          class="login-page__hero-image"
          :src="heroIllustration"
          alt="知勤管理平台数据可视化示意"
        />
      </section>

      <section class="login-page__panel-wrap">
        <div class="login-card">
          <div class="login-card__head">
            <h2>管理员登录</h2>
            <p>欢迎登录知勤管理平台</p>
          </div>

          <el-form label-position="top" class="login-card__form" @submit.prevent="handleSubmit">
            <el-form-item>
              <el-input
                v-model="form.account"
                size="large"
                placeholder="请输入账号"
                autocomplete="username"
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item>
              <el-input
                v-model="form.password"
                size="large"
                type="password"
                show-password
                placeholder="请输入密码"
                autocomplete="current-password"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item class="login-card__captcha-item">
              <el-input
                v-model="form.captcha"
                size="large"
                placeholder="请输入验证码"
                maxlength="4"
                autocomplete="off"
              >
                <template #prefix>
                  <el-icon><CircleCheck /></el-icon>
                </template>
              </el-input>
              <CaptchaImage ref="captchaRef" @change="handleCaptchaChange" />
            </el-form-item>

            <div class="login-card__options">
              <el-checkbox v-model="form.remember">记住我</el-checkbox>
              <button type="button" class="login-card__link" @click="handleForgotPassword">
                忘记密码？
              </button>
            </div>

            <el-button
              type="primary"
              size="large"
              class="login-view__submit login-card__submit"
              :loading="submitting"
              native-type="submit"
              @click="handleSubmit"
            >
              立即登录
            </el-button>
          </el-form>

          <div class="login-card__divider">
            <span>其他登录方式</span>
          </div>

          <button type="button" class="login-card__sso" @click="handleSsoLogin">
            <span class="login-card__sso-icon" aria-hidden="true">
              <el-icon><User /></el-icon>
            </span>
            <span>SSO 单点登录</span>
          </button>
        </div>
      </section>
    </main>

    <footer class="login-page__footer">
      © 2024 知勤 · 管理员端 v2.1.0 | 最佳显示 1920×1080 及以上分辨率
    </footer>
  </div>
</template>

<style scoped lang="scss">
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: linear-gradient(180deg, #f4f9ff 0%, #eef5ff 48%, #f8fbff 100%);
  color: #101828;
}

.login-page__bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.login-page__orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(0.5px);
}

.login-page__orb--a {
  width: 420px;
  height: 420px;
  top: -120px;
  left: -80px;
  background: radial-gradient(circle, rgba(29, 124, 255, 0.12) 0%, rgba(29, 124, 255, 0) 70%);
}

.login-page__orb--b {
  width: 360px;
  height: 360px;
  right: -60px;
  bottom: -80px;
  background: radial-gradient(circle, rgba(0, 82, 217, 0.1) 0%, rgba(0, 82, 217, 0) 72%);
}

.login-page__grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(29, 124, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(29, 124, 255, 0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.65), transparent 85%);
}

.login-page__header,
.login-page__main,
.login-page__footer {
  position: relative;
  z-index: 1;
}

.login-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28px 56px 0;
}

.login-page__brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.login-page__logo {
  width: 40px;
  height: 40px;

  svg {
    display: block;
    width: 100%;
    height: 100%;
  }
}

.login-page__brand-title {
  display: flex;
  align-items: center;
  gap: 10px;

  strong {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: 0.02em;
  }
}

.login-page__brand-tag {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(29, 124, 255, 0.1);
  color: #1d7cff;
  font-size: 12px;
  font-weight: 600;
}

.login-page__help {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s ease, background 0.2s ease;

  &:hover {
    color: #1d7cff;
    background: rgba(255, 255, 255, 0.95);
  }
}

.login-page__main {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(380px, 460px);
  align-items: center;
  gap: 32px;
  min-height: calc(100vh - 140px);
  padding: 24px 56px 0;
}

.login-page__hero {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 28px;
  min-height: 560px;
}

.login-page__hero-copy {
  max-width: 620px;

  h1 {
    margin: 0;
    font-size: clamp(34px, 4vw, 52px);
    line-height: 1.18;
    font-weight: 900;
    color: #0b3d91;
    letter-spacing: 0.01em;
  }

  p {
    margin: 18px 0 0;
    color: #64748b;
    font-size: 16px;
    line-height: 1.8;
  }
}

.login-page__hero-image {
  width: min(100%, 760px);
  max-height: 420px;
  object-fit: contain;
  object-position: left center;
  user-select: none;
}

.login-page__panel-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  width: min(100%, 420px);
  padding: 36px 36px 28px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(29, 124, 255, 0.08);
  box-shadow:
    0 24px 60px rgba(15, 23, 42, 0.08),
    0 8px 24px rgba(29, 124, 255, 0.08);
}

.login-card__head {
  margin-bottom: 24px;

  h2 {
    margin: 0;
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
  }

  p {
    margin: 8px 0 0;
    color: #64748b;
    font-size: 14px;
  }
}

.login-card__form {
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }

  :deep(.el-input__wrapper) {
    min-height: 48px;
    border-radius: 12px;
    box-shadow: 0 0 0 1px #dce8ff inset;
    background: #fbfdff;
  }

  :deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 1px #1d7cff inset;
  }

  :deep(.el-input__prefix) {
    color: #94a3b8;
  }
}

.login-card__captcha-item {
  :deep(.el-form-item__content) {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  :deep(.el-input) {
    flex: 1;
  }
}

.login-card__options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 4px 0 18px;

  :deep(.el-checkbox__label) {
    color: #64748b;
  }
}

.login-card__link {
  padding: 0;
  border: none;
  background: transparent;
  color: #1d7cff;
  font-size: 14px;
  cursor: pointer;

  &:hover {
    color: #0052d9;
  }
}

.login-card__submit {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(90deg, #1d7cff 0%, #0052d9 100%);
}

.login-card__divider {
  position: relative;
  margin: 24px 0 18px;
  text-align: center;

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: #e8eef8;
  }

  span {
    position: relative;
    z-index: 1;
    padding: 0 12px;
    background: rgba(255, 255, 255, 0.96);
    color: #94a3b8;
    font-size: 13px;
  }
}

.login-card__sso {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 0;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 13px;
  cursor: pointer;

  &:hover {
    color: #1d7cff;
  }
}

.login-card__sso-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 999px;
  background: rgba(29, 124, 255, 0.1);
  color: #1d7cff;
  font-size: 20px;
}

.login-page__footer {
  padding: 18px 56px 28px;
  color: #94a3b8;
  font-size: 12px;
}

@media (max-width: 1100px) {
  .login-page__main {
    grid-template-columns: 1fr;
    min-height: auto;
    padding: 24px 24px 0;
  }

  .login-page__hero {
    min-height: auto;
    text-align: center;
  }

  .login-page__hero-copy {
    margin: 0 auto;
  }

  .login-page__hero-image {
    margin: 0 auto;
    object-position: center;
  }

  .login-page__header,
  .login-page__footer {
    padding-left: 24px;
    padding-right: 24px;
  }
}

@media (max-width: 640px) {
  .login-page__header {
    padding-top: 16px;
  }

  .login-card {
    padding: 28px 20px 22px;
  }

  .login-page__hero-copy h1 {
    font-size: 30px;
  }
}
</style>
