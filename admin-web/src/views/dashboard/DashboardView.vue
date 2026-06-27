<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

import {
  getDashboard,
  getExceptions,
  getGroups,
  getTasks,
  type DashboardStats,
} from '../../api/admin'
import { logInfo, showError } from '../../utils/feedback'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const router = useRouter()

const emptyStats = (): DashboardStats => ({
  studentCount: 0,
  taskCount: 0,
  completionRate: 0,
  exceptionCount: 0,
  pendingAppealCount: 0,
})

const stats = ref<DashboardStats>(emptyStats())
const loading = ref(false)

const taskStatusData = ref<Array<{ name: string; value: number }>>([])
const completionData = ref<Array<{ name: string; value: number }>>([])
const exceptionData = ref<Array<{ name: string; value: number }>>([])
const groupData = ref<Array<{ name: string; value: number }>>([])

const palette = ['#1677ff', '#06b6d4', '#8b5cf6', '#f97316', '#ec4899', '#22c55e']

const statCards = computed(() => [
  { label: '学生总数', value: `${stats.value.studentCount}`, suffix: '人', tone: 'stat-card--tone-blue' },
  { label: '任务总数', value: `${stats.value.taskCount}`, suffix: '项', tone: 'stat-card--tone-cyan' },
  { label: '平均完成率', value: `${stats.value.completionRate}`, suffix: '%', tone: 'stat-card--tone-purple' },
  { label: '异常数量', value: `${stats.value.exceptionCount}`, suffix: '条', tone: 'stat-card--tone-orange' },
  { label: '待处理申诉', value: `${stats.value.pendingAppealCount}`, suffix: '条', tone: 'stat-card--tone-pink' },
])

const heroTags = [
  { label: '数据驱动', color: '#1677ff' },
  { label: '智能预警', color: '#06b6d4' },
  { label: '高效协同', color: '#8b5cf6' },
  { label: '安全可靠', color: '#f97316' },
]

const taskStatusOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  color: palette,
  series: [
    {
      name: '任务状态',
      type: 'pie',
      radius: ['45%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{c}' },
      data: taskStatusData.value,
    },
  ],
}))

const completionOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 50, right: 20, top: 30, bottom: 60 },
  xAxis: {
    type: 'category',
    data: completionData.value.map((item) => item.name),
    axisLabel: { interval: 0, rotate: 30, fontSize: 11 },
  },
  yAxis: { type: 'value', max: 100, name: '完成率%' },
  series: [
    {
      type: 'bar',
      data: completionData.value.map((item) => item.value),
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#38bdf8' },
            { offset: 1, color: '#1677ff' },
          ],
        },
      },
      barMaxWidth: 36,
    },
  ],
}))

const exceptionOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  color: palette,
  series: [
    {
      name: '异常类型',
      type: 'pie',
      radius: '65%',
      label: { formatter: '{b}: {c}' },
      data: exceptionData.value,
    },
  ],
}))

const groupOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 50, right: 20, top: 20, bottom: 60 },
  xAxis: {
    type: 'category',
    data: groupData.value.map((item) => item.name),
    axisLabel: { interval: 0, rotate: 30, fontSize: 11 },
  },
  yAxis: { type: 'value', name: '人数' },
  series: [
    {
      type: 'bar',
      data: groupData.value.map((item) => item.value),
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#67e8f9' },
            { offset: 1, color: '#06b6d4' },
          ],
        },
      },
      barMaxWidth: 36,
    },
  ],
}))

function tally(values: string[]): Array<{ name: string; value: number }> {
  const counter = new Map<string, number>()
  for (const value of values) {
    const key = value || '未分类'
    counter.set(key, (counter.get(key) ?? 0) + 1)
  }
  return Array.from(counter, ([name, value]) => ({ name, value }))
}

async function loadDashboard() {
  loading.value = true
  try {
    const [dashboard, tasks, exceptions, groups] = await Promise.all([
      getDashboard(),
      getTasks({ page: 1, pageSize: 100 }),
      getExceptions({ page: 1, pageSize: 100 }),
      getGroups({ page: 1, pageSize: 100 }),
    ])
    stats.value = dashboard
    taskStatusData.value = tally(tasks.items.map((task) => String(task.status)))
    completionData.value = tasks.items.slice(0, 10).map((task) => ({
      name: task.title,
      value: Number(String(task.completionRate).replace('%', '')) || 0,
    }))
    exceptionData.value = tally(
      exceptions.items.map((item) => String(item.exceptionType)),
    )
    groupData.value = groups.items.map((group) => ({
      name: group.name,
      value: Number(group.studentCount) || 0,
    }))
    logInfo('管理端工作台加载成功', stats.value)
  } catch (error) {
    stats.value = emptyStats()
    taskStatusData.value = []
    completionData.value = []
    exceptionData.value = []
    groupData.value = []
    showError(error, '工作台数据加载失败')
  } finally {
    loading.value = false
  }
}

function openDataScreen() {
  const route = router.resolve({ name: 'dataScreen' })
  window.open(route.href, '_blank')
}

onMounted(loadDashboard)
</script>

<template>
  <section class="admin-page">
    <div class="dashboard-hero">
      <div class="dashboard-hero__content">
        <div class="dashboard-hero__copy">
          <h2>
            让考勤管理更智能，助力校园管理
            <span class="highlight">高效成长</span>
          </h2>
          <p>集中查看考勤推进、异常分布与组织治理状态，用数据驱动每一次管理决策。</p>
          <div class="dashboard-hero__tags">
            <span v-for="tag in heroTags" :key="tag.label" class="dashboard-hero__tag">
              <i :style="{ background: tag.color }"></i>
              {{ tag.label }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="page-header">
      <div>
        <h1>数据工作台</h1>
        <p>实时掌握平台运行态势与关键指标变化。</p>
      </div>
      <div class="header-actions">
        <el-button @click="openDataScreen">数据大屏</el-button>
        <el-button type="primary" :loading="loading" @click="loadDashboard">刷新概览</el-button>
      </div>
    </div>

    <div class="stat-grid">
      <article
        v-for="item in statCards"
        :key="item.label"
        class="stat-card--rich"
        :class="item.tone"
      >
        <p class="stat-card__label">{{ item.label }}</p>
        <div class="stat-card__value">
          <strong>{{ item.value }}</strong>
          <span>{{ item.suffix }}</span>
        </div>
      </article>
    </div>

    <div class="chart-grid">
      <el-card header="任务状态分布">
        <el-empty v-if="taskStatusData.length === 0" description="暂无任务数据" :image-size="72" />
        <v-chart v-else class="chart" :option="taskStatusOption" autoresize />
      </el-card>
      <el-card header="异常类型分布">
        <el-empty v-if="exceptionData.length === 0" description="暂无异常数据" :image-size="72" />
        <v-chart v-else class="chart" :option="exceptionOption" autoresize />
      </el-card>
      <el-card header="任务完成率 Top 10">
        <el-empty v-if="completionData.length === 0" description="暂无任务数据" :image-size="72" />
        <v-chart v-else class="chart" :option="completionOption" autoresize />
      </el-card>
      <el-card header="各班级学生人数">
        <el-empty v-if="groupData.length === 0" description="暂无班级数据" :image-size="72" />
        <v-chart v-else class="chart" :option="groupOption" autoresize />
      </el-card>
    </div>
  </section>
</template>

<style scoped lang="scss">
.header-actions {
  display: flex;
  gap: 12px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.chart {
  height: 320px;
  width: 100%;
}

@media (max-width: 1100px) {
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
