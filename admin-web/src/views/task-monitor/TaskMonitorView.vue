<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import { getTasks, type TaskRow } from '../../api/admin'
import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'
import { logInfo, showError } from '../../utils/feedback'

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

const rows = ref<TaskRow[]>([])
const loading = ref(false)

const filteredRows = computed(() =>
  rows.value.filter((row) => {
    const teacherMatched = !filters.teacher || row.teacher.includes(filters.teacher)
    const typeMatched = !filters.type || row.type === filters.type
    const statusMatched = !filters.status || row.status === filters.status
    const dateMatched = !filters.date || row.date === filters.date
    return teacherMatched && typeMatched && statusMatched && dateMatched
  }),
)

const typeOptions = computed(() => [...new Set(rows.value.map((row) => row.type).filter(Boolean))])
const statusOptions = computed(() => [...new Set(rows.value.map((row) => row.status).filter(Boolean))])

async function loadTasks() {
  loading.value = true
  try {
    rows.value = (await getTasks()).items
    logInfo('任务监管列表加载成功', { count: rows.value.length })
  } catch (error) {
    rows.value = []
    showError(error, '任务监管列表加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadTasks)
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
          <el-option v-for="type in typeOptions" :key="type" :label="type" :value="type" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable>
          <el-option v-for="status in statusOptions" :key="status" :label="status" :value="status" />
        </el-select>
        <el-date-picker v-model="filters.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" />
      </div>
    </el-card>

    <el-card>
      <DataTable :columns="columns" :rows="filteredRows" :loading="loading">
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
