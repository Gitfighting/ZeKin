<script setup lang="ts">
import {
  Calendar,
  DataAnalysis,
  DocumentChecked,
  Location,
  PieChart,
  UserFilled,
  WarningFilled,
} from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { BarChart, LineChart, PieChart as EPieChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { computed, onMounted, ref, watch } from 'vue'
import VChart from 'vue-echarts'

import {
  getScenarioAnalytics,
  type AnalyticsRangeKey,
  type ScenarioAnalyticsStats,
  type ScenarioKey,
} from '../../api/admin'
import { logInfo, showError } from '../../utils/feedback'

use([
  CanvasRenderer,
  EPieChart,
  BarChart,
  LineChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const SCENARIO_TABS: { key: ScenarioKey; label: string; hint: string }[] = [
  { key: 'all', label: '综合洞察', hint: '全院四类场景汇总' },
  { key: 'classroom', label: '课堂签到', hint: '默认位置+人脸' },
  { key: 'dorm', label: '查寝签到', hint: '宿舍围栏定位' },
  { key: 'internship', label: '实习签到', hint: '人脸+位置+附件' },
  { key: 'custom', label: '自定义', hint: '教师自建规则' },
]

const RANGE_OPTIONS: { key: AnalyticsRangeKey; label: string }[] = [
  { key: 'today', label: '今日' },
  { key: 'week', label: '本周' },
  { key: 'month', label: '本月' },
  { key: 'semester', label: '本学期' },
]

const palette = ['#1677ff', '#21bf73', '#ff8a16', '#7c4dff', '#06b6d4', '#ec4899']

const emptyStats = (): ScenarioAnalyticsStats => ({
  scenario: 'all',
  scenarioLabel: '综合洞察',
  range: 'week',
  filters: { college: '', major: '', className: '', grade: '' },
  filterOptions: { colleges: [], majors: [], classes: [], grades: [] },
  summary: {
    expectedCount: 0,
    checkedCount: 0,
    completionRate: 0,
    exceptionCount: 0,
    exceptionRate: 0,
    pendingAppealCount: 0,
    taskCount: 0,
    coveredStudentCount: 0,
    faceRegistrationRate: 0,
    locationPassRate: 0,
    facePassRate: 0,
  },
  trend: [],
  majorRates: [],
  classRates: [],
  exceptionTypes: [],
  verificationBreakdown: [],
  checkinTimeDistribution: [],
  classExceptionRanking: [],
  riskStudents: [],
  faceRegistrationByMajor: [],
})

const analytics = ref<ScenarioAnalyticsStats>(emptyStats())
const activeScenario = ref<ScenarioKey>('classroom')
const activeRange = ref<AnalyticsRangeKey>('week')
const selectedCollege = ref('')
const selectedMajor = ref('')
const selectedClass = ref('')
const selectedGrade = ref('')
const loading = ref(false)

const showFaceMetrics = computed(
  () => activeScenario.value === 'classroom' || activeScenario.value === 'all',
)

const metricCards = computed(() => {
  const summary = analytics.value.summary
  const cards = [
    {
      label: '应到人次',
      value: formatNumber(summary.expectedCount),
      unit: '次',
      tone: 'blue',
      icon: Calendar,
    },
    {
      label: '实到人次',
      value: formatNumber(summary.checkedCount),
      unit: '次',
      tone: 'green',
      icon: UserFilled,
    },
    {
      label: '完成率',
      value: String(summary.completionRate),
      unit: '%',
      tone: 'orange',
      icon: PieChart,
    },
    {
      label: '异常记录',
      value: formatNumber(summary.exceptionCount),
      unit: '条',
      tone: 'red',
      icon: WarningFilled,
    },
    {
      label: '待处理申诉',
      value: formatNumber(summary.pendingAppealCount),
      unit: '条',
      tone: 'purple',
      icon: DocumentChecked,
    },
  ]
  if (showFaceMetrics.value) {
    cards.push({
      label: '人脸录入率',
      value: String(summary.faceRegistrationRate),
      unit: '%',
      tone: 'blue',
      icon: DataAnalysis,
    })
    cards.push({
      label: '位置通过率',
      value: String(summary.locationPassRate),
      unit: '%',
      tone: 'green',
      icon: Location,
    })
    cards.push({
      label: '人脸通过率',
      value: String(summary.facePassRate),
      unit: '%',
      tone: 'orange',
      icon: UserFilled,
    })
  }
  return cards
})

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { top: 0 },
  grid: { left: 48, right: 48, top: 40, bottom: 28 },
  xAxis: {
    type: 'category',
    data: analytics.value.trend.map((item) => item.label),
  },
  yAxis: [
    { type: 'value', name: '人次' },
    { type: 'value', name: '完成率%', max: 100 },
  ],
  color: ['#1677ff', '#21bf73', '#ff8a16'],
  series: [
    {
      name: '应到',
      type: 'line',
      smooth: true,
      data: analytics.value.trend.map((item) => item.expected),
    },
    {
      name: '实到',
      type: 'line',
      smooth: true,
      data: analytics.value.trend.map((item) => item.checked),
    },
    {
      name: '完成率',
      type: 'line',
      smooth: true,
      yAxisIndex: 1,
      data: analytics.value.trend.map((item) => item.completionRate),
    },
  ],
}))

const majorOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 48, right: 16, top: 20, bottom: 56 },
  xAxis: {
    type: 'category',
    data: analytics.value.majorRates.map((item) => item.name),
    axisLabel: { interval: 0, rotate: 24, fontSize: 11 },
  },
  yAxis: { type: 'value', max: 100, name: '完成率%' },
  series: [
    {
      type: 'bar',
      data: analytics.value.majorRates.map((item) => item.completionRate),
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
      barMaxWidth: 40,
    },
  ],
}))

const classOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 48, right: 16, top: 20, bottom: 56 },
  xAxis: {
    type: 'category',
    data: analytics.value.classRates.map((item) => item.name),
    axisLabel: { interval: 0, rotate: 24, fontSize: 11 },
  },
  yAxis: { type: 'value', max: 100, name: '完成率%' },
  series: [
    {
      type: 'bar',
      data: analytics.value.classRates.map((item) => item.completionRate),
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#86efac' },
            { offset: 1, color: '#21bf73' },
          ],
        },
      },
      barMaxWidth: 36,
    },
  ],
}))

const exceptionOption = computed(() => ({
  tooltip: { trigger: 'item' },
  color: palette,
  series: [
    {
      type: 'pie',
      radius: ['42%', '68%'],
      data: analytics.value.exceptionTypes.map((item) => ({
        name: item.label,
        value: item.value,
      })),
      label: { formatter: '{b}\n{d}%' },
    },
  ],
}))

const verificationOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { top: 0 },
  grid: { left: 48, right: 16, top: 36, bottom: 28 },
  xAxis: {
    type: 'category',
    data: analytics.value.verificationBreakdown.map((item) => item.label),
  },
  yAxis: { type: 'value', name: '次数' },
  color: ['#21bf73', '#ff6874'],
  series: [
    {
      name: '通过',
      type: 'bar',
      stack: 'total',
      data: analytics.value.verificationBreakdown.map((item) => item.passed),
      barMaxWidth: 48,
    },
    {
      name: '失败',
      type: 'bar',
      stack: 'total',
      data: analytics.value.verificationBreakdown.map((item) => item.failed),
      barMaxWidth: 48,
    },
  ],
}))

const timeOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 48, right: 16, top: 20, bottom: 28 },
  xAxis: {
    type: 'category',
    data: analytics.value.checkinTimeDistribution.map((item) => item.label),
    axisLabel: { interval: 0, rotate: 30, fontSize: 10 },
  },
  yAxis: { type: 'value', name: '打卡次数' },
  series: [
    {
      type: 'bar',
      data: analytics.value.checkinTimeDistribution.map((item) => item.count),
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: '#7c4dff',
      },
      barMaxWidth: 28,
    },
  ],
}))

const faceRegistrationOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 48, right: 16, top: 20, bottom: 56 },
  xAxis: {
    type: 'category',
    data: analytics.value.faceRegistrationByMajor.map((item) => item.name),
    axisLabel: { interval: 0, rotate: 24, fontSize: 11 },
  },
  yAxis: { type: 'value', max: 100, name: '录入率%' },
  series: [
    {
      type: 'bar',
      data: analytics.value.faceRegistrationByMajor.map((item) => item.rate),
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: '#1677ff',
      },
      barMaxWidth: 40,
    },
  ],
}))

