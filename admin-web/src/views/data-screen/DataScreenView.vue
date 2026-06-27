<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
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

import { getDashboard, getExceptions, getGroups, getTasks } from '../../api/admin'

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

function goBack() {
  router.push({ name: 'dashboard' })
}

const now = ref(new Date())
let timer: ReturnType<typeof setInterval> | null = null
let refreshTimer: ReturnType<typeof setInterval> | null = null

const kpis = ref([
  { label: '学生总数', value: 0, suffix: '人' },
  { label: '任务总数', value: 0, suffix: '项' },
  { label: '平均完成率', value: 0, suffix: '%' },
  { label: '异常数量', value: 0, suffix: '条' },
])

const taskStatusData = ref<Array<{ name: string; value: number }>>([])
const completionData = ref<Array<{ name: string; value: number }>>([])
const exceptionData = ref<Array<{ name: string; value: number }>>([])
const groupData = ref<Array<{ name: string; value: number }>>([])

const palette = ['#36cfc9', '#1677ff', '#9254de', '#ffa940', '#ff7875', '#73d13d']
const axisStyle = {
  axisLine: { lineStyle: { color: 'rgba(255,255,255,0.35)' } },
  axisLabel: { color: '#cfe3ff' },
  splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
}

const clock = computed(() =>
  now.value.toLocaleString('zh-CN', { hour12: false }),
)

const taskStatusOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, textStyle: { color: '#cfe3ff' } },
  color: palette,
  series: [
    {
      type: 'pie',
      radius: ['42%', '68%'],
      itemStyle: { borderColor: '#0b2545', borderWidth: 2 },
      label: { color: '#fff', formatter: '{b}\n{c}' },
      data: taskStatusData.value,
    },
  ],
}))

const exceptionOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, textStyle: { color: '#cfe3ff' } },
  color: palette,
  series: [
    {
      type: 'pie',
      roseType: 'radius',
      radius: ['25%', '65%'],
      label: { color: '#fff' },
      data: exceptionData.value,
    },
  ],
}))

const completionOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 50, right: 20, top: 24, bottom: 70 },
  xAxis: {
    type: 'category',
    data: completionData.value.map((item) => item.name),
    ...axisStyle,
    axisLabel: { ...axisStyle.axisLabel, interval: 0, rotate: 30, fontSize: 11 },
  },
  yAxis: { type: 'value', max: 100, ...axisStyle },
  series: [
    {
      type: 'bar',
      data: completionData.value.map((item) => item.value),
      itemStyle: { color: '#36cfc9', borderRadius: [6, 6, 0, 0] },
      barMaxWidth: 30,
    },
  ],
}))

const groupOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 50, right: 20, top: 24, bottom: 70 },
  xAxis: {
    type: 'category',
    data: groupData.value.map((item) => item.name),
    ...axisStyle,
    axisLabel: { ...axisStyle.axisLabel, interval: 0, rotate: 30, fontSize: 11 },
  },
  yAxis: { type: 'value', ...axisStyle },
  series: [
    {
      type: 'bar',
      data: groupData.value.map((item) => item.value),
      itemStyle: { color: '#1677ff', borderRadius: [6, 6, 0, 0] },
      barMaxWidth: 30,
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

async function loadData() {
  try {
    const [dashboard, tasks, exceptions, groups] = await Promise.all([
      getDashboard(),
      getTasks({ page: 1, pageSize: 100 }),
      getExceptions({ page: 1, pageSize: 100 }),
      getGroups({ page: 1, pageSize: 100 }),
    ])
    kpis.value = [
      { label: '学生总数', value: dashboard.studentCount, suffix: '人' },
      { label: '任务总数', value: dashboard.taskCount, suffix: '项' },
      { label: '平均完成率', value: dashboard.completionRate, suffix: '%' },
      { label: '异常数量', value: dashboard.exceptionCount, suffix: '条' },
    ]
    taskStatusData.value = tally(tasks.items.map((task) => String(task.status)))
    completionData.value = tasks.items.slice(0, 10).map((task) => ({
      name: task.title,
      value: Number(String(task.completionRate).replace('%', '')) || 0,
    }))
    exceptionData.value = tally(exceptions.items.map((item) => String(item.exceptionType)))
    groupData.value = groups.items.map((group) => ({
      name: group.name,
      value: Number(group.studentCount) || 0,
    }))
  } catch {
    // 大屏静默失败，保留上一次数据
  }
}

onMounted(() => {
  loadData()
  timer = setInterval(() => (now.value = new Date()), 1000)
  refreshTimer = setInterval(loadData, 30000)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<template>
  <div class="screen">
    <header class="screen__header">
      <span class="screen__brand">考勤助手 · 高校学生考勤数据大屏</span>
      <div class="screen__right">
        <span class="screen__clock">{{ clock }}</span>
        <button class="screen__back" @click="goBack">返回控制台</button>
      </div>
    </header>

    <div class="kpi-row">
      <div v-for="item in kpis" :key="item.label" class="kpi-card">
        <span class="kpi-value">{{ item.value }}<i>{{ item.suffix }}</i></span>
        <span class="kpi-label">{{ item.label }}</span>
      </div>
    </div>

    <div class="grid">
      <div class="panel">
        <h3>任务状态分布</h3>
        <v-chart class="chart" :option="taskStatusOption" autoresize />
      </div>
      <div class="panel">
        <h3>任务完成率 Top 10</h3>
        <v-chart class="chart" :option="completionOption" autoresize />
      </div>
      <div class="panel">
        <h3>异常类型分布</h3>
        <v-chart class="chart" :option="exceptionOption" autoresize />
      </div>
      <div class="panel">
        <h3>各班级学生人数</h3>
        <v-chart class="chart" :option="groupOption" autoresize />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.screen {
  min-height: 100vh;
  padding: 24px 32px 32px;
  background: radial-gradient(circle at top, #103c75 0%, #06182f 60%, #030c1a 100%);
  color: #eaf3ff;
}

.screen__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(120, 180, 255, 0.25);
}

.screen__brand {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: 4px;
  background: linear-gradient(90deg, #6cd3ff, #b18cff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.screen__right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.screen__clock {
  font-size: 16px;
  color: #9ec3ff;
  font-variant-numeric: tabular-nums;
}

.screen__back {
  padding: 6px 16px;
  border-radius: 999px;
  border: 1px solid rgba(120, 180, 255, 0.45);
  background: rgba(26, 78, 142, 0.4);
  color: #cfe3ff;
  font-size: 13px;
  cursor: pointer;
}

.screen__back:hover {
  background: rgba(40, 120, 220, 0.5);
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin: 22px 0;
}

.kpi-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px 24px;
  border-radius: 14px;
  background: rgba(26, 78, 142, 0.35);
  border: 1px solid rgba(120, 180, 255, 0.25);
  box-shadow: inset 0 0 24px rgba(60, 140, 255, 0.12);
}

.kpi-value {
  font-size: 38px;
  font-weight: 800;
  color: #5fe0ff;

  i {
    margin-left: 6px;
    font-size: 16px;
    font-style: normal;
    color: #9ec3ff;
  }
}

.kpi-label {
  font-size: 14px;
  color: #9ec3ff;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.panel {
  padding: 16px 18px;
  border-radius: 14px;
  background: rgba(13, 47, 92, 0.45);
  border: 1px solid rgba(120, 180, 255, 0.2);

  h3 {
    margin: 0 0 10px;
    font-size: 16px;
    color: #bcdcff;
  }
}

.chart {
  height: 300px;
  width: 100%;
}

@media (max-width: 1100px) {
  .kpi-row,
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
