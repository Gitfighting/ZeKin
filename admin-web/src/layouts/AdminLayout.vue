<script setup lang="ts">
import {
  Bell,
  Connection,
  DataAnalysis,
  Expand,
  Fold,
  Grid,
  Monitor,
  School,
  TrendCharts,
  User,
  UserFilled,
  Warning,
} from '@element-plus/icons-vue'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const SIDEBAR_COLLAPSED_KEY = 'admin_sidebar_collapsed'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const collapsed = ref(localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1')
const menuRef = ref<{ open: (index: string) => void } | null>(null)

type MenuLeaf = {
  type: 'item'
  label: string
  routeName: string
  icon: typeof Grid
}

type MenuSubmenu = {
  type: 'submenu'
  label: string
  index: string
  icon: typeof Grid
  children: Array<{ label: string; routeName: string; icon: typeof Grid }>
}

type MenuEntry = MenuLeaf | MenuSubmenu

const menuItems: MenuEntry[] = [
  { type: 'item', label: '工作台', routeName: 'dashboard', icon: Grid },
  { type: 'item', label: '场景化统计分析', routeName: 'analytics', icon: DataAnalysis },
  { type: 'item', label: '数据大屏', routeName: 'dataScreen', icon: TrendCharts },
  { type: 'item', label: '组织管理', routeName: 'organization', icon: School },
  {
    type: 'submenu',
    label: '人员管理',
    index: 'personnel',
    icon: UserFilled,
    children: [
      { label: '学生管理', routeName: 'students', icon: User },
      { label: '教师管理', routeName: 'teachers', icon: UserFilled },
    ],
  },
  { type: 'item', label: '班级与分组', routeName: 'groups', icon: Connection },
  { type: 'item', label: '任务监管', routeName: 'taskMonitor', icon: Monitor },
  { type: 'item', label: '考勤异常', routeName: 'exceptions', icon: Warning },
]

const personnelRoutes = ['students', 'teachers']

const resolveMenuLabel = (routeName: string): string => {
  for (const item of menuItems) {
    if (item.type === 'submenu') {
      const child = item.children.find((entry) => entry.routeName === routeName)
      if (child) return child.label
    } else if (item.routeName === routeName) {
      return item.label
    }
  }
  return '工作台'
}

const activeMenu = computed(() => String(route.name ?? 'dashboard'))
const currentUserName = computed(() => authStore.user?.displayName ?? '系统管理员')
const currentUserRole = computed(() => authStore.user?.role ?? '校级管理员')
const currentPageLabel = computed(() => resolveMenuLabel(activeMenu.value))

const defaultOpenMenus = computed(() =>
  personnelRoutes.includes(activeMenu.value) ? ['personnel'] : [],
)

watch(activeMenu, (routeName) => {
  if (personnelRoutes.includes(routeName)) {
    menuRef.value?.open('personnel')
  }
}, { immediate: true })

const handleSelect = (name: string) => {
  router.push({ name })
}

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'login' })
}

const toggleSidebar = () => {
  collapsed.value = !collapsed.value
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, collapsed.value ? '1' : '0')
}
</script>

<template>
  <div class="admin-layout" :class="{ 'admin-layout--collapsed': collapsed }">
    <aside class="admin-layout__sidebar">
      <div class="admin-layout__brand">
        <div class="brand-mark">
          <svg viewBox="0 0 40 40" fill="none" aria-hidden="true">
            <path d="M20 2L36 11V29L20 38L4 29V11L20 2Z" fill="url(#sidebar-logo)" />
            <path
              d="M14 21L18.5 25.5L27 15"
              stroke="#fff"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <defs>
              <linearGradient id="sidebar-logo" x1="4" y1="2" x2="36" y2="38">
                <stop stop-color="#38bdf8" />
                <stop offset="1" stop-color="#1677ff" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div v-show="!collapsed" class="admin-layout__brand-text">
          <h1>知勤</h1>
          <p>智慧考勤管理平台</p>
        </div>
      </div>

      <el-menu
        ref="menuRef"
        :default-active="activeMenu"
        :default-openeds="defaultOpenMenus"
        :collapse="collapsed"
        :collapse-transition="false"
        class="admin-layout__menu"
        @select="handleSelect"
      >
        <template v-for="item in menuItems" :key="item.type === 'submenu' ? item.index : item.routeName">
          <el-sub-menu v-if="item.type === 'submenu'" :index="item.index">
            <template #title>
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.label }}</span>
            </template>
            <el-menu-item
              v-for="child in item.children"
              :key="child.routeName"
              :index="child.routeName"
            >
              <el-icon><component :is="child.icon" /></el-icon>
              <template #title>{{ child.label }}</template>
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else :index="item.routeName">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.label }}</template>
          </el-menu-item>
        </template>
      </el-menu>

      <div v-show="!collapsed" class="admin-layout__sidebar-footer sz-panel">
        <p>今日概览</p>
        <strong>数据驱动 · 智能预警 · 高效协同</strong>
      </div>

      <button
        type="button"
        class="admin-layout__collapse-btn sz-panel"
        :aria-label="collapsed ? '展开侧栏' : '收起侧栏'"
        @click="toggleSidebar"
      >
        <el-icon><Expand v-if="collapsed" /><Fold v-else /></el-icon>
        <span v-show="!collapsed">收起侧栏</span>
      </button>
    </aside>

    <header class="admin-layout__header">
      <div class="admin-layout__header-left">
        <button
          type="button"
          class="admin-layout__header-toggle sz-panel"
          :aria-label="collapsed ? '展开侧栏' : '收起侧栏'"
          @click="toggleSidebar"
        >
          <el-icon><Expand v-if="collapsed" /><Fold v-else /></el-icon>
        </button>
        <div class="admin-layout__header-main">
          <p class="admin-layout__greeting">欢迎回来</p>
          <h2>{{ currentPageLabel }}</h2>
        </div>
      </div>
      <div class="admin-layout__actions">
        <el-button circle class="admin-layout__notify sz-panel">
          <el-icon><Bell /></el-icon>
        </el-button>
        <div class="admin-layout__user sz-panel">
          <div class="user-avatar">{{ currentUserName.slice(0, 1) }}</div>
          <div class="admin-layout__user-text">
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
</template>