function formatNumber(value: number) {
  return new Intl.NumberFormat('zh-CN').format(value)
}

function riskLabel(level: string) {
  if (level === 'high') return '高风险'
  if (level === 'medium') return '中风险'
  return '低风险'
}

async function loadAnalytics() {
  loading.value = true
  try {
    analytics.value = await getScenarioAnalytics({
      scenario: activeScenario.value,
      range: activeRange.value,
      college: selectedCollege.value || undefined,
      major: selectedMajor.value || undefined,
      className: selectedClass.value || undefined,
      grade: selectedGrade.value || undefined,
    })
    logInfo('场景化统计分析加载成功', {
      scenario: analytics.value.scenario,
      range: analytics.value.range,
    })
  } catch (error) {
    analytics.value = emptyStats()
    showError(error, '场景化统计分析加载失败')
  } finally {
    loading.value = false
  }
}

watch([activeScenario, activeRange, selectedCollege, selectedMajor, selectedClass, selectedGrade], loadAnalytics)

onMounted(loadAnalytics)
</script>

<template>
  <section class="analytics-page" :aria-busy="loading">
    <header class="page-heading">
      <div>
        <h1>场景化统计分析</h1>
        <p>面向计算机学院 · 按课堂 / 查寝 / 实习 / 自定义场景挖掘考勤数据</p>
      </div>
      <div class="range-tabs" aria-label="统计周期">
        <button
          v-for="item in RANGE_OPTIONS"
          :key="item.key"
          :class="{ active: activeRange === item.key }"
          type="button"
          @click="activeRange = item.key"
        >
          {{ item.label }}
        </button>
      </div>
    </header>

    <section class="filter-bar">
      <el-select v-model="selectedCollege" clearable placeholder="学院" style="width: 180px">
        <el-option
          v-for="item in analytics.filterOptions.colleges"
          :key="item"
          :label="item"
          :value="item === '未设置学院' ? '' : item"
        />
      </el-select>
      <el-select v-model="selectedMajor" clearable placeholder="专业" style="width: 180px">
        <el-option
          v-for="item in analytics.filterOptions.majors"
          :key="item"
          :label="item"
          :value="item === '未设置专业' ? '' : item"
        />
      </el-select>
      <el-select v-model="selectedClass" clearable placeholder="班级" style="width: 180px">
        <el-option
          v-for="item in analytics.filterOptions.classes"
          :key="item"
          :label="item"
          :value="item === '未分班' ? '' : item"
        />
      </el-select>
      <el-select v-model="selectedGrade" clearable placeholder="年级" style="width: 140px">
        <el-option
          v-for="item in analytics.filterOptions.grades"
          :key="item"
          :label="item"
          :value="item === '未设置年级' ? '' : item"
        />
      </el-select>
    </section>

    <section class="scenario-tabs" aria-label="签到场景">
      <button
        v-for="tab in SCENARIO_TABS"
        :key="tab.key"
        class="scenario-tab"
        :class="{ active: activeScenario === tab.key }"
        type="button"
        @click="activeScenario = tab.key"
      >
        <strong>{{ tab.label }}</strong>
        <span>{{ tab.hint }}</span>
      </button>
    </section>

    <section class="metric-grid" :class="{ compact: !showFaceMetrics }">
      <article v-for="card in metricCards" :key="card.label" class="metric-card">
        <div :class="['metric-icon', card.tone]">
          <el-icon><component :is="card.icon" /></el-icon>
        </div>
        <div class="metric-copy">
          <span>{{ card.label }}</span>
          <strong>{{ card.value }} <small>{{ card.unit }}</small></strong>
          <p v-if="card.label === '完成率'">覆盖 {{ analytics.summary.taskCount }} 个任务</p>
          <p v-else-if="card.label === '应到人次'">在籍 {{ analytics.summary.coveredStudentCount }} 人</p>
        </div>
      </article>
    </section>

    <section class="chart-grid">
      <article class="panel">
        <header class="panel-header">
          <h2>考勤趋势</h2>
        </header>
        <VChart
          v-if="analytics.trend.length"
          class="chart"
          :option="trendOption"
          autoresize
        />
        <p v-else class="empty-panel">当前筛选条件下暂无趋势数据</p>
      </article>

      <article class="panel">
        <header class="panel-header">
          <h2>专业完成率对比</h2>
        </header>
        <VChart
          v-if="analytics.majorRates.length"
          class="chart"
          :option="majorOption"
          autoresize
        />
        <p v-else class="empty-panel">暂无专业维度数据</p>
      </article>
    </section>

    <section class="chart-grid">
      <article class="panel">
        <header class="panel-header">
          <h2>班级完成率对比</h2>
        </header>
        <VChart
          v-if="analytics.classRates.length"
          class="chart chart--short"
          :option="classOption"
          autoresize
        />
        <p v-else class="empty-panel">暂无班级维度数据</p>
      </article>

      <article class="panel">
        <header class="panel-header">
          <h2>异常类型分布</h2>
        </header>
        <VChart
          v-if="analytics.exceptionTypes.length"
          class="chart chart--short"
          :option="exceptionOption"
          autoresize
        />
        <p v-else class="empty-panel">暂无异常类型数据</p>
      </article>
    </section>

    <section class="chart-grid">
      <article class="panel">
        <header class="panel-header">
          <h2>校验方式通过/失败分解</h2>
        </header>
        <VChart
          v-if="analytics.verificationBreakdown.length"
          class="chart chart--short"
          :option="verificationOption"
          autoresize
        />
        <p v-else class="empty-panel">暂无校验分解数据</p>
      </article>

      <article class="panel">
        <header class="panel-header">
          <h2>打卡时段分布</h2>
        </header>
        <VChart
          v-if="analytics.checkinTimeDistribution.length"
          class="chart chart--short"
          :option="timeOption"
          autoresize
        />
        <p v-else class="empty-panel">暂无打卡时段数据</p>
      </article>
    </section>

    <section v-if="showFaceMetrics" class="chart-grid chart-grid--single">
      <article class="panel">
        <header class="panel-header">
          <h2>各专业人脸录入率</h2>
          <span class="panel-note">课堂签到默认需位置+人脸，录入率是前置指标</span>
        </header>
        <VChart
          v-if="analytics.faceRegistrationByMajor.length"
          class="chart chart--short"
          :option="faceRegistrationOption"
          autoresize
        />
        <p v-else class="empty-panel">暂无人脸录入数据</p>
      </article>
    </section>

    <section class="bottom-grid">
      <article class="panel">
        <header class="panel-header compact">
          <h2>班级异常排行</h2>
        </header>
        <table v-if="analytics.classExceptionRanking.length" class="rank-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>班级</th>
              <th>异常人次</th>
              <th>涉及学生</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in analytics.classExceptionRanking" :key="row.className">
              <td><span :class="['rank-badge', { top: index < 3 }]">{{ index + 1 }}</span></td>
              <td>{{ row.className }}</td>
              <td>{{ row.exceptionCount }}</td>
              <td class="danger">{{ row.exceptionStudentCount }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty-panel">暂无班级异常排行</p>
      </article>

      <article class="panel panel--wide">
        <header class="panel-header compact">
          <h2>风险学生预警</h2>
          <span class="panel-note">缺勤与异常叠加评分，Top 20</span>
        </header>
        <table v-if="analytics.riskStudents.length" class="rank-table">
          <thead>
            <tr>
              <th>学号</th>
              <th>姓名</th>
              <th>专业</th>
              <th>班级</th>
              <th>缺勤</th>
              <th>异常</th>
              <th>风险</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in analytics.riskStudents" :key="row.studentNo">
              <td>{{ row.studentNo }}</td>
              <td>{{ row.name }}</td>
              <td>{{ row.major }}</td>
              <td>{{ row.className }}</td>
              <td>{{ row.missingCount }}</td>
              <td>{{ row.exceptionCount }}</td>
              <td>
                <span :class="['risk-tag', row.riskLevel]">{{ riskLabel(row.riskLevel) }}</span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty-panel">当前筛选条件下暂无风险学生</p>
      </article>
    </section>
  </section>
</template>

<style scoped lang="scss">
.analytics-page {
  display: grid;
  gap: 14px;
  color: #17233d;
}

.page-heading,
.panel-header,
.filter-bar,
.scenario-tabs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.page-heading {
  align-items: end;
  padding: 8px 12px 0;
}

.page-heading h1,
.page-heading p,
.panel-header h2 {
  margin: 0;
}

.page-heading h1 {
  color: #061947;
  font-size: 30px;
  font-weight: 900;
}

.page-heading p {
  margin-top: 10px;
  color: #5a6b88;
  font-size: 14px;
  font-weight: 700;
}

.range-tabs {
  display: grid;
  grid-template-columns: repeat(4, 88px);
  overflow: hidden;
  border: 1px solid #d8e3f1;
  border-radius: 7px;
}

.range-tabs button {
  height: 38px;
  color: #1f2a44;
  background: rgba(255, 255, 255, 0.85);
  border: 0;
  border-left: 1px solid #d8e3f1;
  cursor: pointer;
  font-weight: 800;
}

.range-tabs button:first-child {
  border-left: 0;
}

.range-tabs button.active {
  color: #fff;
  background: linear-gradient(135deg, #2b86ff, #0d67f6);
}

.filter-bar {
  padding: 0 12px;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.scenario-tabs {
  padding: 0 12px;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.scenario-tab {
  display: grid;
  gap: 4px;
  min-width: 140px;
  padding: 12px 16px;
  text-align: left;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #dfe8f6;
  border-radius: 10px;
  cursor: pointer;
}

.scenario-tab strong {
  color: #101828;
  font-size: 15px;
}

.scenario-tab span {
  color: #60708c;
  font-size: 12px;
}

.scenario-tab.active {
  border-color: #1677ff;
  background: linear-gradient(180deg, #f5f9ff 0%, #ffffff 100%);
  box-shadow: 0 8px 20px rgba(22, 119, 255, 0.12);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 0 12px;
}

.metric-grid.compact {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.metric-card,
.panel {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #dfe8f6;
  border-radius: 10px;
  box-shadow: 0 12px 28px rgba(33, 93, 172, 0.08);
}

.metric-card {
  display: grid;
  grid-template-columns: 58px 1fr;
  gap: 18px;
  align-items: center;
  min-height: 110px;
  padding: 18px 20px;
}

.metric-icon {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  color: #fff;
  border-radius: 50%;
}

.metric-icon.blue { background: linear-gradient(135deg, #379aff, #1169f3); }
.metric-icon.green { background: linear-gradient(135deg, #3bd984, #13b96c); }
.metric-icon.orange { background: linear-gradient(135deg, #ffb03a, #ff8917); }
.metric-icon.red { background: linear-gradient(135deg, #ff6874, #ff3345); }
.metric-icon.purple { background: linear-gradient(135deg, #9168ff, #7047e8); }

.metric-copy {
  display: grid;
  gap: 6px;
}

.metric-copy span {
  color: #52627f;
  font-size: 14px;
  font-weight: 800;
}

.metric-copy strong {
  color: #101828;
  font-size: 28px;
}

.metric-copy p {
  margin: 0;
  color: #60708c;
  font-size: 12px;
}

.chart-grid,
.bottom-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 0 12px;
}

.chart-grid--single {
  grid-template-columns: 1fr;
}

.panel {
  padding: 18px 20px 12px;
}

.panel-header.compact {
  margin-bottom: 12px;
}

.panel-header h2 {
  color: #061947;
  font-size: 18px;
  font-weight: 800;
}

.panel-note {
  color: #60708c;
  font-size: 12px;
}

.chart {
  width: 100%;
  height: 320px;
}

.chart--short {
  height: 280px;
}

.empty-panel {
  margin: 0;
  padding: 48px 16px;
  color: #60708c;
  text-align: center;
}

.bottom-grid {
  grid-template-columns: 0.9fr 1.4fr;
}

.rank-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.rank-table th,
.rank-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #edf2f9;
  text-align: left;
}

.rank-badge {
  display: inline-grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #edf2f9;
  font-weight: 800;
}

.rank-badge.top {
  color: #fff;
  background: #1677ff;
}

.danger {
  color: #ff3345;
  font-weight: 700;
}

.risk-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.risk-tag.high {
  color: #ff3345;
  background: rgba(255, 51, 69, 0.12);
}

.risk-tag.medium {
  color: #ff8917;
  background: rgba(255, 137, 23, 0.12);
}

.risk-tag.low {
  color: #1677ff;
  background: rgba(22, 119, 255, 0.12);
}

@media (max-width: 1280px) {
  .metric-grid,
  .metric-grid.compact,
  .chart-grid,
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}
</style>
