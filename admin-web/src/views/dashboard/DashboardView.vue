<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getDashboard, type DashboardStats } from '../../api/admin'
import { logInfo, showError } from '../../utils/feedback'

const emptyStats = (): DashboardStats => ({
  studentCount: 0,
  taskCount: 0,
  completionRate: 0,
  exceptionCount: 0,
  pendingAppealCount: 0,
})

const stats = ref<DashboardStats>(emptyStats())
const loading = ref(false)
const alerts = ref<Array<{ content: string; timestamp: string; type: 'primary' | 'warning' | 'success' }>>([])
const highlights = ref<Array<{ label: string; value: string; hint: string }>>([])

async function loadDashboard() {
  loading.value = true
  try {
    stats.value = await getDashboard()
    logInfo('管理端工作台加载成功', stats.value)
  } catch (error) {
    stats.value = emptyStats()
    alerts.value = []
    highlights.value = []
    showError(error, '工作台数据加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>工作台</h1>
        <p>集中查看任务推进、异常波动与组织治理状态。</p>
      </div>
      <el-button type="primary" :loading="loading" @click="loadDashboard">刷新概览</el-button>
    </div>

    <div class="stat-grid">
      <el-card v-for="item in [
        { label: '任务总数', value: `${stats.taskCount}`, suffix: '项' },
        { label: '今日完成率', value: `${stats.completionRate}`, suffix: '%' },
        { label: '异常数量', value: `${stats.exceptionCount}`, suffix: '条' },
        { label: '待处理申诉', value: `${stats.pendingAppealCount}`, suffix: '条' },
      ]" :key="item.label">
        <template #header>{{ item.label }}</template>
        <div class="stat-card">
          <strong>{{ item.value }}</strong>
          <span>{{ item.suffix }}</span>
        </div>
      </el-card>
    </div>

    <div class="two-column">
      <el-card header="监管提醒">
        <el-empty v-if="alerts.length === 0" description="暂无监管提醒" :image-size="72" />
        <el-timeline v-else>
          <el-timeline-item
            v-for="alert in alerts"
            :key="`${alert.timestamp}-${alert.content}`"
            :timestamp="alert.timestamp"
            :type="alert.type"
          >
            {{ alert.content }}
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <el-card header="重点指标">
        <el-empty v-if="highlights.length === 0" description="暂无重点指标" :image-size="72" />
        <div v-else class="highlight-list">
          <div v-for="item in highlights" :key="item.label" class="highlight-list__item">
            <div>
              <p>{{ item.label }}</p>
              <strong>{{ item.value }}</strong>
            </div>
            <span>{{ item.hint }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </section>
</template>

<style scoped lang="scss">
.stat-card {
  display: flex;
  align-items: flex-end;
  gap: 6px;

  strong {
    font-size: 32px;
    line-height: 1;
    color: var(--sz-primary);
  }

  span {
    color: var(--sz-muted);
    padding-bottom: 4px;
  }
}

.highlight-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.highlight-list__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid rgba(22, 119, 255, 0.1);
  border-radius: 8px;
  background: #f8fbff;

  p,
  span {
    margin: 0;
    color: var(--sz-muted);
    font-size: 13px;
  }

  strong {
    display: block;
    margin-top: 6px;
    font-size: 20px;
  }
}
</style>
