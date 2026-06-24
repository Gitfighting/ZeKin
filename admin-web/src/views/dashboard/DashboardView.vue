<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getDashboard, type DashboardStats } from '../../api/admin'

const stats = ref<DashboardStats>({
  studentCount: 0,
  taskCount: 28,
  completionRate: 92,
  exceptionCount: 11,
  pendingAppealCount: 4,
})

const highlights = [
  { label: '教师侧待提醒任务', value: '7', hint: '晚间任务未确认' },
  { label: '学生侧异常聚类', value: '3 组', hint: '集中在定位缺失' },
  { label: '组织规则变更', value: '2 项', hint: '本周更新模板' },
]

onMounted(async () => {
  try {
    stats.value = await getDashboard()
  } catch {
    // Fallback to local dashboard summary for offline-first shell verification.
  }
})
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>工作台</h1>
        <p>集中查看任务推进、异常波动与组织治理状态。</p>
      </div>
      <el-button type="primary">刷新概览</el-button>
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
        <el-timeline>
          <el-timeline-item timestamp="08:30" type="primary">早签到规则已按学院下发</el-timeline-item>
          <el-timeline-item timestamp="11:20" type="warning">自动判定中出现 5 条定位例外</el-timeline-item>
          <el-timeline-item timestamp="14:00" type="success">任务模板“晨读打卡”完成率超过 95%</el-timeline-item>
        </el-timeline>
      </el-card>

      <el-card header="重点指标">
        <div class="highlight-list">
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
