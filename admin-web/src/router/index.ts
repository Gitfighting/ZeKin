import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/login/LoginView.vue'),
    },
    {
      path: '/',
      component: () => import('../layouts/AdminLayout.vue'),
      meta: {
        requiresAuth: true,
      },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/dashboard/DashboardView.vue'),
        },
        {
          path: 'organization',
          name: 'organization',
          component: () => import('../views/organization/OrganizationView.vue'),
        },
        {
          path: 'students',
          name: 'students',
          component: () => import('../views/students/StudentsView.vue'),
        },
        {
          path: 'teachers',
          name: 'teachers',
          component: () => import('../views/teachers/TeachersView.vue'),
        },
        {
          path: 'groups',
          name: 'groups',
          component: () => import('../views/groups/GroupsView.vue'),
        },
        {
          path: 'checkin-types',
          name: 'checkinTypes',
          component: () => import('../views/checkin-types/CheckinTypesView.vue'),
        },
        {
          path: 'rule-templates',
          name: 'ruleTemplates',
          component: () => import('../views/rule-templates/RuleTemplatesView.vue'),
        },
        {
          path: 'task-monitor',
          name: 'taskMonitor',
          component: () => import('../views/task-monitor/TaskMonitorView.vue'),
        },
        {
          path: 'exceptions',
          name: 'exceptions',
          component: () => import('../views/exceptions/ExceptionsView.vue'),
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (to.name === 'login' && authStore.isAuthenticated) {
    return {
      name: 'dashboard',
    }
  }

  return true
})

export default router
