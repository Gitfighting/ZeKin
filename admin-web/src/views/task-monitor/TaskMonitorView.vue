<script setup lang="ts">
import { reactive } from 'vue'

import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'

interface TaskRow extends Record<string, unknown> {
  id: number
  teacher: string
  type: string
  status: string
  date: string
  completionRate: string
}

const filters = reactive({
  teacher: '',
  type: '',
  status: '',
  date: '',
})

const columns: DataColumn<TaskRow>[] = [
  { key: 'teacher', label: '负责教师', minWidth: 120 },
  { key: 'type', label: '任务类型', minWidth: 160 },
  { key: 'status', label: '状态', minWidth: 120 },
  { key: 'date', label: '日期', minWidth: 140 },
  { key: 'completionRate', label: '完成率', minWidth: 120 },
]

const rows: TaskRow[] = [
  { id: 1, teacher: '张明', type: '晨读签到', status: '进行中', date: '2026-06-24', completionRate: '93%' },
  { id: 2, teacher: '刘倩', type: '晚自习签到', status: '已结束', date: '2026-06-24', completionRate: '88%' },
]
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>任务监管</h1>
        <p>按教师、类型、状态与日期筛选任务执行情况。</p>
      </div>
    </div>

    <el-card>
      <div class="toolbar-grid">
        <el-input v-model="filters.teacher" placeholder="教师" />
        <el-select v-model="filters.type" placeholder="任务类型" clearable>
          <el-option label="晨读签到" value="晨读签到" />
          <el-option label="晚自习签到" value="晚自习签到" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable>
          <el-option label="进行中" value="进行中" />
          <el-option label="已结束" value="已结束" />
        </el-select>
        <el-date-picker v-model="filters.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" />
      </div>
    </el-card>

    <el-card>
      <DataTable :columns="columns" :rows="rows">
        <template #completionRate="{ row }">
          <div class="completion-cell">
            <el-progress :percentage="Number.parseInt(row.completionRate, 10)" :stroke-width="10" />
          </div>
        </template>
      </DataTable>
    </el-card>
  </section>
</template>

<style scoped lang="scss">
.completion-cell {
  min-width: 140px;
}
</style>
