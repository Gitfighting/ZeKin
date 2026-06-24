<script setup lang="ts">
import { reactive } from 'vue'

import DataTable, { type DataColumn } from '../../components/DataTable/DataTable.vue'

interface ExceptionRow extends Record<string, unknown> {
  id: number
  student: string
  exceptionType: string
  status: string
  reviewStatus: string
}

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

const rows: ExceptionRow[] = [
  { id: 1, student: '李晨', exceptionType: '定位缺失', status: '待复核', reviewStatus: '申诉待处理' },
  { id: 2, student: '王宁', exceptionType: '人脸不一致', status: '已驳回', reviewStatus: '已完成' },
]
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
          <el-option label="定位缺失" value="定位缺失" />
          <el-option label="人脸不一致" value="人脸不一致" />
        </el-select>
        <el-select v-model="filters.status" placeholder="处理状态" clearable>
          <el-option label="待复核" value="待复核" />
          <el-option label="已驳回" value="已驳回" />
        </el-select>
      </div>
    </el-card>

    <el-card>
      <DataTable :columns="columns" :rows="rows">
        <template #reviewStatus="{ row }">
          <el-tag :type="row.reviewStatus.includes('待') ? 'warning' : 'success'">
            {{ row.reviewStatus }}
          </el-tag>
        </template>
      </DataTable>
    </el-card>
  </section>
</template>
