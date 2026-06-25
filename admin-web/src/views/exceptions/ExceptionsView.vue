<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import { getExceptions, type ExceptionRow } from '../../api/admin'
import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'
import { logInfo, showError } from '../../utils/feedback'

const filters = reactive({
  exceptionType: '',
  status: '',
})

const columns: DataColumn<ExceptionRow>[] = [
  { key: 'student', label: '学生', minWidth: 120 },
  { key: 'exceptionType', label: '异常类型', minWidth: 150 },
  { key: 'status', label: '处理状态', minWidth: 120 },
  { key: 'reviewStatus', label: '审核状态', minWidth: 150 },
]

const rows = ref<ExceptionRow[]>([])
const loading = ref(false)

const filteredRows = computed(() =>
  rows.value.filter((row) => {
    const typeMatched = !filters.exceptionType || row.exceptionType === filters.exceptionType
    const statusMatched = !filters.status || row.status === filters.status
    return typeMatched && statusMatched
  }),
)

const exceptionOptions = computed(() => [...new Set(rows.value.map((row) => row.exceptionType).filter(Boolean))])
const statusOptions = computed(() => [...new Set(rows.value.map((row) => row.status).filter(Boolean))])

async function loadExceptions() {
  loading.value = true
  try {
    rows.value = (await getExceptions()).items
    logInfo('异常与申诉列表加载成功', { count: rows.value.length })
  } catch (error) {
    rows.value = []
    showError(error, '异常与申诉列表加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadExceptions)
</script>

<template>
  <section class="admin-page">
    <div class="page-header">
      <div>
        <h1>异常与申诉</h1>
        <p>筛选异常类型与处理状态，快速跟踪复核进展。</p>
      </div>
    </div>

    <el-card>
      <div class="toolbar-grid">
        <el-select v-model="filters.exceptionType" placeholder="异常类型" clearable>
          <el-option v-for="type in exceptionOptions" :key="type" :label="type" :value="type" />
        </el-select>
        <el-select v-model="filters.status" placeholder="处理状态" clearable>
          <el-option v-for="status in statusOptions" :key="status" :label="status" :value="status" />
        </el-select>
      </div>
    </el-card>

    <el-card>
      <DataTable :columns="columns" :rows="filteredRows" :loading="loading">
        <template #reviewStatus="{ row }">
          <el-tag :type="row.reviewStatus.includes('待') ? 'warning' : 'success'">
            {{ row.reviewStatus }}
          </el-tag>
        </template>
      </DataTable>
    </el-card>
  </section>
</template>
