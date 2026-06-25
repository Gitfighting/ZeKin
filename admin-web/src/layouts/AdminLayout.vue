<script setup lang="ts">
import {
  Bell,
  Briefcase,
  Connection,
  DocumentCopy,
  Grid,
  Monitor,
  Operation,
  School,
  User,
  UserFilled,
  Warning,
} from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const menuItems = [
  { label: '工作台', routeName: 'dashboard', icon: Grid },
  { label: '组织管理', routeName: 'organization', icon: School },
  { label: '学生管理', routeName: 'students', icon: User },
  { label: '教师管理', routeName: 'teachers', icon: UserFilled },
  { label: '班级与分组', routeName: 'groups', icon: Connection },
  { label: '打卡类型', routeName: 'checkinTypes', icon: Operation },
  { label: '规则模板', routeName: 'ruleTemplates', icon: DocumentCopy },
  { label: '任务监管', routeName: 'taskMonitor', icon: Monitor },
  { label: '异常与申诉', routeName: 'exceptions', icon: Warning },
]

const activeMenu = computed(() => String(route.name ?? 'dashboard'))
const currentUserName = computed(() => authStore.user?.displayName ?? '系统管理员')
const currentUserRole = computed(() => authStore.user?.role ?? '校级管理员')

const handleSelect = (name: string) => {
  router.push({ name })
}

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="admin-layout">
    <aside class="admin-layout__sidebar">
      <div class="admin-layout__brand">
        <div class="brand-mark">
          <el-icon><Briefcase /></el-icon>
        </div>
        <div>
          <h1>AI思政辅助平台</h1>
          <p>管理员控制台</p>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="admin-layout__menu"
        @select="handleSelect"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.routeName"
          :index="item.routeName"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
      <div class="admin-layout__sidebar-footer sz-card">
        <p>今日概览</p>
        <strong>校内任务监管已接入 9 个一级组织</strong>
      </div>
    </aside>

    <div class="admin-layout__main">
      <header class="admin-layout__header">
        <div>
          <p class="admin-layout__greeting">欢迎回来</p>
          <h2>{{ menuItems.find((item) => item.routeName === activeMenu)?.label ?? '工作台' }}</h2>
        </div>
        <div class="admin-layout__actions">
          <el-button circle>
            <el-icon><Bell /></el-icon>
          </el-button>
          <div class="admin-layout__user sz-card">
            <div class="user-avatar">{{ currentUserName.slice(0, 1) }}</div>
            <div>
              <strong>{{ currentUserName }}</strong>
              <p>{{ currentUserRole }}</p>
            </div>
            <el-button text type="primary" @click="handleLogout">退出</el-button>
          </div>
        </div>
      </header>

      <main class="admin-layout__content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss">
.admin-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr);
}

.admin-layout__sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px 16px;
  background: linear-gradient(180deg, #ffffff 0%, #f4f9ff 100%);
  border-right: 1px solid rgba(22, 119, 255, 0.1);
}

.admin-layout__brand {
  display: flex;
  align-items: center;
  gap: 12px;

  h1 {
    margin: 0;
    font-size: 18px;
  }

  p {
    margin: 4px 0 0;
    color: var(--sz-muted);
    font-size: 13px;
  }
}

.brand-mark {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--sz-primary), #4fa4ff);
  color: white;
  font-size: 20px;
  box-shadow: 0 10px 24px rgba(22, 119, 255, 0.24);
}

.admin-layout__menu {
  flex: 1;
  background: transparent;
}

.admin-layout__sidebar-footer {
  padding: 14px 16px;

  p {
    margin: 0 0 6px;
    color: var(--sz-muted);
    font-size: 12px;
  }

  strong {
    font-size: 14px;
    line-height: 1.5;
  }
}

.admin-layout__main {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.admin-layout__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(22, 119, 255, 0.08);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);

  h2 {
    margin: 4px 0 0;
    font-size: 22px;
  }
}

.admin-layout__greeting {
  margin: 0;
  color: var(--sz-muted);
  font-size: 13px;
}

.admin-layout__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-layout__user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--sz-primary-soft);
  color: var(--sz-primary);
  font-weight: 700;
}

.admin-layout__user p {
  margin: 4px 0 0;
  color: var(--sz-muted);
  font-size: 12px;
}

.admin-layout__content {
  flex: 1;
  padding: 24px;
}

@media (max-width: 1100px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .admin-layout__sidebar {
    border-right: none;
    border-bottom: 1px solid rgba(22, 119, 255, 0.1);
  }
}

@media (max-width: 720px) {
  .admin-layout__header,
  .admin-layout__content {
    padding: 16px;
  }

  .admin-layout__header {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-layout__actions {
    justify-content: space-between;
  }
}
</style>
