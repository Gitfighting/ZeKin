<script setup lang="ts">
import { Lock, User } from '@element-plus/icons-vue'
import { reactive } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  account: '',
  password: '',
})

const handleSubmit = async () => {
  await authStore.login(form.account || 'admin', form.password)
  await router.push({ name: 'dashboard' })
}
</script>

<template>
  <div class="login-view">
    <div class="login-view__hero">
      <div class="login-view__copy">
        <span>Campus Governance Console</span>
        <h1>AI思政辅助平台</h1>
        <p>统一治理组织、规则、任务与异常申诉，让管理动作保持清晰、稳定、可追踪。</p>
      </div>
    </div>

    <div class="login-view__panel sz-card">
      <div class="login-view__panel-head">
        <h2>登录</h2>
        <p>管理员入口</p>
      </div>
      <el-form label-position="top" @submit.prevent="handleSubmit">
        <el-form-item label="账号">
          <el-input v-model="form.account" placeholder="请输入账号">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码">
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-button type="primary" size="large" class="login-view__submit" @click="handleSubmit">
          登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-view {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(360px, 460px);
  background:
    radial-gradient(circle at top left, rgba(116, 182, 255, 0.26), transparent 28%),
    linear-gradient(135deg, #e9f3ff 0%, #f7fbff 40%, #dcefff 100%);
}

.login-view__hero {
  position: relative;
  overflow: hidden;
  padding: 56px;
  display: flex;
  align-items: flex-end;
}

.login-view__hero::before,
.login-view__hero::after {
  content: '';
  position: absolute;
  border-radius: 999px;
  background: rgba(22, 119, 255, 0.08);
}

.login-view__hero::before {
  width: 420px;
  height: 420px;
  top: -120px;
  left: -80px;
}

.login-view__hero::after {
  width: 280px;
  height: 280px;
  right: 56px;
  bottom: 64px;
  background: rgba(255, 255, 255, 0.34);
  box-shadow: inset 0 0 0 1px rgba(22, 119, 255, 0.08);
}

.login-view__copy {
  position: relative;
  z-index: 1;
  max-width: 520px;

  span {
    display: inline-flex;
    padding: 6px 10px;
    border-radius: 999px;
    color: var(--sz-primary);
    background: rgba(255, 255, 255, 0.7);
    font-size: 13px;
  }

  h1 {
    margin: 18px 0 12px;
    font-size: 44px;
    line-height: 1.1;
  }

  p {
    margin: 0;
    max-width: 440px;
    color: #35506d;
    line-height: 1.75;
  }
}

.login-view__panel {
  align-self: center;
  justify-self: center;
  width: min(100% - 32px, 392px);
  padding: 32px;
  background: rgba(255, 255, 255, 0.94);
}

.login-view__panel-head {
  margin-bottom: 16px;

  h2 {
    margin: 0;
    font-size: 28px;
  }

  p {
    margin: 6px 0 0;
    color: var(--sz-muted);
  }
}

.login-view__submit {
  width: 100%;
  margin-top: 8px;
}

@media (max-width: 960px) {
  .login-view {
    grid-template-columns: 1fr;
    padding: 20px;
  }

  .login-view__hero {
    min-height: 280px;
    padding: 24px 8px;
  }

  .login-view__panel {
    margin-bottom: 20px;
  }
}
</style>