<style scoped lang="scss">
.admin-layout {
  --sidebar-width: 248px;
  --sidebar-width-collapsed: 68px;
  --header-height: 64px;
  --sidebar-current-width: var(--sidebar-width);

  min-height: 100vh;

  &--collapsed {
    --sidebar-current-width: var(--sidebar-width-collapsed);
  }
}

.admin-layout__sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
  width: var(--sidebar-current-width);
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 12px;
  box-sizing: border-box;
  background: transparent;
  transition: width 0.24s ease;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    top: 12px;
    right: 0;
    bottom: 12px;
    width: 1px;
    background: linear-gradient(
      180deg,
      transparent 0%,
      rgba(22, 119, 255, 0.1) 15%,
      rgba(148, 163, 184, 0.16) 50%,
      rgba(22, 119, 255, 0.1) 85%,
      transparent 100%
    );
    pointer-events: none;
  }
}

.admin-layout__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 6px 8px;
  min-height: 52px;
  flex-shrink: 0;

  h1 {
    margin: 0;
    font-size: 18px;
    font-weight: 800;
    color: var(--sz-text);
    white-space: nowrap;
  }

  p {
    margin: 4px 0 0;
    color: var(--sz-muted);
    font-size: 12px;
    white-space: nowrap;
  }
}

.admin-layout__brand-text {
  overflow: hidden;
}

.brand-mark {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: var(--sz-radius);
  background: var(--sz-primary);

  svg {
    width: 24px;
    height: 24px;
  }
}

.admin-layout__menu {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  border: none;

  :deep(.el-menu-item) {
    height: 44px;
    margin-bottom: 4px;
    border-radius: var(--sz-radius);
    color: var(--sz-muted);
  }

  :deep(.el-sub-menu__title) {
    height: 44px;
    margin-bottom: 4px;
    border-radius: var(--sz-radius);
    color: var(--sz-muted);
  }

  :deep(.el-sub-menu .el-menu-item) {
    padding-left: 48px !important;
    min-width: auto;
  }

  :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
    color: var(--sz-primary);
  }

  :deep(.el-menu-item.is-active) {
    color: var(--sz-primary);
  }

  &:not(.el-menu--collapse) {
    width: 100%;
  }
}

.admin-layout__sidebar-footer {
  flex-shrink: 0;
  margin: 0 2px;
  padding: 12px 14px;

  p {
    margin: 0 0 4px;
    color: var(--sz-primary);
    font-size: 12px;
    font-weight: 600;
  }

  strong {
    font-size: 12px;
    line-height: 1.5;
    color: var(--sz-muted);
    font-weight: 500;
  }
}

.admin-layout__collapse-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: calc(100% - 4px);
  margin: 0 2px;
  padding: 10px 12px;
  color: var(--sz-muted);
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s ease;

  &:hover {
    color: var(--sz-primary);
  }
}

.admin-layout--collapsed .admin-layout__collapse-btn {
  padding: 10px 0;
}

.admin-layout__header {
  position: fixed;
  top: 0;
  left: var(--sidebar-current-width);
  right: 0;
  z-index: 190;
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 24px;
  box-sizing: border-box;
  background: transparent;
  transition: left 0.24s ease;

  h2 {
    margin: 2px 0 0;
    font-size: 20px;
    color: var(--sz-text);
    line-height: 1.2;
    font-weight: 700;
  }
}

.admin-layout__header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.admin-layout__header-toggle {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  padding: 0;
  color: var(--sz-muted);
  cursor: pointer;
  transition: color 0.2s ease;

  &:hover {
    color: var(--sz-primary);
  }
}

.admin-layout__header-main {
  min-width: 0;
}

.admin-layout__greeting {
  margin: 0;
  color: var(--sz-muted);
  font-size: 12px;
}

.admin-layout__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.admin-layout__notify {
  width: 36px;
  height: 36px;
  padding: 0;
  color: var(--sz-primary);
  border: none;
}

.admin-layout__user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px 6px 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--sz-primary-soft);
  color: var(--sz-primary);
  font-weight: 700;
  font-size: 14px;
}

.admin-layout__user-text {
  p {
    margin: 2px 0 0;
    color: var(--sz-muted);
    font-size: 12px;
  }
}

.admin-layout__content {
  margin-left: var(--sidebar-current-width);
  margin-top: var(--header-height);
  min-height: calc(100vh - var(--header-height));
  padding: 20px 24px 24px;
  box-sizing: border-box;
  transition: margin-left 0.24s ease;
}

@media (max-width: 900px) {
  .admin-layout__header,
  .admin-layout__content {
    padding-left: 16px;
    padding-right: 16px;
  }

  .admin-layout__user-text {
    display: none;
  }
}

@media (max-width: 720px) {
  .admin-layout__header {
    flex-wrap: wrap;
    height: auto;
    min-height: var(--header-height);
    padding-top: 12px;
    padding-bottom: 12px;
  }

  .admin-layout__content {
    margin-top: 72px;
  }
}
</style>
